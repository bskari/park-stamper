# -*- coding: utf-8 -*
from collections import namedtuple
from pyquery import PyQuery
import codecs
import csv
import logging
import math
import os
import re
import sys
import transaction
import unicodedata
import urllib

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from sqlalchemy import engine_from_config
from sqlalchemy.types import String

from parks.models import Base
from parks.models import DBSession
from parks.models import get_park_types
from parks.models import Park
from parks.models import Stamp
#from parks.models import StampCollection
from parks.models import StampLocation
from parks.models import StampToLocation
from parks.models import State
from parks.models import User
#from parks.models import UserEmail


logger = None


ParkTuple = namedtuple(
    'ParkTuple',
    ['name', 'state', 'latitude', 'longitude', 'agency', 'date']
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def remove_whitespace(s):
    s = re.sub(r'[ \t]+', ' ', s)
    return s


def remove_newlines(s):
    return re.sub(r'\n', ' ', s)


def levenshtein(s1, s2, cutoff=None):
    """Compute the Levenshtein edit distance between two strings. If the
    minimum distance will be greater than cutoff, then quit early and return
    at least cutoff.
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1, cutoff)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        current_row_min = 1000000000000000000
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            min_all_three = min(
                insertions,
                deletions,
                substitutions
            )
            current_row.append(min_all_three)
            current_row_min = min(current_row_min, min_all_three)

        if cutoff is not None and current_row_min > cutoff:
            return current_row_min
        previous_row = current_row

    return previous_row[-1]


def levenshtein_ratio(s1, s2, cutoff=None):
    max_len = max(len(s1), len(s2))
    if cutoff is not None:
        cutoff = int(math.ceil((1.0 - cutoff) * max_len) + .1)
    return 1.0 - (
        float(levenshtein(s1, s2, cutoff=cutoff))
        / max_len
    )


def save_page_to_file(pq, filename):
    """For debugging, so I'm not hitting Wikipedia constantly."""
    with open(filename, 'w') as f:
        f.write(str(pq))

    # Try to save the pickled file too
    pickle = None
    try:
        # Use Python's __import__ function to ignore Pyflakes warnings
        pickle = __import__('cpickle')
    except:
        try:
            # Fall back to slower, regular pickle
            pickle = __import__('pickle')
        except:
            pass
    if pickle is not None:
        pickle_filename = filename + '.pq.pickle'
        # Pickle sometimes blows up with stack overflow, so... do this in a
        # try/except block
        try:
            with open(pickle_filename, 'w') as f:
                pickle.dump(pq, f)
        except:
            pass


def load_page_from_file(filename):
    with open(filename, 'r') as f:
        pq = PyQuery(f.read())
    return pq


def load_page_from_pickle_file(filename):
    pickle_filename = filename + '.pq.pickle'
    # Only try to load the pickle if it's newer than the Wikipedia file
    import os
    wiki_stats = os.stats(filename)
    pickle_stats = os.stats(pickle_filename)
    if pickle_stats.st_ctime < wiki_stats.st_ctime:
        os.unlink(pickle_filename)
        pq = load_page_from_file(filename)
        save_page_to_file(pq, filename)
        return pq

    try:
        # Use Python's __import__ function to ignore Pyflakes warnings
        pickle = __import__('cpickle')
    except:
        # Fall back to slower, regular pickle
        pickle = __import__('pickle')

    with open(pickle_filename, 'r') as f:
        pq = pickle.load(f)
    return pq


def load_page_from_url(url):
    user_agent = 'Mozilla/5 (Solaris 10) Gecko'
    headers = {'User-Agent': user_agent}
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)

    pq = PyQuery(response.read())
    return pq


def load_wiki_page(wiki_page_name):
    """Returns the pq of the given Wiki page name. If the file has been
    accessed before and saved, it will use that. If not, it will access
    Wikipedia, download the page, save it for future calls, and then return
    the pq.
    """
    # Some wikis have / in them, which messes with Linux files
    escaped_wiki_page_name = wiki_page_name.replace('/', '-')
    filename = ''.join(
        (
            'parks/scripts/initialize_db/',
            escaped_wiki_page_name,
            '.html',
        )
    )

    try:
        pq = load_page_from_pickle_file(filename)
    except:
        try:
            pq = load_page_from_file(filename)
        except:
            pq = load_page_from_url(
                ''.join(
                    (
                        'http://en.wikipedia.org/wiki/',
                        wiki_page_name,
                    )
                )
            )
            save_page_to_file(pq, filename)
    return pq


def get_national_parks():
    """Loads the list of national parks from Wikipedia."""
    from dateutil.parser import parse
    pq = load_wiki_page('List_of_national_parks_of_the_United_States')
    wikitables = pq('table.wikitable')
    assert len(wikitables) == 1
    np_table = wikitables[0]
    trs = np_table.findall('tr')

    parks = []

    # Skip the header row
    for tr in trs[1:]:
        # The name is in a th tag
        name = tr.findall('th')[0].findall('a')[0].get('title')
        # Remove Unicode emdash
        name = name.replace('\u2013', '-')

        # The remaining columns are photo, location, date, area, description
        _, location_column, date_column, _, _ = tr.findall('td')

        # The location column has one or more states and a GPS coordinate
        state_name = location_column.findall('a')[0].text
        geo_text = PyQuery(location_column)('span.geo').text()
        latitude_text, longitude_text = geo_text.split(';')
        latitude = float(latitude_text)
        longitude = float(longitude_text)

        date = parse(PyQuery(date_column)('span')[-1].text, fuzzy=True)

        parks.append(
            ParkTuple(
                name=name,
                state=state_name,
                latitude=latitude,
                longitude=longitude,
                agency='NPS',
                date=date,
            )
        )

    return parks


def get_national_monuments():
    """Loads the list of national monuments from Wikipedia."""
    from dateutil.parser import parse
    pq = load_wiki_page('List_of_National_Monuments_of_the_United_States')
    wikitables = pq('table.wikitable')
    # There's an 'breakdown by agency' table and a list table
    assert len(wikitables) == 2
    nm_table = wikitables[1]
    trs = nm_table.findall('tr')

    monuments = []

    # Skip the header row
    for tr in trs[1:]:
        # The columns are name, photo, agency, location, date, description
        name_column, _, agency_column, location_column, date_column, _ = tr.findall('td')
        name = name_column.findall('a')[0].get('title')

        agency = agency_column.findall('a')[0].text

        # The location column has one or more states and a GPS coordinate
        state_name = location_column.findall('a')[0].text
        geo_text = PyQuery(location_column)('span.geo').text()
        try:
            latitude_text, longitude_text = geo_text.split(';')
            latitude = float(latitude_text)
            longitude = float(longitude_text)
        except:
            latitude = longitude = None
            logger.warning(
                'Skipping GPS for {monument}, no GPS found in "{geo_text}"'.format(
                    geo_text=geo_text,
                    monument=name,
                )
            )

        date = parse(PyQuery(date_column)('span')[-1].text, fuzzy=True)

        monuments.append(
            ParkTuple(
                name=name,
                state=state_name,
                latitude=latitude,
                longitude=longitude,
                agency=agency,
                date=date,
            )
        )

    return monuments


def get_national_lakeshores_and_seashores():
    """Loads the list of national lakeshores and seashores from Wikipedia."""
    from dateutil.parser import parse
    pq = load_wiki_page('List_of_United_States_national_lakeshores_and_seashores')
    wikitables = pq('table.wikitable')
    # There's a seashore table and a lakeshore table
    assert len(wikitables) == 2

    lakeshores = []
    seashores = []

    for table, list in zip(wikitables, (lakeshores, seashores)):
        trs = table.findall('tr')
        # Skip the header row
        for tr in trs[1:]:
            # The columns are name, photo, location, date, area, description
            name_column, _, location_column, date_column, _, _ = tr.findall('td')
            name = name_column.findall('a')[0].get('title')

            # The location column has one or more states and a GPS coordinate
            state_name = location_column.findall('a')[0].text
            geo_text = PyQuery(location_column)('span.geo').text()
            latitude_text, longitude_text = geo_text.split(';')
            latitude = float(latitude_text)
            longitude = float(longitude_text)

            date = parse(PyQuery(date_column)('span')[-1].text, fuzzy=True)

            list.append(
                ParkTuple(
                    name=name,
                    state=state_name,
                    latitude=latitude,
                    longitude=longitude,
                    agency='NPS',
                    date=date,
                )
            )

    return (lakeshores, seashores)


def get_national_grasslands():
    """Loads the list of national grasslands from Wikipedia."""
    pq = load_wiki_page('United_States_National_Grassland')
    tables = pq('table')
    # There's a list for TOC, a list of national grasslands, a list of prairie
    # reserves, a list of "See also" stuff, and a ton of other crap
    grassland_table = tables[1]

    grasslands = []

    for tr in grassland_table.findall('tr')[1:]: # Skip the header
        name = tr.findall('th')[0].text
        # Photo, Location, Administered by, Area, Description
        _, location_column, _, _, _ = tr.findall('td')
        # Some entries have multiple states, e.g. "Oklahoma, Texas"
        state = location_column.findall('a')[0].text
        geo_text = PyQuery(location_column)('span.geo').text()
        latitude_text, longitude_text = geo_text.split(';')
        latitude = float(latitude_text)
        longitude = float(longitude_text)

        grasslands.append(
            ParkTuple(
                name=name,
                state=state,
                agency='NFS',
                latitude=latitude,
                longitude=longitude,
                date=None,
            )
        )

    return grasslands


def get_national_marine_sanctuaries(state_names):
    """Loads the list of national marine sanctuaries from Wikipedia."""
    pq = load_wiki_page('United_States_National_Marine_Sanctuary')
    ul_lists = pq('ul')
    # There's a list of marine sanctuaries, and a ton of other crap
    sanctuary_list = ul_lists[0]

    sanctuaries = []

    for li in sanctuary_list.findall('li'):
        wiki_page_name = li.findall('a')[0].get('href').split('wiki/')[-1]
        pq = load_wiki_page(wiki_page_name)
        state = _get_state_from_wiki_pq(state_names, pq)
        latitude, longitude = _get_latitude_longitude_from_wiki_pq(pq)
        date = _get_date_from_wiki_pq(pq)

        name = li.findall('a')[0].text
        # Wikipedia includes some national monuments here too
        if 'National Marine Sanctuary' not in name:
            logger.warning(
                'Skipping {name} claiming to be a national marine sanctuary'.format(
                    name=name,
                )
            )
            continue

        ParkTuple(
            name=name,
            state=state,
            agency='NMSP', # National Marine Sanctuaries Program
            latitude=latitude,
            longitude=longitude,
            date=date,
        )

    return sanctuaries


def get_rivers():
    """Loads the list of national wild and scenic rivers from Wikipedia."""
    pq = load_wiki_page('List_of_National_Wild_and_Scenic_Rivers')
    ul_lists = pq('ul')
    # There's a TOC, list of bureaus and other crap
    state_river_lists = ul_lists[2:42]

    rivers = []
    river_names = set()

    for state_river_list in state_river_lists:
        # Some lists have sublists, so if there are no spans, just skip it
        try:
            state = PyQuery(state_river_list.getprevious())('span')[0].text
            # Some headings have things like "Georgia, North Carolina and South Carolina"
            if ',' in state:
                state = state.split(',')[0].strip()
            elif ' and' in state:
                state = state.split(' and')[0].strip()
        except IndexError:
            continue

        for li in state_river_list.findall('li'):
            # Some lists have sublists, so if there's no links, just skip it
            try:
                name = li.findall('a')[0].get('title')
            except IndexError:
                continue

            # Some rivers are listed in more than one state - skip duplicates
            if name in river_names:
                continue
            river_names.add(name)

            try:
                agency = PyQuery(li).text().split(',')[1].strip()
                # Remove crap like "BLM/NPS/USFS", "NPS/Florida"
                if '/' in agency:
                    agency = agency.split('/')[0].strip()
                # Some places have the state listed; ignore it
                if agency not in ('NPS', 'USFS', 'BLM', 'ACOE', 'USFWS'):
                    agency = None
            except IndexError:
                agency = None

            rivers.append(
                ParkTuple(
                    name=name,
                    state=state,
                    agency=agency,
                    latitude=None,
                    longitude=None,
                    date=None,
                )
            )

    return rivers


def get_national_trails():
    """Loads the list of national scenic trails and national historic trails
    from Wikipedia.
    """
    from dateutil.parser import parse
    national_trails = []

    for page in ('National_Historic_Trail', 'National_Scenic_Trail'):
        pq = load_wiki_page(page)
        wikitables = pq('table.wikitable')
        assert len(wikitables) == 1

        trs = wikitables('tr')

        # Skip the header row and total length row
        for tr in trs[1:-1]:
            # The columns are trail name, year established, length authorized
            name_column, date_column, _ = tr.findall('td')
            name = name_column.findall('a')[0].text

            date_text = date_column.text
            date = parse(date_text)

            national_trails.append(
                ParkTuple(
                    name=name,
                    latitude=None,
                    longitude=None,
                    state=None,
                    agency='NPS',
                    date=date,
                )
            )

    return national_trails


def get_national_memorials():
    """Loads the list of national memorials from Wikipedia."""
    from dateutil.parser import parse
    pq = load_wiki_page('List_of_National_Memorials_of_the_United_States')
    wikitables = pq('table.wikitable')
    # There's a national memorials table and an affiliated areas table
    assert len(wikitables) == 2

    memorials = []

    # TODO(bskari|2012-11-19) do something with areas?
    #for table, list in zip(wikitables, (memorials, areas)):
    for table, list in zip(wikitables[0:1], (memorials,)):
        trs = table.findall('tr')
        # Skip the header row
        for tr in trs[1:]:
            # The columns are name, photo, location, date, area, description
            name_column, _, location_column, date_column, _, _ = tr.findall('td')
            name = name_column.findall('a')[0].get('title')

            # The location column has the sate
            state_name = location_column.findall('a')[0].text

            date_text = date_column.findall('span')[-1].text
            if len(date_text) > 0:
                date = parse(date_text, fuzzy=True)
            else:
                date = None

            list.append(
                ParkTuple(
                    name=name,
                    latitude=None,
                    longitude=None,
                    state=state_name,
                    agency='NPS',
                    date=date,
                )
            )

    return memorials


def get_national_heritage_areas(state_names):
    """Loads the list of national heritage areas from Wikipedia."""
    pq = load_wiki_page('National_Heritage_Area')
    ul_lists = pq('ul')
    # There's a list of heritage areas, and other crap
    heritage_area_list = ul_lists[1]

    heritage_areas = []

    for li in heritage_area_list.findall('li'):
        name = li.findall('a')[0].text
        name = name.replace('&amp;', '&')

        # Some names leave off the NHA or whatever, so add them back in
        if 'National Heritage Area' not in name:
            if 'Canal' in name:
                name = name + ' National Heritage Area'
            elif 'River' in name and 'Corridor' not in name:
                name = name + ' Corridor'

        if 'Heritage' not in name and 'Corridor' not in name and 'District' not in name:
            logger.warning(
                'Incomplete name for heritage area: "{name}", skipping'.format(
                    name=name
                )
            )
            continue

        wiki_page_name = li.findall('a')[0].get('href').split('wiki/')[-1]
        pq = load_wiki_page(wiki_page_name)
        state = _get_state_from_wiki_pq(state_names, pq)

        heritage_areas.append(
            ParkTuple(
                name=name,
                state=state,
                agency='NHA',
                latitude=None,
                longitude=None,
                date=None,
            )
        )

    return heritage_areas


def get_nps_exclusive_areas(state_names):
    """Loads the list of national whatevers from Wikipedia. These are areas
    that are exclusively listed by the National Park Service and therefore
    the list on the areas in the US NPS wiki page is exhaustive.
    """
    pq = load_wiki_page(
        'List_of_areas_in_the_United_States_National_Park_System'
    )
    wikitables = pq('table.wikitable')
    def get_table(location_name):
        """Returns the only table that contains a given location name. We use
        this because the format of the Wiki page keeps moving around.
        """
        potential_tables = [
            table for table in wikitables
            if location_name in PyQuery(table).text()
        ]
        if len(potential_tables) != 1:
            logger.error(location_name + ' not found in any wiki table')
            assert False
        return potential_tables[0]

    # National preserves
    nps_table = get_table('Big Cypress National Preserve')
    nhps_table = get_table('Adams National Historical Park')
    nhs_table = get_table('Allegheny Portage Railroad National Historic Site')
    ihs_table = get_table('Saint Croix Island International Historic Site')
    nbps_table = get_table('Kennesaw Mountain National Battlefield Park')
    nmps_table = get_table('Gettysburg National Military Park')
    nbs_table = get_table('Antietam National Battlefield')
    nbss_table = get_table('Brices Cross Roads National Battlefield Site')
    nra_table = get_table('Amistad National Recreation Area')
    nrs_table = get_table('Alagnak Wild and Scenic River')
    npws_table = get_table('Blue Ridge Parkway')
    nhst_table = get_table('Ala Kahakai National Historic Trail')
    ncs_table = get_table('Arlington National Cemetery')
    other_table = get_table('Catoctin Mountain Park')

    areas = []

    for table in (
        nps_table,
        nhps_table,
        nhs_table,
        ihs_table,
        nbps_table,
        nmps_table,
        nbs_table,
        nbss_table,
        nra_table,
        nrs_table,
        npws_table,
        nhst_table,
        ncs_table,
        other_table,
    ):
        trs = table.findall('tr')
        # Skip the header row
        for tr in trs[1:]:
            # The columns are name, states
            name_column, state_column = tr.findall('td')
            name = name_column.findall('a')[0].text

            state_name = state_column.findall('a')[0].text

            wiki_page_name = name_column.findall('a')[0].get('href').split('wiki/')[-1]
            pq = load_wiki_page(wiki_page_name)
            latitude, longitude = _get_latitude_longitude_from_wiki_pq(pq)
            date = _get_date_from_wiki_pq(pq)

            areas.append(
                ParkTuple(
                    name=name,
                    state=state_name,
                    latitude=latitude,
                    longitude=longitude,
                    agency='NPS',
                    date=date,
                )
            )

    # The other table has sublists with stuff in it, e.g. National Capital
    # Parks-East also has Anacostia Park, Baltimore-Washington Parkway, etc.
    uls = other_table.findall('ul')
    for ul in uls:
        for li in ul.findall('li'):
            name = li.findall('a')[0].text

            wiki_page_name = name_column.findall('a')[0].get('href').split('wiki/')[-1]
            pq = load_wiki_page(wiki_page_name)
            latitude, longitude = _get_latitude_longitude_from_wiki_pq(pq)
            date = _get_date_from_wiki_pq(pq)
            state = _get_state_from_wiki_pq(state_names, pq)

            areas.append(
                ParkTuple(
                    name=name,
                    state=state,
                    latitude=latitude,
                    longitude=longitude,
                    agency='NPS',
                    date=date,
                )
            )

    return areas


def get_other_areas():
    """Returns a list of areas that, for whatever reason, aren't in the other
    lists.
    """
    from dateutil.parser import parse
    return (
        ParkTuple(
            name='Sunset Crater Volcano National Monument',
            state='Arizona',
            latitude=35.365579283,
            longitude=-111.500652017,
            agency='NPS',
            date=parse('1930'),
        ),
        ParkTuple(
            name='Big Sur River',
            state='California',
            latitude=36.280519,
            longitude=-121.8599558,
            agency='USFS',
            date=parse('1936'),
        ),
        ParkTuple(
            name='National AIDS Memorial Grove',
            state='California',
            latitude=37.77,
            longitude=-122.461389,
            agency='NPS',
            date=parse('1996'),
        ),
        ParkTuple(
            name='USS Arizona Memorial',
            state='Hawaii',
            latitude=21.365,
            longitude=-157.95,
            agency='NPS',
            date=parse('May 30, 1962'),
        ),
        ParkTuple(
            name='Inupiat Heritage Center',
            state='Alaska',
            latitude=71.298611,
            longitude=-156.753333,
            agency='NPS',
            date=parse('February 1, 1999'),
        ),
        ParkTuple(
            name='Land Between the Lakes National Recreation Area',
            state='Kentucky',
            latitude=36.856944,
            longitude=-88.074722,
            agency='USFS',
            date=parse('1963'),
        ),
        # This one is listed in the list of areas administed by the NPS, but
        # not on the list of national wild and scenic rivers page
        ParkTuple(
            name='Big South Fork National River and Recreation Area',
            state='Tennessee',
            latitude=36.4865,
            longitude=-84.6985,
            agency='NPS',
            date=parse('March 4, 1974'),
        ),
        ParkTuple(
            name='Chesapeake Bay Gateways Network',
            state='Maryland',
            latitude=37.32212,
            longitude=-76.25336,
            agency='NPS',
            date=parse('1998'),
        ),
        ParkTuple(
            name='Clara Barton Parkway',
            state='Maryland',
            # Midway between two end points
            latitude=(38.930403 + 38.978528) / 2.0,
            longitude=(-77.111922 + -77.206678) / 2.0,
            agency='NPS',
            date=parse('1989'),
        ),
        ParkTuple(
            name='Glen Echo Park',
            state='Maryland',
            latitude=38.966389,
            longitude=-77.138056,
            agency='NPS',
            date=parse('June 8, 1984'),
        ),
        ParkTuple(
            name='Western Arctic National Parklands',
            state='Alaska',
            latitude=38.989167,
            longitude=-76.898333,
            agency='NPS',
            date=None,
        ),
        ParkTuple(
            name='Western Historic Trails Center',
            state='Iowa',
            latitude=41.2259667,
            longitude=-95.8982943,
            agency='NPS',
            date=None,
        ),
        ParkTuple(
            name='Oregon Caves National Monumenti',
            state='Oregon',
            latitude=42.095556,
            longitude=-123.405833,
            agency='NPS',
            date=parse('July 12, 1909'),
        ),
        ParkTuple(
            name='Saint Croix National Scenic Riverway',
            latitude=45.389167,
            longitude=-92.6575,
            state='Wisconsin',
            agency='NPS',
            date=parse('October 2, 1968'),
        ),
        ParkTuple(
            name='Glacier Bay National Park and Preserve',
            state='Alaska',
            latitude=58.5,
            longitude=-137,
            agency='USFS',
            date=parse('1963'),
        ),
    )


def _get_state_from_wiki_pq(state_names, wiki_pq):
    """Try to guess the state by just seeing which one has the most links on
    on its respective wiki page.
    """
    state_counts = dict()
    state_set = set(state_names)

    # Try to count direct links to states first
    for link in wiki_pq('a'):
        if link.get('href') is not None and '/wiki/' in link.get('href'):
            wiki_state = link.get('href').split('/wiki/')[1]
            state = wiki_state.replace('_', ' ')
            if state in state_set:
                if state in state_counts:
                    state_counts[state] += 1
                else:
                    state_counts[state] = 1
                continue

    if len(state_counts) > 0:
        most_common_state = max(
            state_counts.items(),
            key=lambda s_c: s_c[1]
        )[0]
        max_count = state_counts[most_common_state]
        ties_for_first = [
            s_c[0] for s_c in state_counts.items() if s_c[1] == max_count
        ]

    if len(state_counts) == 0 or len(ties_for_first) == 0:
        # Count direct links to states and links to places with states in the
        # name, like "Essex County, Massachusetts". I could do this in a
        # one-liner, but it would be create tons of temporary variables and be
        # super slow.
        state_counts = dict()
        for link in wiki_pq('a'):
            if link.text is None or link.text == '':
                continue
            for state in state_set:
                if state.replace(' ', '_') in link.text:
                    if state in state_counts:
                        state_counts[state] += 1
                    else:
                        state_counts[state] = 1
                    continue

        most_common_state = max(
            state_counts.items(),
            key=lambda s_c: s_c[1]
        )[0]

    # Sanity check
    max_count = state_counts[most_common_state]
    ties_for_first = [
        s_c[0] for s_c in state_counts.items() if s_c[1] == max_count
    ]
    if len(ties_for_first) > 1:
        title = wiki_pq('title')[0].text.split('Wikipedia')[0]
        logger.warning(
            'Unable to reliably choose between states'
            ' for {park}: {states}'.format(
                park=title,
                states=', '.join(ties_for_first),
            )
        )

    return most_common_state


def _get_latitude_longitude_from_wiki_pq(wiki_pq):
    """Get the latitude and longitude from the wiki."""
    geo_decimal_spans = wiki_pq('span.geo')
    if len(geo_decimal_spans) == 0:
        return (None, None)
    geo_text = geo_decimal_spans[0].text
    latitude_text, longitude_text = geo_text.split(';')
    try:
        latitude = float(latitude_text)
        longitude = float(longitude_text)
        return (latitude, longitude)
    except:
        return (None, None)


def _get_date_from_wiki_pq(wiki_pq):
    from dateutil.parser import parse
    date_tr = [
        PyQuery(i).text() for i in wiki_pq('tr')
        if 'Established' in PyQuery(i).text()
        or 'Designated' in PyQuery(i).text()
    ]
    date = None
    if len(date_tr) == 1:
        try:
            date_string = date_tr[0]
            date_string = date_string.replace('Established', '')
            date_string = date_string.replace('Designated', '')

            # If there's a Wiki citation, ignore it
            if '[' in date_string:
                date_string = date_string.split('[')[0]
            # If there's HTML markup, ignore it
            if '&' in date_string:
                date_string = date_string.split('&')[0]
            # If there's a clarification e.g.:
            # December 2, 1980(Park &; Preserve)December 1, 1978(National Monument)
            # then ignore it
            if '(' in date_string:
                date_string = date_string.split('(')[0].strip()

            date = parse(date_string, fuzzy=True)
        except:
            try:
                # Some pages have extra crap hidden behind spans with
                # display:none. The only I've seen just has a year, so try to
                # just parse that.
                year = re.findall(r'(\d+)', date_string)[0].strip()
                if int(year) < 1980 or int(year) > 2012:
                    raise ValueError
                date = parse(year)
            except:
                logger.warning(
                    'Couldn\'t parse "{date}" as date on page {page}'.format(
                        date=date_string,
                        page=wiki_pq('title')[0].text,
                    )
                )
    return date


def guess_canonical_park(park_name, session):
    """Guesses the canonical name of the park as is stored in the database."""
    if not hasattr(guess_canonical_park, 'canonical_parks'):
        full_parks = session.query(Park).all()
        guess_canonical_park.canonical_parks = []
        for full_park in full_parks:
            trimmed_name = _remove_common_park_words(full_park.name)
            guess_canonical_park.canonical_parks.append(
                (full_park, trimmed_name)
            )

    trimmed_park = _remove_common_park_words(park_name)

    best_closeness_index = -1
    best_closeness = -100000.0
    for index in range(
        len(
            guess_canonical_park.canonical_parks
        )
    ):
        trimmed_canonical = guess_canonical_park.canonical_parks[index][1]
        new_closeness = levenshtein_ratio(trimmed_canonical, trimmed_park, cutoff=best_closeness)
        if new_closeness > best_closeness:
            best_closeness = new_closeness
            best_closeness_index = index

    canonical = guess_canonical_park.canonical_parks[best_closeness_index][0].name
    trimmed_canonical = guess_canonical_park.canonical_parks[best_closeness_index][1]
    if levenshtein_ratio(trimmed_park, trimmed_canonical) < .8:
        logger.warning(
            '"{park}":"{trimmed_park}" guessed as\n"{canonical}":"{trimmed_canonical}"'.format(
                park=park_name,
                trimmed_park=trimmed_park,
                canonical=canonical,
                trimmed_canonical=trimmed_canonical,
            )
        )
    return guess_canonical_park.canonical_parks[best_closeness_index][0]


def _remove_common_park_words(park_name):
    """Removes common park words (such as 'National Park') from a park name."""
    common_word_regexes = (
        r'\bPark\b',
        r'\bNational\b',
        r'\band\b',
        r'\bCemetery\b',
        r'\bPreserve\b',
        r'\bTrail\b',
        r'\bScenic\b',
        r'\bHistoric\b',
        r'\bHistorical\b',
        r'\bRecreation\b',
        r'\bRecreational\b',
        r'\bHeritage\b',
        r'\bArea\b',
        r'\bWild\b',
        r'\bScenic\b',
        r'\bMonument\b',
        r'\bMemorial\b',
        r'&', # No word boundary here; I was having trouble getting it to work
    )
    for regex in common_word_regexes:
        park_name = re.sub(regex, '', park_name)
    while '  ' in park_name:
        park_name = park_name.replace('  ', ' ')
    park_name = park_name.strip()
    return park_name


def load_park_stamps_csv(csv_reader):
    """Loads the parks, stamps, and stamp location entries from the list CSV.
    Returns an array of NamedTuples with park and text.
    """
    c = {
        'park': 0,
        'stamp': 1,
    }

    bonus_re = re.compile(r'bonus|bonue|bpnus', re.IGNORECASE)
    stamper_re = re.compile(r'stamp|stanp', re.IGNORECASE)

    current_park = None

    rows = []

    StampTuple = namedtuple('StampTuple', ['park', 'text', 'state'])
    state = 'Alabama' # Prime the loop, this is the first alphabetic state

    for row in csv_reader:
        # Good rows start with the name of a state in the park column
        if (
            row[c['park']] != ''
            and row[c['stamp']].strip() == ''
        ):
            # The list has "George Washington Memorial Parkway" on its own
            # (ugh, this thing is terribly formatted) so if a state has a space
            # and doesn't start with "New", assume it's just bad formatting
            if ' ' in row[c['park']] and 'New' not in row[c['park']]:
                logger.warning(
                    'Assuming that {entry} is not a state'.format(
                        entry=row[c['park']],
                    )
                )
                continue
            state = row[c['park']].strip()
            # Some states list which region they're in, so remove that
            state = re.sub(r'\(.*\)', '', state).strip()
            continue

        if state == 'Other':
            continue

        # Sometimes merges the park cells and had the same park for a few
        # stamps in a row
        if row[c['park']] != '':
            new_park = remove_whitespace(remove_newlines(row[c['park']]))
            new_park = new_park.strip()
            # Some parks have dashes, while their identical counterparts in
            # other regions don't, so just remove dashes
            new_park = new_park.replace('-', ' ')
            # Try to make some things consistent I guess
            new_park = new_park.replace('&', 'and')
            # Some parks have abbreviations because, according to the list,
            # that's the exact wording on the pamphlet. That's dumb.
            new_park = new_park.replace('NHA', 'National Heritage Area')
            new_park = new_park.replace('NHT', 'National Historic Trail')
            new_park = new_park.replace('NHP', 'National Historical Park')

            if new_park.strip() == '' or row[c['stamp']] == '':
                continue

            current_park = new_park

        stamp = remove_whitespace(row[c['stamp']]).strip()

        # Ignore empty lines
        if len(stamp) == 0:
            continue
        if (
            # Anything that doesn't have exactly 2 lines deserves a second look
            stamp.count('\n') != 1
        ):
            reason = 'there are {count} newlines'.format(
                count=stamp.count('\n')
            )

            logger.warning(
                'Skipping stamp "{stamp}" because {reason}'.format(
                    stamp=stamp.replace('\n', ';'),
                    reason=reason,
                )
            )
            continue

        rows.append(StampTuple(current_park, stamp, state))

    return rows


def get_region_from_state(state, session):
    """Given a state, returns the region that the state belongs to."""
    mapping = {
        'AL': 'SE',
        'AK': 'PNWA',
        'AZ': 'W',
        'AR': 'SW',
        'CA': 'W',
        'CO': 'RM',
        'CT': 'NA',
        'DC': 'NC',
        'DE': 'MA',
        'FL': 'SE',
        'GA': 'SE',
        'GU': 'W', # Guam
        'HI': 'W',
        'ID': 'PNWA',
        'IL': 'MW',
        'IN': 'MW',
        'IA': 'MW',
        'KS': 'MW',
        'KY': 'SE',
        'LA': 'SW',
        'ME': 'NA',
        'MD': 'MA',
        'MA': 'MA',
        'MI': 'MW',
        'MN': 'MW',
        'MS': 'SE',
        'MO': 'MW',
        'MT': 'RM',
        'NE': 'MW',
        'NV': 'W',
        'NH': 'NA',
        'NJ': 'MA',
        'NM': 'SW',
        'NY': 'NA',
        'NC': 'SE',
        'ND': 'RM',
        'OH': 'MW',
        'OK': 'SW',
        'OR': 'PNWA',
        'PA': 'MA',
        'PR': 'W', # TODO(bskari|2012-12-22) I don't know if this is the right region for Puerto Rico
        'RI': 'NA',
        'SC': 'SE',
        'SD': 'RM',
        'TN': 'SE',
        'TX': 'SW',
        'UT': 'RM',
        'VI': 'W', # TODO(bskari|2012-12-22) I don't know if this is the right region for the Virgin Islands
        'VT': 'NA',
        'VA': 'MA',
        'WA': 'PNWA',
        'WV': 'MA',
        'WI': 'MW',
        'WY': 'RM',
    }
    if state in mapping:
        return mapping[state]
    abbreviations = session.query(
        State.abbreviation
    ).filter(
        State.name == state
    ).all()
    if len(abbreviations) == 1 and abbreviations[0].abbreviation in mapping:
        return mapping[abbreviations[0].abbreviation]
    logger.warning(
        "Couldn't find region for state {state}".format(
            state=state,
        )
    )
    return 'PNWA'


def guess_park_type(park_name):
    best_match = ('', '')
    for abbreviation, type in get_park_types().items():
        if type in park_name and len(best_match[1]) < len(type):
            best_match = (abbreviation, type)

    if not best_match[0]:
        if 'Park' in park_name:
            return 'NP'
        if 'Site' in park_name or 'Fort' in park_name:
            return 'NHS'
        if 'River' in park_name:
            return 'NR'
        if 'Memorial' in park_name:
            return 'N MEM'
        # Dont just check for 'Monument' because 'National Monument and Preserve'
        # is a separate type
        if 'Volcanic Monument' in park_name:
            return 'NM'
        if 'Washington Monument' in park_name:
            return 'NM'

    if best_match[0] == '':
        return None
    else:
        return best_match[0]


def load_states(filename=None):
    filename = filename or 'parks/scripts/initialize_db/state_table.csv'
    reader = csv.reader(open(filename, 'r'), quotechar='"')
    StateTuple = namedtuple('StateTuple', ['name', 'abbreviation', 'type'])
    states = [
        # statetable.com has spaces after most Canadian provinces, so strip
        StateTuple(name=name.strip(), abbreviation=abbreviation, type=type)
        for _, name, abbreviation, _, type, _, _, occupied, _ in reader
        if occupied != 'unoccupied' # Skip unoccupied areas, like islands
    ]
    # First row is just headers so skip it
    states = states[1:]
    # Add some that aren't included by statetable.com
    # These are in the list, but they're listed separately as islands, and the
    # Pacific Remote Islands Marine National Monument spans multiple islands
    # anyway, so just lump them together
    states.append(
        StateTuple(
            name='U.S. Minor Outlying Islands',
            abbreviation='MOI',
            type='minor outlying islands',
        )
    )
    return states



def save_states(states, session):
    for state in states:
        state = State(
            name=state.name,
            abbreviation=state.abbreviation,
            type=state.type,
        )
        session.add(state)


def format_park_tuples(wiki_list, list_stamp_entries):
    """Returns a list of ParkTuples with data loaded from the list and
    Wikipedia.
    """
    # We want to have data for as many of the entries from the list
    # as possible
    names_from_wiki = set([p.name for p in wiki_list])
    wiki_dict = dict([(p.name, p) for p in wiki_list])
    park_list = []
    unique_park_list = set()
    for entry in list_stamp_entries:
        if entry.park not in unique_park_list:
            unique_park_list.add(entry.park)
            if entry.park in names_from_wiki:
                state = entry.state
                if wiki_dict[entry.park].state is not None and wiki_dict[entry.park].state != entry.state:
                    # Go with the wiki, because... Yellowstone's in Wyoming,
                    # not Montana!
                    state = wiki_dict[entry.park].state
                    logger.warning(
                        'State disagrees for {name}, choosing {wiki_state} from wiki instead of {list_state}'.format(
                            name=entry.park,
                            wiki_state=wiki_dict[entry.park].state,
                            list_state=entry.state,
                        )
                    )
                park_list.append(
                    ParkTuple(
                        name=entry.park,
                        state=state,
                        latitude=wiki_dict[entry.park].latitude,
                        longitude=wiki_dict[entry.park].longitude,
                        agency='NPS',
                        date=wiki_dict[entry.park].date,
                    )
                )
            else:
                logger.warning('No wiki entry for {name}'.format(name=entry.park))
                park_list.append(
                    ParkTuple(
                        name=entry.park,
                        state=entry.state,
                        latitude=None,
                        longitude=None,
                        agency=None,
                        date=None,
                    )
                )

    return park_list


def save_parks(session, parks):
    def normalized_url_from_name(name):
        url = name.lower()
        url = url.strip()
        url = re.sub("'", '', url)
        def strip_accents(unicode):
            return unicodedata.normalize(
                'NFKD',
                unicode
            ).encode(
                'ascii',
                'ignore'
            )
        url = strip_accents(url)
        url = str(url)
        # Don't include the UNICODE flag here, so that we remove all non-ASCII
        url = url.strip()
        url = re.sub('\\W', '-', url)
        # Removing punctuation can cause duplicate dashes
        url = re.sub('-+', '-', url)
        url = re.sub('-$', '', url)
        url = re.sub('^-', '', url)
        url = re.sub("'", '', url)
        return url

    def stripped_url_from_name(name):
        url = normalized_url_from_name(name)
        # Drop the "National Park", etc.
        url = re.sub('national.*', '', url)
        url = re.sub('memorial.*', '', url)
        url = re.sub('park.*', '', url)
        url = url.strip()
        url = re.sub('-$', '', url)
        url = re.sub('^-', '', url)
        url = url.strip()
        return url

    used_once_url = set()
    used_multiple_url = set()
    for park in parks:
        url = stripped_url_from_name(park.name)
        if url in used_once_url:
            used_multiple_url.add(url)
        else:
            used_once_url.add(url)

    urls = set()
    for park in parks:
        park_type = guess_park_type(park.name)

        if park_type is None:
            logger.warning(
                'Unknown park type for {park}'.format(park=park.name)
            )
        state = park.state
        #if not isinstance(state, str):
        #    print(state)
        #    import pdb; pdb.set_trace()

        url = stripped_url_from_name(park.name)
        # Some things start with the word "National", like
        # "National Constitution Center"
        need_full_name_for_url = False
        for i in ('National', 'International'):
            if park.name.startswith(i):
                need_full_name_for_url = True
                break
        if url in used_multiple_url:
            need_full_name_for_url = True

        if need_full_name_for_url:
            url = normalized_url_from_name(park.name)

        # Normalize to statetable.com's naming convention
        if state is not None:
            if (
                re.search('washington.*d.*c', state.lower()) or \
                re.search('district.*of.*columbia', state.lower())
            ):
                state = 'Washington DC'
            # US Virgin Islands, US Minor Outlying Islands, etc. => U.S.
            state = state.replace('US', 'U.S.')
            if 'Virgin' in state:
                state = 'U.S. Virgin Islands'

        if url not in urls:
            urls.add(url)
            park_row = Park(
                name=park.name,
                url=url,
                type=park_type,
                region=get_region_from_state(state, session),
                state=state,
                latitude=park.latitude,
                longitude=park.longitude,
                date_founded=park.date,
            )
            session.add(park_row)
        else:
            logger.error('Duplicate URL for {park}'.format(park=park.name))


def save_stamps(session, stamp_texts):
    """Creates Stamp entries in the database."""
    for text in set(stamp_texts):
        stamp = Stamp(text=text, type='normal', status='active')
        session.add(stamp)


def save_stamp_locations(session, stamp_info_entries):
    """Creates StampLocation entries in the database."""
    park_id_objects = session.query(Park.id, Park.latitude, Park.longitude).all()
    for park_id_object in park_id_objects:
        stamp_location = StampLocation(
            park_id=park_id_object.id,
            description='Uncategorized',
            latitude=park_id_object.latitude,
            longitude=park_id_object.longitude,
        )
        session.add(stamp_location)

    for stamp_info in stamp_info_entries:
        guess_park = guess_canonical_park(stamp_info.park, session)

        stamp_id = session.query(
            Stamp.id
        ).filter(
            Stamp.text == stamp_info.text
        ).scalar()

        stamp_location_id = session.query(
            StampLocation.id
        ).join(
            Park
        ).filter(
            Park.id == guess_park.id
        ).scalar()

        stamp_to_location = StampToLocation(stamp_id=stamp_id, stamp_location_id=stamp_location_id)
        session.add(stamp_to_location)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    global logger
    logger = logging.Logger('initializedb')
    formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s %(message)s'
    )
    file_handler = None
    try:
        file_handler = logging.FileHandler('initializedb.log')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except Exception as exception:
        logging.warning('Could not create file log: ' + str(exception))

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.WARNING)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    if engine.driver == 'mysqldb':
        # MySQL does case insensitive compares for most things, but stamp text
        # needs to be case sensitive
        cursor = engine.raw_connection().cursor()
        # MySQL can't do case sensitive UTF8 collation because, well, it's
        # hard. Different countries and locales have different orderings, so
        # the best we can do is just do binary, which is probably fine.
        text_column = Stamp.text.property.columns[0]
        assert isinstance(text_column.type, String)
        cursor.execute(
            'ALTER TABLE {table} MODIFY {column} {type} ({length}) COLLATE utf8_bin'.format(
                table=Stamp.__tablename__,
                column=text_column.name,
                type='VARCHAR', # Default used by SQLAlchemy for String
                length=text_column.type.length,
            )
        )

    states = load_states()

    # Load the canonical park list from Wikipedia
    parks = get_national_parks()
    monuments = get_national_monuments()
    lakeshores, seashores = get_national_lakeshores_and_seashores()
    grasslands = get_national_grasslands()
    marine_sanctuaries = get_national_marine_sanctuaries([s.name for s in states])
    rivers = get_rivers()
    memorials = get_national_memorials()
    heritage_areas = get_national_heritage_areas([s.name for s in states])
    nps_exclusives = get_nps_exclusive_areas([s.name for s in states])
    national_trails = get_national_trails()
    other_areas = get_other_areas()

    # Load data for parks
    with codecs.open('parks/scripts/initialize_db/list.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, quotechar='"')
        stamp_info_entries = load_park_stamps_csv(reader)

    with transaction.manager:
        save_states(states, DBSession)

    # We have to set these, because some areas belong to more than one
    # designation, e.g. Aniakchak National Monument and Preserve
    names = set()
    wiki_list = []
    for areas_list in (
        parks,
        monuments,
        lakeshores,
        seashores,
        grasslands,
        marine_sanctuaries,
        rivers,
        memorials,
        heritage_areas,
        nps_exclusives,
        national_trails,
        other_areas,
    ):
        for area in areas_list:
            if area.name not in names:
                wiki_list.append(area)
                names.add(area.name)

    park_list = format_park_tuples(wiki_list, stamp_info_entries)

    with transaction.manager:
        save_parks(DBSession, park_list)
    with transaction.manager:
        save_stamps(DBSession, set([stamp.text for stamp in stamp_info_entries]))
    with transaction.manager:
        save_stamp_locations(DBSession, stamp_info_entries)

        user = User(
            username='guest',
            password='password',
            signup_ip=1,
        )
        DBSession.add(user)
