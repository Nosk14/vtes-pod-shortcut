import logging
from datetime import datetime

from flask import Flask, render_template

from parsers import DriveThruCards

UPDATE_INTERVAL = 30 * 24 * 60 * 60
app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

card_source = DriveThruCards()


def __get_cards():
    # return [
    #     {'name': 'Abyssal Hunter', 'id': '100014', 'img': 'https://vtes.dirtydevelopers.org/img/100014.jpg',
    #      'link': 'https://www.drivethrucards.com/product/339307/Library--Abyssal-Hunter--Ally?cPath=30619_34256'},
    #     {'name': 'Chair of Hades', 'id': '100318', 'img': 'https://vtes.dirtydevelopers.org/img/100318.jpg',
    #      'link': 'https://www.drivethrucards.com/product/339329/Library--Chair-of-Hades--Action?cPath=30619_34256'},
    #     {'name': 'Dead Hand', 'id': '100503', 'img': 'https://vtes.dirtydevelopers.org/img/100503.jpg',
    #      'link': 'https://www.drivethrucards.com/product/339347/Library--Dead-Hand--Combat?cPath=30619_34256'},
    #     {'name': "Deed the Heart's Desire", 'id': '100513', 'img': 'https://vtes.dirtydevelopers.org/img/100513.jpg',
    #      'link': 'https://www.drivethrucards.com/product/297318/Library--Deed-the-Hearts-Desire--Action-Modifier?cPath=30619_34256'},
    #     {'name': 'Descent into Darkness', 'id': '100528', 'img': 'https://vtes.dirtydevelopers.org/img/100528.jpg',
    #      'link': 'https://www.drivethrucards.com/product/339348/Library--Descent-into-Darkness--Action?cPath=30619_34256'},
    #     {'name': 'Giuseppe, Gravedigger', 'id': '100833', 'img': 'https://vtes.dirtydevelopers.org/img/100833.jpg',
    #      'link': 'https://www.drivethrucards.com/product/339375/Library--Giuseppe-Gravedigger--Retainer?cPath=30619_34256'}
    # ]
    return card_source.get_cards()


cards = __get_cards()
last_cards_update = datetime.now()


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
