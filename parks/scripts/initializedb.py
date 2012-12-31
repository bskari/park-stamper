# -*- coding: utf-8 -*
from BeautifulSoup import BeautifulSoup
import codecs
import csv
import math
from collections import namedtuple
import os
from dateutil.parser import parse
import re
import sys
import transaction
import unicodedata
import urllib2

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from sqlalchemy import engine_from_config

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

class DumbLogger(object):
    """I can't get Python logging to work right; this is a hopefully temporary
    shim to work around it.
    """
    def __init__(self, filename):
        self.file = codecs.open(filename, mode=u'w', encoding=u'utf-8')

    def warning(self, string):
        self.file.write(string + u'\n')
        print(string)
        self.file.flush()

    def error(self, string):
        self.file.write(string + u'\n')
        print(string)
        self.file.flush()

logger = None


ParkTuple = namedtuple(
    u'ParkTuple',
    [u'name', u'state', u'latitude', u'longitude', u'agency', u'date']
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(u'usage: %s <config_uri>\n'
          u'(example: "%s development.ini")' % (cmd, cmd))
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

    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        current_row_min = sys.maxint
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


def save_page_to_file(soup, filename):
    """For debugging, so I'm not hitting Wikipedia constantly."""
    with open(filename, u'w') as f:
        f.write(str(soup))

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
        pickle_filename = filename + '.soup.pickle'
        # Pickle sometimes blows up with stack overflow, so... do this in a
        # try/except block
        try:
            with open(pickle_filename, u'w') as f:
                pickle.dump(soup, f)
        except:
            pass


def load_page_from_file(filename):
    with open(filename, u'r') as f:
        soup = BeautifulSoup(f.read())
    return soup


def load_page_from_pickle_file(filename):
    pickle_filename = filename + '.soup.pickle'
    # Only try to load the pickle if it's newer than the Wikipedia file
    import os
    wiki_stats = os.stats(filename)
    pickle_stats = os.stats(pickle_filename)
    if pickle_stats.st_ctime < wiki_stats.st_ctime:
        os.unlink(pickle_filename)
        soup = load_page_from_file(filename)
        save_page_to_file(soup, filename)
        return soup

    try:
        # Use Python's __import__ function to ignore Pyflakes warnings
        pickle = __import__('cpickle')
    except:
        # Fall back to slower, regular pickle
        pickle = __import__('pickle')

    with open(pickle_filename, u'r') as f:
        soup = pickle.load(f)
    return soup


def load_page_from_url(url):
    user_agent = u'Mozilla/5 (Solaris 10) Gecko'
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(request)

    soup = BeautifulSoup(response.read())
    return soup


def load_wiki_page(wiki_page_name):
    """Returns the soup of the given Wiki page name. If the file has been
    accessed before and saved, it will use that. If not, it will access
    Wikipedia, download the page, save it for future calls, and then return
    the soup.
    """
    # Some wikis have / in them, which messes with Linux files
    escaped_wiki_page_name = wiki_page_name.replace('/', '-')
    filename = u''.join(
        (
            u'parks/scripts/initialize_db/',
            escaped_wiki_page_name,
            u'.html',
        )
    )

    try:
        soup = load_page_from_pickle_file(filename)
    except:
        try:
            soup = load_page_from_file(filename)
        except:
            soup = load_page_from_url(
                u''.join(
                    (
                        u'http://en.wikipedia.org/wiki/',
                        wiki_page_name,
                    )
                )
            )
            save_page_to_file(soup, filename)
    return soup


def get_national_parks():
    """Loads the list of national parks from Wikipedia."""
    soup = load_wiki_page(u'List_of_national_parks_of_the_United_States')
    tables = soup.fetch(u'table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    assert len(wikitables) == 1
    np_table = wikitables[0]
    trs = np_table.fetch(u'tr')

    parks = []

    # Skip the header row
    for tr in trs[1:]:
        # The name is in a th tag
        name = tr.fetch(u'th')[0].fetch(u'a')[0]['title']
        # Remove Unicode emdash
        name = name.replace(u'\u2013', u'-')

        # The remaining columns are photo, location, date, area, description
        _, location_column, date_column, _, _ = tr.fetch(u'td')

        # The location column has one or more states and a GPS coordinate
        state_name = location_column.fetch(u'a')[0].text
        gps_text = location_column.fetch(u'a')[-1].text
        # gps_text looks like:
        # 44°21′N68°13′W / 44.35°N 68.21°W /44.35; -68.21 (Acadia)
        float_text = gps_text.split(u'/')[-1]
        latitude_text, longitude_text = re.findall(r'([-]?\d+(?:\.\d+)?)', float_text)
        latitude = float(latitude_text)
        longitude = float(longitude_text)

        date = parse(date_column.fetch(u'span')[-1].text, fuzzy=True)

        parks.append(
            ParkTuple(
                name=name,
                state=state_name,
                latitude=latitude,
                longitude=longitude,
                agency=u'NPS',
                date=date,
            )
        )

    return parks


def get_national_monuments():
    """Loads the list of national monuments from Wikipedia."""
    soup = load_wiki_page(u'List_of_National_Monuments_of_the_United_States')
    tables = soup.fetch(u'table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    # There's an u'breakdown by agency' table and a list table
    assert len(wikitables) == 2
    nm_table = wikitables[1]
    trs = nm_table.fetch(u'tr')

    monuments = []

    # Skip the header row
    for tr in trs[1:]:
        # The columns are name, photo, agency, location, date, description
        name_column, _, agency_column, location_column, date_column, _ = tr.fetch(u'td')
        name = name_column.fetch(u'a')[0]['title']

        agency = agency_column.fetch(u'a')[0].text

        # The location column has one or more states and a GPS coordinate
        state_name = location_column.fetch(u'a')[0].text
        gps_text = location_column.fetch(u'a')[-1].text
        # gps_text looks like:
        # 44°21′N68°13′W / 44.35°N 68.21°W /44.35; -68.21 (Acadia)
        float_text = gps_text.split(u'/')[-1]
        try:
            latitude_text, longitude_text = re.findall(r'([-]?\d+(?:\.\d+)?)', float_text)
            latitude = float(latitude_text)
            longitude = float(longitude_text)
        except:
            latitude = longitude = None
            logger.warning(
                u'Skipping GPS {gps_text} for {monument}'.format(
                    gps_text=gps_text,
                    monument=name,
                )
            )

        date = parse(date_column.fetch(u'span')[-1].text, fuzzy=True)

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
    soup = load_wiki_page(u'List_of_United_States_national_lakeshores_and_seashores')
    tables = soup.fetch(u'table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    # There's a seashore table and a lakeshore table
    assert len(wikitables) == 2

    lakeshores = []
    seashores = []

    for table, list in zip(wikitables, (lakeshores, seashores)):
        trs = table.fetch(u'tr')
        # Skip the header row
        for tr in trs[1:]:
            # The columns are name, photo, location, date, area, description
            name_column, _, location_column, date_column, _, _ = tr.fetch(u'td')
            name = name_column.fetch(u'a')[0]['title']

            # The location column has one or more states and a GPS coordinate
            state_name = location_column.fetch(u'a')[0].text
            gps_text = location_column.fetch(u'a')[-1].text
            # gps_text looks like:
            # 44°21′N68°13′W / 44.35°N 68.21°W /44.35; -68.21 (Acadia)
            float_text = gps_text.split(u'/')[-1]
            latitude_text, longitude_text = re.findall(r'([-]?\d+(?:\.\d+)?)', float_text)
            latitude = float(latitude_text)
            longitude = float(longitude_text)

            date = parse(date_column.fetch(u'span')[-1].text, fuzzy=True)

            list.append(
                ParkTuple(
                    name=name,
                    state=state_name,
                    latitude=latitude,
                    longitude=longitude,
                    agency=u'NPS',
                    date=date,
                )
            )

    return (lakeshores, seashores)


def get_national_grasslands():
    """Loads the list of national grasslands from Wikipedia."""
    soup = load_wiki_page(u'United_States_National_Grassland')
    tables = soup.fetch(u'table')
    # There's a list for TOC, a list of national grasslands, a list of prairie
    # reserves, a list of "See also" stuff, and a ton of other crap
    grassland_table = tables[1]

    grasslands = []

    for tr in grassland_table.fetch(u'tr')[1:]: # Skip the header
        name = tr.fetch(u'th')[0].text
        # Photo, Location, Administered by, Area, Description
        _, location_td, _, _, _ = tr.fetch(u'td')
        # Some entries have multiple states, e.g. "Oklahoma, Texas"
        state = location_td.text.split(',')[0]
        geo_text = location_td.fetch('span', {'class': 'geo'})[0].text
        latitude_text, longitude_text = re.findall(r'([-]?\d+(?:\.\d+)?)', geo_text)
        latitude = float(latitude_text)
        longitude = float(longitude_text)

        grasslands.append(
            ParkTuple(
                name=name,
                state=state,
                agency=u'NFS',
                latitude=latitude,
                longitude=longitude,
                date=None,
            )
        )

    return grasslands


def get_national_marine_sanctuaries(state_names):
    """Loads the list of national marine sanctuaries from Wikipedia."""
    soup = load_wiki_page(u'United_States_National_Marine_Sanctuary')
    ul_lists = soup.fetch(u'ul')
    # There's a list of marine sanctuaries, and a ton of other crap
    sanctuary_list = ul_lists[0]

    sanctuaries = []

    for li in sanctuary_list.fetch(u'li'):
        wiki_page_name = li.fetch(u'a')[0][u'href'].split(u'wiki/')[-1]
        soup = load_wiki_page(wiki_page_name)
        state = _get_state_from_wiki_soup(state_names, soup)
        latitude, longitude = _get_latitude_longitude_from_wiki_soup(soup)
        date = _get_date_from_wiki_soup(soup)

        name = li.fetch(u'a')[0].text
        # Wikipedia includes some national monuments here too
        if u'National Marine Sanctuary' not in name:
            logger.warning(
                u'Skipping {name} claiming to be a national marine sanctuary'.format(
                    name=name,
                )
            )
            continue


        ParkTuple(
            name=name,
            state=state,
            agency=u'NMSP', # National Marine Sanctuaries Program
            latitude=latitude,
            longitude=longitude,
            date=date,
        )

    return sanctuaries


def get_rivers():
    """Loads the list of national wild and scenic rivers from Wikipedia."""
    soup = load_wiki_page(u'List_of_National_Wild_and_Scenic_Rivers')
    ul_lists = soup.fetch(u'ul')
    # There's a TOC, list of bureaus and other crap
    state_river_lists = ul_lists[2:42]

    rivers = []
    river_names = set()

    for state_river_list in state_river_lists:
        # Some lists have sublists, so if there are no spans, just skip it
        try:
            state = state_river_list.previousSibling.previousSibling.fetch(u'span')[1].text
            # Some headings have things like "Georgia, North Carolina and South Carolina"
            if u',' in state:
                state = state.split(u',')[0].strip()
            elif u' and' in state:
                state = state.split(u' and')[0].strip()
        except IndexError:
            continue

        for li in state_river_list.fetch(u'li'):
            # Some lists have sublists, so if there's no links, just skip it
            try:
                name = li.fetch(u'a')[0]['title']
            except IndexError:
                continue

            # Some rivers are listed in more than one state - skip duplicates
            if name in river_names:
                continue
            river_names.add(name)

            try:
                agency = li.text.split(u',')[1].strip()
                # Remove crap like "BLM/NPS/USFS", "NPS/Florida"
                if u'/' in agency:
                    agency = agency.split(u'/')[0].strip()
                # Some places have the state listed; ignore it
                if agency not in (u'NPS', u'USFS', u'BLM', u'ACOE', u'USFWS'):
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
    national_trails = []

    for page in (u'National_Historic_Trail', u'National_Scenic_Trail'):
        soup = load_wiki_page(page)
        tables = soup.fetch(u'table')
        wikitables = [t for t in tables if u'wikitable' in t['class']]
        assert len(wikitables) == 1

        trs = wikitables[0].fetch(u'tr')

        # Skip the header row and total length row
        for tr in trs[1:-1]:
            # The columns are trail name, year established, length authorized
            name_column, date_column, _ = tr.fetch(u'td')
            name = name_column.fetch(u'a')[0].text

            date_text = date_column.text
            date = parse(date_text)

            national_trails.append(
                ParkTuple(
                    name=name,
                    latitude=None,
                    longitude=None,
                    state=None,
                    agency=u'NPS',
                    date=date,
                )
            )

    return national_trails


def get_national_memorials():
    """Loads the list of national memorials from Wikipedia."""
    soup = load_wiki_page(u'List_of_National_Memorials_of_the_United_States')
    tables = soup.fetch(u'table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    # There's a national memorials table and an affiliated areas table
    assert len(wikitables) == 2

    memorials = []

    # TODO(bskari|2012-11-19) do something with areas?
    #for table, list in zip(wikitables, (memorials, areas)):
    for table, list in zip(wikitables[0:1], (memorials,)):
        trs = table.fetch(u'tr')
        # Skip the header row
        for tr in trs[1:]:
            # The columns are name, photo, location, date, area, description
            name_column, _, location_column, date_column, _, _ = tr.fetch(u'td')
            name = name_column.fetch(u'a')[0]['title']

            # The location column has the sate
            state_name = location_column.fetch(u'a')[0].text

            date_text = date_column.fetch(u'span')[-1].text
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
                    agency=u'NPS',
                    date=date,
                )
            )

    return memorials


def get_national_heritage_areas(state_names):
    """Loads the list of national heritage areas from Wikipedia."""
    soup = load_wiki_page(u'National_Heritage_Area')
    ul_lists = soup.fetch(u'ul')
    # There's a list of heritage areas, and other crap
    heritage_area_list = ul_lists[1]

    heritage_areas = []

    for li in heritage_area_list.fetch(u'li'):
        name = li.fetch(u'a')[0].text
        name = name.replace(u'&amp;', u'&')

        # Some names leave off the NHA or whatever, so add them back in
        if u'National Heritage Area' not in name:
            if u'Canal' in name:
                name = name + u' National Heritage Area'
            elif u'River' in name and u'Corridor' not in name:
                name = name + u' Corridor'

        if u'Heritage' not in name and u'Corridor' not in name and u'District' not in name:
            logger.warning(
                u'Incomplete name for heritage area: "{name}", skipping'.format(
                    name=name
                )
            )
            continue

        wiki_page_name = li.fetch(u'a')[0][u'href'].split(u'wiki/')[-1]
        soup = load_wiki_page(wiki_page_name)
        state = _get_state_from_wiki_soup(state_names, soup)

        heritage_areas.append(
            ParkTuple(
                name=name,
                state=state,
                agency=u'NHA',
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
    soup = load_wiki_page(u'List_of_areas_in_the_United_States_National_Park_System')
    tables = soup.fetch(u'table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    assert len(wikitables) == 32
    nps_table = wikitables[4] # National preserves
    nhps_table = wikitables[5]
    nhs_table = wikitables[7]
    ihs_table = wikitables[10]
    nbps_table = wikitables[11]
    nmps_table = wikitables[12]
    nbs_table = wikitables[14]
    nbss_table = wikitables[15]
    nra_table = wikitables[19]
    nrs_table = wikitables[24]
    npws_table = wikitables[25]
    nhst_table = wikitables[26]
    ncs_table = wikitables[27]
    other_table = wikitables[29]

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
        trs = table.fetch(u'tr')
        # Skip the header row
        for tr in trs[1:]:
            # The columns are name, states
            name_column, state_column = tr.fetch(u'td')
            name = name_column.fetch(u'a')[0].text

            state_name = state_column.fetch(u'a')[0].text

            wiki_page_name = name_column.fetch(u'a')[0][u'href'].split(u'wiki/')[-1]
            soup = load_wiki_page(wiki_page_name)
            latitude, longitude = _get_latitude_longitude_from_wiki_soup(soup)
            date = _get_date_from_wiki_soup(soup)

            areas.append(
                ParkTuple(
                    name=name,
                    state=state_name,
                    latitude=latitude,
                    longitude=longitude,
                    agency=u'NPS',
                    date=date,
                )
            )

    # The other table has sublists with stuff in it, e.g. National Capital
    # Parks-East also has Anacostia Park, Baltimore-Washington Parkway, etc.
    uls = other_table.fetch(u'ul')
    for ul in uls:
        for li in ul.fetch(u'li'):
            name = li.fetch(u'a')[0].text

            wiki_page_name = name_column.fetch(u'a')[0][u'href'].split(u'wiki/')[-1]
            soup = load_wiki_page(wiki_page_name)
            latitude, longitude = _get_latitude_longitude_from_wiki_soup(soup)
            date = _get_date_from_wiki_soup(soup)
            state = _get_state_from_wiki_soup(state_names, soup)

            areas.append(
                ParkTuple(
                    name=name,
                    state=state,
                    latitude=latitude,
                    longitude=longitude,
                    agency=u'NPS',
                    date=date,
                )
            )

    return areas


def get_other_areas():
    """Returns a list of areas that, for whatever reason, aren't in thr other
    lists.
    """
    return (
        ParkTuple(
            name=u'Sunset Crater Volcano National Monument',
            state=u'Arizona',
            latitude=35.365579283,
            longitude=-111.500652017,
            agency=u'NPS',
            date=parse(u'1930'),
        ),
        ParkTuple(
            name=u'Big Sur River',
            state=u'California',
            latitude=36.280519,
            longitude=-121.8599558,
            agency=u'USFS',
            date=parse(u'1936'),
        ),
        ParkTuple(
            name=u'National AIDS Memorial Grove',
            state=u'California',
            latitude=37.77,
            longitude=-122.461389,
            agency=u'NPS',
            date=parse(u'1996'),
        ),
        ParkTuple(
            name=u'USS Arizona Memorial',
            state=u'Hawaii',
            latitude=21.365,
            longitude=-157.95,
            agency=u'NPS',
            date=parse(u'May 30, 1962'),
        ),
        ParkTuple(
            name=u'Inupiat Heritage Center',
            state=u'Alaska',
            latitude=71.298611,
            longitude=-156.753333,
            agency=u'NPS',
            date=parse(u'February 1, 1999'),
        ),
        ParkTuple(
            name=u'Land Between the Lakes National Recreation Area',
            state=u'Kentucky',
            latitude=36.856944,
            longitude=-88.074722,
            agency=u'USFS',
            date=parse(u'1963'),
        ),
        # This one is listed in the list of areas administed by the NPS, but
        # not on the list of national wild and scenic rivers page
        ParkTuple(
            name=u'Big South Fork National River and Recreation Area',
            state=u'Tennessee',
            latitude=36.4865,
            longitude=-84.6985,
            agency=u'NPS',
            date=parse(u'March 4, 1974'),
        ),
        ParkTuple(
            name=u'Chesapeake Bay Gateways Network',
            state=u'Maryland',
            latitude=37.32212,
            longitude=-76.25336,
            agency=u'NPS',
            date=parse(u'1998'),
        ),
        ParkTuple(
            name=u'Clara Barton Parkway',
            state=u'Maryland',
            # Midway between two end points
            latitude=(38.930403 + 38.978528) / 2.0,
            longitude=(-77.111922 + -77.206678) / 2.0,
            agency=u'NPS',
            date=parse(u'1989'),
        ),
        ParkTuple(
            name=u'Glen Echo Park',
            state=u'Maryland',
            latitude=38.966389,
            longitude=-77.138056,
            agency=u'NPS',
            date=parse(u'June 8, 1984'),
        ),
        ParkTuple(
            name=u'Western Arctic National Parklands',
            state=u'Alaska',
            latitude=38.989167,
            longitude=-76.898333,
            agency=u'NPS',
            date=None,
        ),
        ParkTuple(
            name=u'Western Historic Trails Center',
            state=u'Iowa',
            latitude=41.2259667,
            longitude=-95.8982943,
            agency=u'NPS',
            date=None,
        ),
        ParkTuple(
            name=u'Oregon Caves National Monumenti',
            state=u'Oregon',
            latitude=42.095556,
            longitude=-123.405833,
            agency=u'NPS',
            date=parse('July 12, 1909'),
        ),
        ParkTuple(
            name=u'Saint Croix National Scenic Riverway',
            latitude=45.389167,
            longitude=-92.6575,
            state=u'Wisconsin',
            agency=u'NPS',
            date=parse('October 2, 1968'),
        ),
        ParkTuple(
            name=u'Glacier Bay National Park and Preserve',
            state=u'Alaska',
            latitude=58.5,
            longitude=-137,
            agency=u'USFS',
            date=parse('1963'),
        ),
    )


def _get_state_from_wiki_soup(state_names, wiki_soup):
    """Try to guess the state by just seeing which one has the most links on
    on its respective wiki page.
    """
    state_counts = dict()
    state_set = set(state_names)

    # Try to count direct links to states first
    for a in wiki_soup.fetch(u'a'):
        if a.has_key(u'href') and u'/wiki/' in a['href']:
            wiki_state = a[u'href'].split(u'/wiki/')[1]
            state = wiki_state.replace('_', ' ')
            if state in state_set:
                if state_counts.has_key(state):
                    state_counts[state] += 1
                else:
                    state_counts[state] = 1
                continue

    if len(state_counts) > 0:
        most_common_state = max(state_counts.iteritems(), key=lambda s_c: s_c[1])[0]
        max_count = state_counts[most_common_state]
        ties_for_first = [
            s_c[0] for s_c in state_counts.iteritems() if s_c[1] == max_count
        ]

    if len(state_counts) == 0 or len(ties_for_first) == 0:
        # Count direct links to states and links to places with states in the name,
        # like "Essex County, Massachusetts". I could do this in a one-liner, but
        # it would be create tons of temporary variables and be super slow.
        state_counts = dict()
        for a in wiki_soup.fetch(u'a'):
            link_text = a.text
            for state in state_set:
                if state.replace(' ', '_') in link_text:
                    if state in state_counts:
                        state_counts[state] += 1
                    else:
                        state_counts[state] = 1
                    continue

        most_common_state = max(state_counts.iteritems(), key=lambda s_c: s_c[1])[0]

    # Sanity check
    max_count = state_counts[most_common_state]
    ties_for_first = [
        s_c[0] for s_c in state_counts.iteritems() if s_c[1] == max_count
    ]
    if len(ties_for_first) > 1:
        logger.warning(''.join((
            'Unable to choose between states for ',
            wiki_soup.fetch(u'title')[0].text.split('Wikipedia')[0],
            ': ',
            ', '.join(ties_for_first),
            '; returning None',
        )))
        return None

    return most_common_state


def _get_latitude_longitude_from_wiki_soup(wiki_soup):
    """Get the latitude and longitude from the wiki."""
    geo_decimal_spans = wiki_soup.fetch(u'span', {'class': 'geo-dec'})
    if len(geo_decimal_spans) == 0:
        return (None, None)
    geo_dec_text = geo_decimal_spans[0].text
    latitude_text, longitude_text = re.findall(r'([-]?\d+(?:\.\d+)?)', geo_dec_text)
    try:
        latitude = float(latitude_text)
        longitude = float(longitude_text)
        return (latitude, -longitude)
    except:
        return (None, None)


def _get_date_from_wiki_soup(wiki_soup):
    date_tr = [
        i for i in wiki_soup.fetch(u'tr')
        if u'Established' in unicode(i) or u'Designated' in unicode(i)
    ]
    date = None
    if len(date_tr) == 1:
        try:
            date_string = date_tr[0].td.text

            # If there's a Wiki citation, ignore it
            if u'[' in date_string:
                date_string = date_string.split(u'[')[0]
            # If there's HTML markup, ignore it
            if u'&' in date_string:
                date_string = date_string.split(u'&')[0]
            # If there's a clarification e.g.:
            # December 2, 1980(Park &; Preserve)December 1, 1978(National Monument)
            # then ignore it
            if u'(' in date_string:
                date_string = date_string.split(u'(')[0]

            date = parse(date_string)
        except:
            try:
                # Some pages have extra crap hidden behind spans with
                # display:none. The only I've seen just has a year, so try to
                # just parse that.
                year = re.findall(r'(\d+)', date_string)[0]
                if int(year) < 1980 or int(year) > 2012:
                    raise ValueError
                date = parse(year)
            except:
                logger.warning(
                    u'Couldn\'t parse "{date}" as date on page'.format(
                        date=date_string,
                        page=wiki_soup.fetch(u'title')[0].text,
                    )
                )
    return date


def guess_canonical_park(park_name, session):
    """Guesses the canonical name of the park as is stored in the database."""
    if not hasattr(guess_canonical_park, u'canonical_parks'):
        full_parks = session.query(Park).all()
        guess_canonical_park.canonical_parks = []
        for fp in full_parks:
            trimmed_name = _remove_common_park_words(fp.name)
            guess_canonical_park.canonical_parks.append((fp, trimmed_name))

    trimmed_park = unicode(_remove_common_park_words(park_name))

    best_closeness_index = -1
    best_closeness = -100000.0
    for index in xrange(len(guess_canonical_park.canonical_parks)):
        trimmed_canonical = guess_canonical_park.canonical_parks[index][1]
        new_closeness = levenshtein_ratio(trimmed_canonical, trimmed_park, cutoff=best_closeness)
        if new_closeness > best_closeness:
            best_closeness = new_closeness
            best_closeness_index = index

    canonical = guess_canonical_park.canonical_parks[best_closeness_index][0].name
    trimmed_canonical=guess_canonical_park.canonical_parks[best_closeness_index][1]
    if levenshtein_ratio(trimmed_park, trimmed_canonical) < .8:
        logger.warning(
            u'"{park}":"{trimmed_park}" guessed as\n"{canonical}":"{trimmed_canonical}"'.format(
                park=park_name,
                trimmed_park=trimmed_park,
                canonical=canonical,
                trimmed_canonical=trimmed_canonical,
            )
        )
    return guess_canonical_park.canonical_parks[best_closeness_index][0]


def _remove_common_park_words(park_name):
    """Removes common park words (such as u'National Park') from a park name."""
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
        park_name = re.sub(regex, u'', park_name)
    while u'  ' in park_name:
        park_name = park_name.replace(u'  ', u' ')
    park_name = park_name.strip()
    return park_name


def load_park_stamps_csv(csv_reader):
    """Loads the parks, stamps, and stamp location entries from the master list
    CSV. Returns an array of NamedTuples with park, text, and address.
    """
    c = {'update': 0, u'park': 1, u'stamp': 2, u'address': 3, u'last_seen': 4, u'confirmed_by': 5, u'comment': 6}

    # There were misspellings of bonus, so use this to find them
    bonus_re = re.compile(r'bonus|bonue|bpnus', re.IGNORECASE)
    # Stampers have their own custom stamps; skip them
    stamper_re = re.compile(r'stamp|stanp', re.IGNORECASE)

    lost_stamps = False
    current_park = None

    rows = []

    StampTuple = namedtuple(u'StampTuple', [u'park', u'text', u'address', u'state'])
    state = u'Alabama' # Prime the loop, this is the first alphabetic state

    for row in csv_reader:
        # The list toggles between retired and active stamps - ignore retired ones
        if u'RETIRED' in row[c[u'park']]:
            lost_stamps = True
            continue
        # Good rows start with the name of a state in the park column
        elif lost_stamps and row[c[u'update']].strip() == '' and row[c['park']] != ''  and row[c[u'stamp']].strip() == '':
            lost_stamps = False
            # The master list has "George Washington Memorial Parkway" on its
            # own (ugh, this thing is terribly formatted) so if a state has a
            # space and doesn't start with "New", assume it's just bad formatting
            if u' ' in row[c[u'park']] and u'New' not in row[c[u'park']]:
                logger.warning(u'Assuming that {entry} is not a state'.format(entry=row[c[u'park']]))
                continue
            state = row[c[u'park']].strip()
            # Some states list which region they're in, so remove that
            state = re.sub(r'\(.*\)', u'', state).strip()
            continue
        if lost_stamps:
            continue

        if state == 'Other':
            # Entries under this heading are things from things like National
            # Parks Travelers Club, so just ignore them
            continue

        # The Excel document merges the park cells and had the same park for a
        # few stamps in a row
        if row[c[u'park']] != '':
            new_park = remove_whitespace(remove_newlines(row[c[u'park']]))
            new_park = new_park.decode(u'utf-8')
            new_park = new_park.strip()
            # Some parks have dashes, while their identical counterparts in other
            # regions don't, so just remove dashes
            new_park = new_park.replace('-', ' ')
            # Try to make some things consistent I guess
            new_park = new_park.replace('&', 'and')
            # Some parks have abbreviations because, according to the list,
            # that's the exact wording on the pamphlet. That's dumb.
            new_park = new_park.replace('NHA', 'National Heritage Area')
            new_park = new_park.replace('NHT', 'National Historic Trail')
            new_park = new_park.replace('NHP', 'National Historical Park')

            if new_park.strip() == '' or row[c[u'stamp']] == '':
                continue

            current_park = new_park

        stamp = remove_whitespace(row[c[u'stamp']]).strip()
        address = row[c[u'address']]
        address = address.decode(u'utf-8')

        if (
            # Anything that doesn't have exactly 2 lines deserves a second look
            stamp.count('\n') != 1
            # Anything that says bonus, we ignore for now
            or bonus_re.search(stamp)
            # The stampers have their own custom ones; skip them
            or stamper_re.search(stamp) or stamper_re.search(current_park)
        ):
            if not isinstance(stamp, unicode):
                stamp = unicode(stamp, errors='ignore')

            if bonus_re.search(stamp):
                reason = u'it is a bonus stamp'
            elif stamp.count('\n') != 1:
                reason = u''.join((
                    u'there are ',
                    unicode(stamp.count(u'\n')),
                    u' newlines',
                ))
            else:
                reason = u'it is a custom stamp'

            logger.warning(
                u'Skipping stamp "{stamp}" because {reason}'.format(
                    stamp=stamp.replace(u'\n', u';'),
                    reason=reason,
                )
            )
            continue

        rows.append(StampTuple(current_park, stamp, address, state))

    return rows


def get_region_from_state(state, session):
    mapping = {
        u'AL': u'SE',
        u'AK': u'PNWA',
        u'AZ': u'W',
        u'AR': u'SW',
        u'CA': u'W',
        u'CO': u'RM',
        u'CT': u'NA',
        u'DC': u'NC',
        u'DE': u'MA',
        u'FL': u'SE',
        u'GA': u'SE',
        u'GU': u'W', # Guam
        u'HI': u'W',
        u'ID': u'PNWA',
        u'IL': u'MW',
        u'IN': u'MW',
        u'IA': u'MW',
        u'KS': u'MW',
        u'KY': u'SE',
        u'LA': u'SW',
        u'ME': u'NA',
        u'MD': u'MA',
        u'MA': u'MA',
        u'MI': u'MW',
        u'MN': u'MW',
        u'MS': u'SE',
        u'MO': u'MW',
        u'MT': u'RM',
        u'NE': u'MW',
        u'NV': u'W',
        u'NH': u'NA',
        u'NJ': u'MA',
        u'NM': u'SW',
        u'NY': u'NA',
        u'NC': u'SE',
        u'ND': u'RM',
        u'OH': u'MW',
        u'OK': u'SW',
        u'OR': u'PNWA',
        u'PA': u'MA',
        u'PR': u'W', # TODO(bskari|2012-12-22) I don't know if this is the right region for Puerto Rico
        u'RI': u'NA',
        u'SC': u'SE',
        u'SD': u'RM',
        u'TN': u'SE',
        u'TX': u'SW',
        u'UT': u'RM',
        u'VI': u'W', # TODO(bskari|2012-12-22) I don't know if this is the right region for the Virgin Islands
        u'VT': u'NA',
        u'VA': u'MA',
        u'WA': u'PNWA',
        u'WV': u'MA',
        u'WI': u'MW',
        u'WY': u'RM',
    }
    if mapping.has_key(state):
        return mapping[state]
    abbreviations = session.query(
        State.abbreviation
    ).filter(
        State.name == state
    ).all()
    if len(abbreviations) == 1 and mapping.has_key(abbreviations[0].abbreviation):
        return mapping[abbreviations[0].abbreviation]
    logger.warning(
        u"Couldn't find region for state {state}".format(
            state=state,
        )
    )
    return None


def guess_park_type(park_name):
    best_match = (u'', u'')
    for abbreviation, type in get_park_types().iteritems():
        if type in park_name and len(best_match[1]) < len(type):
            best_match = (abbreviation, type)

    if not best_match[0]:
        if u'Park' in park_name:
            return u'NP'
        if u'Site' in park_name or u'Fort' in park_name:
            return u'NHS'
        if u'River' in park_name:
            return u'NR'
        if u'Memorial' in park_name:
            return u'N MEM'
        # Dont just check for 'Monument' because 'National Monument and Preserve'
        # is a separate type
        if u'Volcanic Monument' in park_name:
            return 'NM'
        if 'Washington Monument' in park_name:
            return 'NM'

    if best_match[0] == '':
        return None
    else:
        return best_match[0]


def load_states(filename=None):
    filename = filename or u'parks/scripts/initialize_db/state_table.csv'
    reader = csv.reader(open(filename, u'rb'), quotechar='"')
    StateTuple = namedtuple(u'StateTuple', [u'name', u'abbreviation', u'type'])
    # First row is just headers so skip it
    reader.next()
    states = [
        # statetable.com has spaces after most Canadian provinces, so strip
        StateTuple(name=name.strip(), abbreviation=abbreviation, type=type)
        for _, name, abbreviation, _, type, _, _, occupied, _ in reader
        if occupied != u'unoccupied' # Skip unoccupied areas, like islands
    ]
    # Add some that aren't included by statetable.com
    # These are in the list, but they're listed separately as islands, and the
    # Pacific Remote Islands Marine National Monument spans multiple islands
    # anyway, so just lump them together
    states.append(
        StateTuple(
            name=u'U.S. Minor Outlying Islands',
            abbreviation=u'MOI',
            type=u'minor outlying islands',
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


def format_park_tuples(wiki_list, master_list_stamp_entries):
    """Returns a list of ParkTuples with data loaded from the master list and
    Wikipedia.
    """
    # We want to have data for as many of the entries from the master list
    # as possible
    names_from_wiki = set([p.name for p in wiki_list])
    wiki_dict = dict([(p.name, p) for p in wiki_list])
    park_list = []
    unique_park_list = set()
    for entry in master_list_stamp_entries:
        if entry.park not in unique_park_list:
            unique_park_list.add(entry.park)
            if entry.park in names_from_wiki:
                state = entry.state
                if wiki_dict[entry.park].state is not None and wiki_dict[entry.park].state != entry.state:
                    # Go with the wiki, because... Yellowstone's in Wyoming,
                    # not Montana!
                    state = wiki_dict[entry.park].state
                    logger.warning(
                        u'State disagrees for {name}, choosing {state}'.format(
                            name=entry.park,
                            state=state,
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
                logger.warning(u'No wiki entry for {name}'.format(name=entry.park))
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
        url = re.sub(u"'", u'', url)
        def strip_accents(unicode):
            return u''.join([
                c for c in unicodedata.normalize(u'NFD', unicode)
                if unicodedata.category(c) != u'Mn'
            ])
        url = strip_accents(url)
        # Don't include the UNICODE flag here, so that we remove all non-ASCII
        url = url.strip()
        url = re.sub(u'\\W', u'-', url)
        # Removing punctuation can cause duplicate dashes
        url = re.sub(u'-+', u'-', url)
        url = re.sub(u'-$', u'', url)
        url = re.sub(u'^-', u'', url)
        url = re.sub(u"'", u'', url)
        return url

    def stripped_url_from_name(name):
        url = normalized_url_from_name(name)
        # Drop the "National Park", etc.
        url = re.sub(u'national.*', u'', url)
        url = re.sub(u'memorial.*', u'', url)
        url = re.sub(u'park.*', u'', url)
        url = url.strip()
        url = re.sub(u'-$', u'', url)
        url = re.sub(u'^-', u'', url)
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

    for park in parks:
        park_type = guess_park_type(park.name)

        if park_type is None:
            logger.warning(
                u'Unknown park type for {park}'.format(park=park.name)
            )
        state = park.state

        url = stripped_url_from_name(park.name)
        # Some things start with the word "National", like
        # "National Constitution Center"
        need_full_name_for_url = False
        for i in (u'National', u'International'):
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
                re.search(u'washington.*d.*c', state.lower()) or \
                re.search(u'district.*of.*columbia', state.lower())
            ):
                state = u'Washington DC'
            # US Virgin Islands, US Minor Outlying Islands, etc. => U.S.
            state = state.replace(u'US', u'U.S.')
            if u'Virgin' in state:
                state = u'U.S. Virgin Islands'

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


def save_stamps(session, stamp_texts):
    """Creates Stamp entries in the database."""
    for text in set(stamp_texts):
        stamp = Stamp(text=text, type='normal', status='active')
        session.add(stamp)


def save_stamp_locations(session, stamp_info_entries):
    """Creates StampLocation entries in the database."""
    # I'm not sure about the legality of directly copying the address
    # information, so just create dummy entries for now
    park_id_objects = session.query(Park.id, Park.latitude, Park.longitude).all()
    for park_id_object in park_id_objects:
        stamp_location = StampLocation(
            park_id=park_id_object.id,
            address='Uncategorized',
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
    logger = DumbLogger(u'initializedb.log')

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, u'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

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
    with open(u'parks/scripts/initialize_db/master_list.csv', u'rb') as f:
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
            username=u'guest',
            password=u'password',
            signup_ip=1,
        )
        DBSession.add(user)
