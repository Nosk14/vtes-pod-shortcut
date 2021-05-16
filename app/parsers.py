from html.parser import HTMLParser
from multiprocessing import Pool
import logging
import requests
import csv


BLOODLIBRARY_ENDPOINT = "https://api.bloodlibrary.info/api/search/?name={0}"
BLOODLIBRARY_CRYPT = "https://api.bloodlibrary.info/api/crypt/{0}"
BLOODLIBRARY_LIBRARY = "https://api.bloodlibrary.info/api/library/{0}"


class DriveThruCards:

    WEB_URL = "https://www.drivethrucards.com/browse/pub/12056/Black-Chantry-Productions/subcategory/30619_34256/VTES-Legacy-Card-Singles?sort=4a&pfrom=0.35&pto=0.35&page={0}"

    def __init__(self):
        pass

    def get_cards(self):
        raw_cards = self.__get_cards_from_web()
        cards = DriveThruCards.__parse_raw_cards(raw_cards)
        return sorted(cards, key=lambda item: item['id'])

    def __get_cards_from_web(self):
        raw_cards = []
        for page in range(1, 11):
            html = self.__get_html(DriveThruCards.WEB_URL.format(page))
            parser = DriveThruParser()
            parser.feed(html)
            raw_cards.extend(parser.cards)
        return raw_cards

    def __get_html(self, url):
        rs = requests.get(url, headers={'User-Agent': "Mozilla/5.0"})
        return rs.text

    @staticmethod
    def get_card_data(card_name):
        rs = requests.get(BLOODLIBRARY_ENDPOINT.format(card_name))
        basic_data = rs.json()[0]
        card_id = basic_data['id']
        if card_id[0] == '1':
            full_data = requests.get(BLOODLIBRARY_LIBRARY.format(card_id))
        else:
            full_data = requests.get(BLOODLIBRARY_CRYPT.format(card_id))

        return full_data.json()

    @staticmethod
    def parse_raw_card(raw_card):
        raw_name = raw_card['name'].split("-", 1)[1].rsplit("-", 1)[0]
        link = raw_card['link'].rsplit('?')[0].rsplit('/', 1)[0]
        card_data = DriveThruCards.get_card_data(raw_name)

        return {
            'name': card_data['name'],
            'id': card_data['id'],
            'link': link,
            'type': card_data['card_type'].split("/"),
            'clan': card_data['clan'].split("/")
        }

    @staticmethod
    def __parse_raw_cards(raw_cards):
        pool = Pool(16)
        results = pool.map(DriveThruCards.parse_raw_card, raw_cards)
        pool.close()
        pool.join()

        return results  # return [self.__parse_raw_card(c) for c in raw_cards]


class DriveThruParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.cards = []
        self.__is_parsing_card = False
        self.__card_link = None
        self.__card_name = None

    def error(self, message):
        logging.error(message)

    def handle_starttag(self, tag, attrs):
        if tag == 'tr' and ('class', 'dtrpgListing-row') in attrs:
            self.__is_parsing_card = True
        elif self.__is_parsing_card:
            if tag == 'a' and self.__card_link is None:
                self.__card_link = list(filter(lambda att: att[0] == 'href', attrs))[0][1]
            elif tag == 'img' and self.__card_name is None:
                self.__card_name = list(filter(lambda att: att[0] == 'alt', attrs))[0][1]

    def handle_endtag(self, tag):
        if tag == 'tr' and self.__is_parsing_card:
            self.__is_parsing_card = False
            self.cards.append({'name': self.__card_name, 'link': self.__card_link})
            self.__card_name = None
            self.__card_link = None

    def handle_data(self, data):
        pass


if __name__ == '__main__':
    dtc = DriveThruCards()
    cards = dtc.get_cards()

    with open('resources/twda_usage.csv') as csvfile:
        next(csvfile)
        reader = csv.reader(csvfile, delimiter=',')
        card_usage = {row[0]: int(row[1]) for row in reader}

    for card in cards:
        card['twda'] = card_usage[card['id']] if card['id'] in card_usage else 0

    with open('resources/data.js', 'w') as f:
        f.write("var cards = [")
        for card in cards:
            f.write(f"""
            {{
              "name":"{card['name']}",
              "id":"{card['id']}",
              "link":"{card['link']}",
              "type":{card['type']},
              "clan":{card['clan']},
              "twda":{card['twda']}
            }},
        """)
        f.write("];")

        print(set([str(card['clan']) for card in cards]))
        print(set([str(card['type']) for card in cards]))
