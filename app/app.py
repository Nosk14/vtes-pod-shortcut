import logging

from flask import Flask, render_template

from parsers import DriveThruCards

card_source = DriveThruCards()
cards = card_source.get_cards()

app = Flask(__name__)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


@app.route("/", methods=['GET'])
def cards_panel():
    global cards
    return render_template('cards_panel.html', cards=cards)


if __name__ == '__main__':
    app.run(port=8080)
