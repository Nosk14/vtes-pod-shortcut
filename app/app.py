import logging
from datetime import datetime

from flask import Flask, render_template

from parsers import DriveThruCards

UPDATE_INTERVAL = 30 * 24 * 60 * 60

card_source = DriveThruCards()


def __get_cards():
    return card_source.get_cards()


cards = __get_cards()
last_cards_update = datetime.now()


app = Flask(__name__)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


@app.route("/", methods=['GET'])
def cards_panel():
    global last_cards_update
    global cards
    time_since_last_update = last_cards_update - datetime.now()
    if time_since_last_update.total_seconds() > UPDATE_INTERVAL:
        cards = __get_cards()
        last_cards_update = datetime.now()

    return render_template('cards_panel.html', cards=cards)


if __name__ == '__main__':
    app.run(port=8080)
