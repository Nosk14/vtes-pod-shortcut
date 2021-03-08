from html.parser import HTMLParser
import logging
import requests


BLOODLIBRARY_ENDPOINT = "https://api.bloodlibrary.info/api/search/?name={0}"


class DriveThruCards:

    WEB_URL = "https://www.drivethrucards.com/browse/pub/12056/Black-Chantry-Productions/subcategory/30619_34256/VTES-Legacy-Card-Singles?sort=4a&pfrom=0.35&pto=0.35&page={0}"

    def __init__(self):
        pass

    def get_cards(self):
        raw_cards = self.__get_cards_from_web()
        cards = self.__parse_raw_cards(raw_cards)
        return sorted(cards, key=lambda item: item['id'])

    def __get_cards_from_web(self):
        raw_cards = []
        for page in range(1, 10):
            html = self.__get_html(DriveThruCards.WEB_URL.format(page))
            parser = DriveThruParser()
            parser.feed(html)
            raw_cards.extend(parser.cards)
            break
        return raw_cards

    def __get_html(self, url):
        rs = requests.get(url, headers={'User-Agent': "Mozilla/5.0"})
        return rs.text

    def __parse_raw_cards(self, raw_cards):
        return [self.__parse_raw_card(c) for c in raw_cards]

    def __parse_raw_card(self, raw_card):
        raw_name = raw_card['name'].split("-", 1)[1].rsplit("-", 1)[0]
        rs = requests.get(BLOODLIBRARY_ENDPOINT.format(raw_name))
        card_data = rs.json()[0]
        link = raw_card['link'].rsplit('?')[0].rsplit('/', 1)[0]

        return {
            'name': card_data['name'],
            'id': card_data['id'],
            'img': card_data['image'],
            'link': link
        }


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