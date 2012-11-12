from BeautifulSoup import BeautifulSoup
import csv
import logging
from collections import namedtuple
import os
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
from parks.models import State
from parks.models import User
from parks.models import UserEmail


console = logging.StreamHandler()
console.setLevel(logging.ERROR)
logging.getLogger('').addHandler(console)

# Each row has a tuple of (park, stamp, address)
rows = []
parks = set()
park_set = set()
stamps = set()
addresses = set()
states = []


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def remove_whitespace(s):
    return s.replace('\t', ' ').replace('  ', ' ')


def remove_newlines(s):
    return s.replace('\n', ' ').replace('  ', ' ')


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def save_page_to_file(soup, filename=None):
    """For debugging, so I'm not hitting Wikipedia constantly."""
    filename = filename or 'parks/scripts/initialize_db/wiki.txt'
    f = file(filename, 'w')
    f.write(str(soup))
    f.close()


def load_soup(url=None):
    # Load the page from the file if we've hit it before
    try:
        f = open('parks/scripts/initialize_db/wiki.txt')
        soup = BeautifulSoup(f.read())
    except:
        soup = load_page_from_url(url)
        save_page_to_file(soup, 'parks/scripts/initialize_db/wiki.txt')

    return soup


def load_page_from_url(url=None):
    url = url or 'http://en.wikipedia.org/wiki/List_of_areas_in_the_United_States_National_Park_System'
    user_agent = 'Mozilla/5 (Solaris 10) Gecko'
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(request)

    soup = BeautifulSoup(response.read())
    return soup


def get_td_text(td):
    if td and td.find('a') and td.a.has_key('title'):
        # Just return the first state
        return td.a['title']
    else:
        # I don't expect this to happen - just about everything has links
        logging.warning(u'No link in {td}\n'.format(td=td))


def add_park_entry(park_name, state_name):
    # Well, I'd rather have special cases in code then have to do them by
    # hand, so at the very least they automatically get filled in when I
    # run this batch
    if u'Yellowstone' in park_name:
        state_name = u'Wyoming'

    if park_name and state_name:
        entry = u'"{park}","{state}","{region}"'.format(
            park=park_name,
            state=state_name,
            region=get_region_from_state(state_name),
        )

        if park_name not in parks:
            park_set.add(entry)
            parks.add(park_name)
        elif entry not in park_set:
            logging.error(
                u'{entry} already added but has a different state or region\n'.format(
                    entry=entry
                )
            )
            # List the duplicate matching entries
            for i in park_set:
                if park_name in i:
                    logging.error(u'\tEntry: {entry}\n'.format(entry=i))
    else:
        logging.info(
            u'Skipping {park} {state}\n'.format(
                park=park_name,
                state=state_name,
            )
        )


def parse_list(park_list, state):
    state_name = get_td_text(state)
    links = park_list.fetch('a')
    # Well, I'd rather have special cases in code then have to do them by
    # hand, so at the very least they automatically get filled in when I
    # run this batch
    if u'National Capital Parks-East' in links[0]['title']:
        state_name = u'Maryland'

    for link in links:
        park_name = link['title']
        add_park_entry(park_name, state_name)


def load_tables(soup):
    tables = soup.fetch('table')
    # Some of the tables have disabled or future parks; skip them
    relevant_tables = (1, 3, 5, 6, 8, 11, 12, 13, 15, 16, 17, 20, 22, 23, 24, 25, 26, 27, 28, 30,)
    for i in relevant_tables:
        # Skip the table header
        trs = tables[i].fetch('tr')[1:]
        for tr in trs:
            tds = tr.fetch('td')
            park = (tds[0] if len(tds) > 0 else None)
            state = (tds[1] if len(tds) > 1 else None)

            # Some tables have lists of more stuff in them; parse those too
            if len(park.fetch('li')) > 0:
                parse_list(park, state)
                continue

            park_name = get_td_text(park)
            state_name = get_td_text(state)
            add_park_entry(park_name, state_name)


def add_extra_parks():
    """The wiki page doesn't include some parks, so add them manually."""
    add_park_entry('Western Arctic National Parklands', 'Alaska')


def load_rows(csv_reader):
    c = {'update': 0, 'park': 1, 'stamp': 2, 'address': 3, 'last_seen': 4, 'confirmed_by': 5, 'comment': 6}

    # There were misspellings of bonus, so use this to find them
    bonus_re = re.compile(r'bonus|bonue|bpnus', re.IGNORECASE)
    # Stampers have their own custom stamps; skip them
    stamper_re = re.compile(r'stamp|stanp', re.IGNORECASE)

    lost_stamps = False
    current_park = None

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
                logging.warning('Skipping {stamp}\n'.format(stamp=stamp.replace('\n', ';')))
                continue

            rows.append((current_park, stamp, address))
            parks.add(current_park)
            stamps.add(stamp)
            addresses.add(address)


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
    return [
        # statetable.com has spaces after most Canadian provinces, so strip
        StateTuple(name=name.strip(), abbreviation=abbreviation, type=type)
        for _, name, abbreviation, _, type, _, _, occupied, _ in reader
        if occupied != 'unoccupied' # Skip unoccupied areas, like islands
    ]


def save_states(states, session):
    for state in states:
        state = State(
            name=state.name,
            abbreviation=state.abbreviation,
            type=state.type,
        )
        session.add(state)


def save_parks(session):
    sorted_list = list(park_set)
    sorted_list.sort()

    for string in sorted_list:
        park_name = string.split('"')[1]
        park_state = string.split('"')[3]
        park_region = string.split('"')[5]
        park_type = guess_park_type(park_name)

        if not park_type:
            logging.error(
                'Unknown park type for {park}\n'.format(park=park_name)
            )

        # Replace spaces with dashes, drop the "National Park", etc.
        url = park_name.lower()
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

        # Wikipedia sometimes has disambiguation crap, so remove it
        park_state = re.sub(u' \\(U\\.S\\. state\\)', u'', park_state)
        park_state = park_state.strip()

        # Normalize to statetable.com's naming convention
        if (
            re.search(u'washington.*d.*c', park_state.lower()) or \
            re.search(u'district.*of.*columbia', park_state.lower())
        ):
            park_state = u'Washington DC'

        park = Park(
            name=park_name,
            url=url,
            type=park_type,
            region=park_region,
            state=park_state,
        )

        session.add(park)


def save_stamps(session):
    unique_stamp_text = set([stamp_text for _, stamp_text, _ in rows])
    for stamp_text in unique_stamp_text:
        stamp = Stamp(text=stamp_text)
        session.add(stamp)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    # Load data for parks
    parks_soup = load_soup()
    load_tables(parks_soup)
    add_extra_parks()

    with transaction.manager:
        states = load_states()
        save_states(states, DBSession)
        save_parks(DBSession)
