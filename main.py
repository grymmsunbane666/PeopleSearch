from bs4 import BeautifulSoup as bs
import json
import requests
import sys
import time


class Soup:
    """Creates a soup object based on the given url.
       Accounts for bot detection and allows easy ways to extract html and json data."""

    def __init__(self, url, parse_type='lxml', headers=None, evasion_method=0):
        # HTML Parser
        self.parse_type = parse_type

        # Url
        self.url = url

        # Dictionary of headers if needed
        self.headers = headers

        # Soup Object (None by Default)
        self.soup = None

        # Bot Evasion Method Type
        self.evasion_method = evasion_method

        # Test all variables before running
        """if self.__test__():
            print('[*] Sending request to {}...'.format(self.url))
            self.run()"""

    def __test__(self):
        # Is the parse type provided a string?
        if not isinstance(self.parse_type, str):
            raise ValueError('Invalid Parse Type:: Must be a string.')

        # Is the header list a dictionary?
        if self.headers is not None and not isinstance(self.headers, dict):
            raise ValueError('Invalid Header:: Must be a dictionary of valid html request headers')

        # Is the evasion method provided as an integer?
        if self.evasion_method < 0 or self.evasion_method > 2:
            raise ValueError(
                'Invalid Evasion Method: Must be an integer between 0 and 2.\n\n::Evasion Methods::\n0 = NO bot detection\n\n1 = ONLY NOTIFY ME when bot detection is found\n\n2 = detect AND evade bot detection')

        # Is the url provided as a string?
        if not isinstance(self.url, str):
            raise ValueError('Invalid url: Must be a string')

        # If no errors have been raised then return True
        return True

    def test_soup(self):
        """Ensure that the soup object that has been created was created successfully"""
        try:
            test = self.soup.prettify()
            return True
        except AttributeError:
            print('[!] Invalid Soup: soup returned null')
            return False

    def bot_detection_test(self):
        """returns False if the url given has bot detection"""
        # Returns None for now until this function is completed
        return None

    def bypass_bot_detection(self):
        """attempts to bypass bot detection"""
        # Returns None for now until this function is completed
        return None

    def get_json(self, type_='application/ld+json'):
        """returns any json data found in the url"""
        return self.soup.find_all('script', {'type':type_})

    def get_html(self):
        """returns the prettified html retrieved from the url"""
        if self.test_soup():
            return self.soup.prettify()
        else:
            return None

    def setup_request(self):
        """create the request based on headers provided"""
        # Default Request
        request = requests.get(self.url).text

        # Bot Evasion Method 0: No Bot Evasion
        if self.evasion_method == 0:
            return request

        # Bot Evasion Method 1: Only Notify if "Bot Detection" is detected
        elif self.evasion_method == 1:
            if self.bot_detection_test():
                sys.stdout.write("[*] Bot Detection Suspected!!\n")
            return request

        # Bot Evasion Method 2: Attempt to bypass bot detection if it is found
        elif self.evasion_method == 2:
            if self.bot_detection_test():
                try:
                    test = self.bypass_bot_detection()
                    return test
                except Exception:
                    return request

    def run(self):
        """complete the request and create the soup object"""
        try:
            request = self.setup_request()
            self.soup = bs(request, self.parse_type)
            print('[*] Request to {} successful.'.format(self.url))
        except Exception as e:
            print('[!] Failed to complete request.')


class SearchQuery:
    def __init__(self, **queries):
        self.queries = queries
        self.query = self.compile()

    def get_query(self):
        return self.query

    def compile(self):
        query = ""
        sections = {}

        print("[*] Constructing Search Query...")

        for type_ in self.queries:
            if type_ == "city":
                city = self.queries.get(type_).split(' ')
                entry = ""
                for pos, word in enumerate(city):
                    if pos != len(city) - 1:
                        entry += "{}-".format(word.lower())
                    else:
                        entry += word.lower()
                sections["city"] = entry
            elif type_ == "name":
                name = self.queries.get(type_).split(' ')
                entry = ""
                for pos, word in enumerate(name):
                    if pos != len(name) - 1:
                        entry += "{}-".format(word.lower())
                    else:
                        entry += word.lower()
                sections["name"] = entry
            elif type_ == "state":
                sections["state"] = self.queries.get("state").lower()

        if "name" in sections and "city" in sections and "state" in sections:
            query += "{}_{}-{}".format(sections.get("name"), sections.get("city"), sections.get("state"))
        elif "name" in sections and "city" in sections and "state" not in sections:
            query += "{}_{}".format(sections.get("name"), sections.get("city"))
        elif "name" in sections and "state" in sections and "city" not in sections:
            query += "{}_{}".format(sections.get("name"), sections.get("state"))
        elif "name" in sections and "state" not in sections and "city" not in sections:
            query += sections.get("name")
        else:
            raise AttributeError("Invalid query input: Must provide a name as input (city and/or state OPTIONAL)")

        return query


def get_individual_data(soup_):
    scripts = soup_.soup.find_all('script')
    data = {}

    for script in scripts:
        if scripts.index(script) == 14:
            p2 = """{}""".format(str(script)[35:len(str(script)) - 9:])
            d = json.loads(p2)
            data["basic"] = d
        elif scripts.index(script) == 13:
            p2 = """{}""".format(str(script)[35:len(str(script)) - 11:])
            d = json.loads(p2)
            data["questions"] = d
    return data


def get_person_data(soup_, data_selection=0, default=False):
    """Gathers Person Data and returns it as a dictionary"""
    try:
        person_list = None
        for data in soup_.get_json()[data_selection]:
            person_list = json.loads(data)
        return person_list
    except json.decoder.JSONDecodeError as e:
        print("[!] Incorrect Data Format")
        return get_person_data(soup_, data_selection=6, default=True)
    except IndexError as e:
        if default:
            print("[!] Default Selection FAILED.....Exiting")
            return None
        else:
            print("[!] Incorrect JSON Item Selected : Attempting Default Selection")
            return get_person_data(soup_, data_selection=1, default=True)


def display_data(data, reload=False):
    print("[*] Preparing to display data...")
    try:
        if not reload:
            for person in data:
                dec_lines = int((100 - len(person.get("name"))) / 2)
                print("_" * 102)
                print("|{}{}{}|".format("_" * (dec_lines), person.get("name"), "_" * (dec_lines)))
                for info in person:
                    if info != "@content" and info != "@type" and info != "@id" and info != "@context":
                        print("   |_> {} :: {}".format(info, person.get(info)))
            print("_" * 102)
        else:
            for info in data:
                print(info, data.get(info))
    except TypeError:
        print("[!] FAILED TO PARSE DATA : Person Data returned None")
        print("[*] Returning html for inspection...")
        time.sleep(5)
        print(soup_.get_html())
    except AttributeError:
        display_data(data, reload=True)


if __name__ == '__main__':
    # Person Search Input
    name = "Kyle Ford"
    city = "Midwest City"
    state = "OK"

    # Build query and add it to the url
    query = SearchQuery(name=name, city=city, state=state)

    # To Enable Search Query, Uncomment this line
    url = 'https://www.fastpeoplesearch.com/name/{}'.format(query.get_query())

    # To Enable Individual Query, Uncomment this line
    #url = "https://www.fastpeoplesearch.com/kyle-ford_id_G4632180477220707958"

    print("[*] Sending Request to {}...".format(url))

    # Use the previously constructed url to build a soup object
    print("[*] Creating Soup Object...")
    soup_ = Soup(url)
    soup_.run()

    # Gather Search Data
    display_data(get_person_data(soup_, data_selection=2))

    """# Gather Individual Data
    d = get_individual_data(soup_)
    for info in d.get("basic"):
        print("{} : {}".format(info, d.get("basic")))
    for info in d.get("questions"):
        print("{} : {}".format(info, d.get("questions")))"""

