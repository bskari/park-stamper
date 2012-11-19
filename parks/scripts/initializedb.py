# -*- coding: utf-8 -*
from BeautifulSoup import BeautifulSoup
import csv
import datetime
import logging
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

from parks.models import DBSession
from parks.models import Base
from parks.models import get_park_types
from parks.models import Park
from parks.models import Stamp
from parks.models import StampCollection
from parks.models import StampLocation
from parks.models import State
from parks.models import User
from parks.models import UserEmail


logger = logging.getLogger('initializedb')
logger.setLevel(logging.WARNING)
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logger.addHandler(console)


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
    return s.replace('\t', ' ').replace('  ', ' ')


def remove_newlines(s):
    return s.replace('\n', ' ').replace('  ', ' ')


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
    with open(filename, 'w') as f:
        f.write(str(soup))


def load_page_from_file(filename):
    with open(filename, 'r') as f:
        soup = BeautifulSoup(f.read())
    return soup


def load_page_from_url(url):
    user_agent = 'Mozilla/5 (Solaris 10) Gecko'
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
    filename = ''.join(
        (
            'parks/scripts/initialize_db/',
            wiki_page_name,
            '.html',
        )
    )
    try:
        soup = load_page_from_file(filename)
    except:
        soup = load_page_from_url(
            ''.join(
                (
                    'http://en.wikipedia.org/wiki/',
                    wiki_page_name,
                )
            )
        )
        save_page_to_file(soup, filename)
    return soup


def get_national_parks():
    """Loads the list of national parks from Wikipedia."""
    soup = load_wiki_page('List_of_national_parks_of_the_United_States')
    tables = soup.fetch('table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    assert len(wikitables) == 1
    np_table = wikitables[0]
    trs = np_table.fetch('tr')

    parks = []

    # Skip the header row
    for tr in trs[1:]:
        # The name is in a th tag
        name = tr.fetch('th')[0].fetch('a')[0].text

        # The remaining columns are photo, location, date, area, description
        _, location_column, date_column, _, _ = tr.fetch('td')

        # The location column has one or more states and a GPS coordinate
        state_name = location_column.fetch('a')[0].text
        gps_text = location_column.fetch('a')[-1].text
        # gps_text looks like:
        # 44°21′N68°13′W / 44.35°N 68.21°W /44.35; -68.21 (Acadia)
        float_text = gps_text.split('/')[-1]
        latitude = float(float_text.split(';')[0])
        longitude = float(re.search(r'(-\d+\.\d+)', float_text).group())

        date = parse(date_column.fetch('span')[-1].text, fuzzy=True)

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
    soup = load_wiki_page('List_of_National_Monuments_of_the_United_States')
    tables = soup.fetch('table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    # There's an 'breakdown by agency' table and a list table
    assert len(wikitables) == 2
    nm_table = wikitables[1]
    trs = nm_table.fetch('tr')

    monuments = []

    # Skip the header row
    for tr in trs[1:]:
        # The columns are name, photo, agency, location, date, description
        name_column, _, agency_column, location_column, date_column, _ = tr.fetch('td')
        name = name_column.fetch('a')[0].text

        agency = agency_column.fetch('a')[0].text

        # The location column has one or more states and a GPS coordinate
        state_name = location_column.fetch('a')[0].text
        gps_text = location_column.fetch('a')[-1].text
        # gps_text looks like:
        # 44°21′N68°13′W / 44.35°N 68.21°W /44.35; -68.21 (Acadia)
        float_text = gps_text.split('/')[-1]
        try:
            latitude = float(float_text.split(';')[0])
            # There's some weird Unicode crap in the above, so I can't just split by ' '
            longitude = float(re.search(r'((?:-)?\d+(?:\.\d+)?)', float_text).group())
        except:
            latitude = longitude = None
            logger.warning(
                u'Skipping GPS {gps_text} for {monument}'.format(
                    gps_text=gps_text,
                    monument=name,
                )
            )

        date = parse(date_column.fetch('span')[-1].text, fuzzy=True)

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
    soup = load_wiki_page('List_of_United_States_national_lakeshores_and_seashores')
    tables = soup.fetch('table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    # There's a seashore table and a lakeshore table
    assert len(wikitables) == 2

    lakeshores = []
    seashores = []

    for table, list in zip(wikitables, (lakeshores, seashores)):
        trs = table.fetch('tr')
        # Skip the header row
        for tr in trs[1:]:
            # The columns are name, photo, location, date, area, description
            name_column, _, location_column, date_column, _, _ = tr.fetch('td')
            name = name_column.fetch('a')[0].text

            # The location column has one or more states and a GPS coordinate
            state_name = location_column.fetch('a')[0].text
            gps_text = location_column.fetch('a')[-1].text
            # gps_text looks like:
            # 44°21′N68°13′W / 44.35°N 68.21°W /44.35; -68.21 (Acadia)
            float_text = gps_text.split('/')[-1]
            latitude = float(float_text.split(';')[0])
            # There's some weird Unicode crap in the above, so I can't just split by ' '
            longitude = float(re.search(r'((?:-)?\d+(?:\.\d+)?)', float_text).group())

            date = parse(date_column.fetch('span')[-1].text, fuzzy=True)

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
    soup = load_wiki_page('United_States_National_Grassland')
    ul_lists = soup.fetch('ul')
    # There's a list for TOC, a list of national grasslands, a list of prairie
    # reserves, a list of "See also" stuff, and a ton of other crap
    grassland_list = ul_lists[1]

    grasslands = []

    for li in grassland_list.fetch('li'):
        # Most are formatted as follows:
        # Little Missouri National Grassland -- western North Dakota, blah blah...
        name = li.fetch('a')[0].text
        # Texas Panhandle => Texas
        state_name = li.fetch('a')[1].text.replace(' Panhandle', '')
        # Fannin County => Texas
        if state_name == 'Fannin County':
            state_name = 'Texas'

        grasslands.append(
            ParkTuple(
                name=name,
                state=state_name,
                agency='NFS',
                latitude=None,
                longitude=None,
                date=None,
            )
        )

    return grasslands


def get_national_marine_sanctuaries():
    """Loads the list of national marine sanctuaries from Wikipedia."""
    soup = load_wiki_page('United_States_National_Marine_Sanctuary')
    ul_lists = soup.fetch('ul')
    # There's a list of marine sanctuaries, and a ton of other crap
    sanctuary_list = ul_lists[0]

    sanctuaries = []

    for li in sanctuary_list.fetch('li'):
        name = li.fetch('a')[0].text
        # Wikipedia includes some national monuments here too
        if u'National Marine Sanctuary' not in name:
            logger.warning(
                u'Skipping {name} claiming to be a national marine anctuary'.format(
                    name=name,
                )
            )
            continue

        sanctuaries.append(
            ParkTuple(
                name=name,
                state=None,
                agency='NMSP', # National Marine Sanctuaries Program
                latitude=None,
                longitude=None,
                date=None,
            )
        )

    return sanctuaries 


def get_national_recreation_areas():
    """Loads the list of national recreation areas from Wikipedia."""
    # This doesn't have its own page
    soup = load_wiki_page('List_of_areas_in_the_United_States_National_Park_System')
    tables = soup.fetch('table')
    wikitables = [t for t in tables if u'wikitable' in t['class']]
    assert len(wikitables) == 32
    nra_table = wikitables[19]
    trs = nra_table.fetch('tr')

    areas = []

    # Skip the header row
    for tr in trs[1:]:
        # The columns are name, states
        name_column, state_column = tr.fetch('td')
        name = name_column.fetch('a')[0].text

        state_name = state_column.fetch('a')[0].text

        # TODO(bskari|2012-11-18) Load each NRA's Wiki page and scrape other
        # information

        areas.append(
            ParkTuple(
                name=name,
                state=state_name,
                latitude=None,
                longitude=None,
                agency='NPS',
                date=None,
            )
        )

    return areas


def guess_canonical_park(park_name, session):
    """Guesses the canonical name of the park as is stored in the database."""
    if not hasattr(guess_canonical_park, 'canonical_parks'):
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
        logging.warn(
            u"\n'{park}':'{trimmed_park}' guessed as\n'{canonical}':'{trimmed_canonical}'\n".format(
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
        r'\bHeritage\b',
        r'&', # No word boundary here; I was having trouble getting it to work
    )
    for regex in common_word_regexes:
        park_name = re.sub(regex, '', park_name)
    while u'  ' in park_name:
        park_name = park_name.replace(u'  ', u' ')
    park_name = park_name.strip()
    return park_name


def load_park_stamps_csv(csv_reader):
    """Loads the parks, stamps, and stamp location entries from the master list
    CSV. Returns an array of NamedTuples with park, stamp_text, and address.
    """
    c = {'update': 0, 'park': 1, 'stamp': 2, 'address': 3, 'last_seen': 4, 'confirmed_by': 5, 'comment': 6}

    # There were misspellings of bonus, so use this to find them
    bonus_re = re.compile(r'bonus|bonue|bpnus', re.IGNORECASE)
    # Stampers have their own custom stamps; skip them
    stamper_re = re.compile(r'stamp|stanp', re.IGNORECASE)

    lost_stamps = False
    current_park = None

    rows = []

    StampTuple = namedtuple('StampTuple', ['park', 'stamp_text', 'address'])

    for row in csv_reader:
        # The list toggles between retired and active stamps - ignore retired ones
        if 'LOST/STOLEN/RETIRED STAMPS' in row[c['park']]:
            lost_stamps = True
            continue
        # Good rows start with the name of a state in the park column
        elif lost_stamps and not row[c['update']] and row[c['park']] and not row[c['stamp']]:
            lost_stamps = False
            continue

        # The Excel document sometimes merged the park cells and had the same
        # listing for a few stamps in a row
        if row[c['park']]:
            current_park = remove_newlines(remove_whitespace(row[c['park']]))
            current_park = current_park.decode('utf-8')

        if current_park and row[c['stamp']]:
            stamp = remove_whitespace(row[c['stamp']])
            address = row[c['address']]
            address = address.decode('utf-8')

            # The Excel document sometimes would have trailing blank lines, remove them
            while len(stamp) > 0 and stamp[-1] == '\n':
                stamp = stamp[:-1]

            if (
                # Anything that doesn't have exactly 2 lines deserves a second look
                stamp.count('\n') != 1
                # Anything that says bonus, we ignore for now
                or bonus_re.search(stamp)
                # The stampers have their own custom ones; skip them
                or stamper_re.search(stamp) or stamper_re.search(current_park)
            ):
                logger.warning('Skipping {stamp}\n'.format(stamp=stamp.replace('\n', ';')))
                continue

            rows.append(StampTuple(current_park, stamp, address))

        return rows


def get_region_from_state(state):
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
        u'RI': u'NA',
        u'SC': u'SE',
        u'SD': u'RM',
        u'TN': u'SE',
        u'TX': u'SW',
        u'UT': u'RM',
        u'VT': u'NA',
        u'VA': u'MA',
        u'WA': u'PNWA',
        u'WV': u'MA',
        u'WI': u'MW',
        u'WY': u'RM',
    }
    if mapping.has_key(state):
        return mapping[state]
    return None


def guess_park_type(park_name):
    best_match = ('', '')
    for abbreviation, type in get_park_types().iteritems():
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
            return 'NM'

    return best_match[0]


def load_states(filename=None):
    filename = filename or 'parks/scripts/initialize_db/state_table.csv'
    reader = csv.reader(open(filename, 'rb'), quotechar='"')
    StateTuple = namedtuple('StateTuple', ['name', 'abbreviation', 'type'])
    # First row is just headers so skip it
    reader.next()
    states = [
        # statetable.com has spaces after most Canadian provinces, so strip
        StateTuple(name=name.strip(), abbreviation=abbreviation, type=type)
        for _, name, abbreviation, _, type, _, _, occupied, _ in reader
        if occupied != 'unoccupied' # Skip unoccupied areas, like islands
    ]
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


def save_parks(session, parks):
    for park in parks:
        park_type = guess_park_type(park.name)

        if park_type is None:
            logger.warning(
                'Unknown park type for {park}'.format(park=park.name)
            )
        if park.state is None:
            logger.error(
                'No state given for {park}'.format(park=park.name)
            )
            continue
        state = park.state

        # Replace spaces with dashes, drop the "National Park", etc.
        url = park.name.lower()
        need_full_name_for_url = False
        # Some things start with the word "National", like
        # "National COnstitution Center"
        for i in (u'national', u'international'):
            if url.startswith(i):
                need_full_name_for_url = True
                break
        # Some things are named the same thing but have different types, e.g.
        # Andrew Johnson National Cemetery and National Historic Site
        for duplicate in (
            u'andrew johnson',
            u'clara barton',
            u'colonial',
            u'fort vancouver',
            u'lewis and clark',
            u'martin luther king',
            u'shiloh',
            u'stones river',
            u'vicksburg',
        ):
            if duplicate in url:
                need_full_name_for_url = True
                break
        if not need_full_name_for_url:
            url = re.sub(u'national.*', u'', url)
            url = re.sub(u'memorial.*', u'', url)
            url = re.sub(u'park.*', u'', url)
        url = url.strip()
        url = re.sub(u"'", u'', url)
        def strip_accents(unicode):
            return ''.join([
                c for c in unicodedata.normalize('NFD', unicode)
                if unicodedata.category(c) != 'Mn'
            ])
        url = strip_accents(url)
        # Don't include the UNICODE flag here, so that we remove all non-ASCII
        url = re.sub(u'\\W', u'-', url)
        # Removing punctuation can cause duplicate dashes
        url = re.sub(u'-+', u'-', url)
        url = re.sub(u'-$', u'', url)
        url = re.sub(u'^-', u'', url)

        # Normalize to statetable.com's naming convention
        if (
            re.search(u'washington.*d.*c', state.lower()) or \
            re.search(u'district.*of.*columbia', state.lower())
        ):
            state = u'Washington DC'
        # US Virgin Islands, US Minor Outlying Islands, etc.
        state = state.replace('US ', 'U.S. ')

        try:
            park = Park(
                name=park.name,
                url=url,
                type=park_type,
                region=get_region_from_state(state),
                state=state,
            )
        except (IOError, Exception), e:
            print('******************' + park.state + ':' + str(e))
            continue

        session.add(park)


def save_stamps(session, stamp_texts):
    """Creates Stamp entries in the database."""
    assert len(stamp_texts) == len(set(stamp_texts))
    for text in stamp_texts:
        stamp = Stamp(text=text)
        session.add(stamp)


def save_stamp_locations(session, stamp_info_entries):
    """Creates StampLocation entries in the database."""
    for stamp_info in stamp_info_entries:
        guess_park = guess_canonical_park(stamp_info.park, session)
        stamp_location = StampLocation(park_id=guess_park.id, address=stamp_info.address)
        session.add(stamp_location)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    # Load the canonical park list from Wikipedia
    nps = get_national_parks()
    nms = get_national_monuments()
    lss, sss = get_national_lakeshores_and_seashores()
    gls = get_national_grasslands()
    nmss = get_national_marine_sanctuaries()
    nras = get_national_recreation_areas()

    # Load data for parks
    with open('parks/scripts/initialize_db/master_list.csv', 'rb') as f:
        reader = csv.reader(f, quotechar='"')
        stamp_info_entries = load_park_stamps_csv(reader)

    with transaction.manager:
        states = load_states()
        save_states(states, DBSession)
        for location_list in (nps, nms, lss, sss, gls, nmss, nras):
            save_parks(DBSession, location_list)
        save_stamp_locations(DBSession, stamp_info_entries)

        user = User(
            username='guest',
            password='password',
            signup_ip=1,
        )
        DBSession.add(user)
