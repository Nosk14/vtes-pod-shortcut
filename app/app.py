import logging
import csv
from flask import Flask, render_template, request
from parsers import DriveThruCards

app = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

app.logger.info("Getting cards...")
card_source = DriveThruCards()
cards = card_source.get_cards()
app.logger.info("Ready!")

app.logger.info("Parsing CSV...")
with open('resources/twda_usage.csv') as csvfile:
    next(csvfile)
    reader = csv.reader(csvfile, delimiter=',')
    card_usage = {row[0]: int(row[1]) for row in reader}
app.logger.info("Ready!")


def add_missing_cards():
    global cards
    global card_usage
    for card in cards:
        if card['id'] not in card_usage:
            app.logger.info("Card missing:" + card['id'])
            card_usage[card['id']] = 0


add_missing_cards()


@app.route("/", methods=['GET'])
def cards_panel():
    sorting_method = request.args.get('sort', None)
    global cards
    global card_usage
    local_cards = cards[:]

    if sorting_method == 'twda':
        local_cards.sort(key=lambda c: card_usage[c['id']])

    return render_template('cards_panel.html', cards=local_cards)


if __name__ == '__main__':
    app.run(port=8080)
