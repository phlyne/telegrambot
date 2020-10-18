import urllib.request
from datetime import datetime
import wikipedia
from telebot import types
from pyowm import OWM
import telebot


def date_check(dateinp):
    min_date = datetime(1992, 7, 1)
    max_date = datetime.today()

    return min_date <= dateinp <= max_date


bot = telebot.TeleBot("1235868231:AAH7bJMZmyOswO8xcXpJfu7URMQr8V8qCbA")


@bot.message_handler(commands=["currency"])
def currency(message):
    try:
        message_str = str(message.text.replace("/currency", ""))

        if len(message_str) >= 15:
            currency = message_str[1:4].upper()
            date = datetime.strptime(message_str[5:15], "%Y-%m-%d")

            if date_check(date):
                date = datetime.strftime(date, "%d/%m/%Y")
                url = "http://www.cbr.ru/scripts/XML_daily.asp?date_req=" + date
                html = str(urllib.request.urlopen(url).read())
                if currency in html:
                    bot.send_message(message.chat.id,
                                     f"Курс рубля к {currency} на {date}: {html[html.find('Value', html.find(currency)) + 6:html.find(',', html.find(currency)) + 5].replace(',', '.')}")
                else:
                    bot.send_message(message.chat.id, "no such currency in data")
            else:
                bot.send_message(message.chat.id, "wrong date format")
        else:
            bot.send_message(message.chat.id, "wrong input with '/currency'")
    except:
        bot.send_message(message.chat.id, "amm, something go wrong, try again in correct input format")


@bot.message_handler(commands=["wiki"])
def wiki(message):

    wikipedia.set_lang(message.from_user.language_code)

    try:
        bot.send_message(message.chat.id, wikipedia.summary(message.text[6:], sentences=2))
    except BaseException:
        bot.send_message(message.chat.id, "amm, wheres request")


@bot.message_handler(commands=["horoscope"])
def horoscope(message):
    keyboard = types.InlineKeyboardMarkup()

    key_aries = types.InlineKeyboardButton(text='Овен', callback_data='/?znak=aries')
    keyboard.add(key_aries)

    key_taurus = types.InlineKeyboardButton(text='Телец', callback_data='/?znak=taurus')
    keyboard.add(key_taurus)

    key_gemini = types.InlineKeyboardButton(text='Близнецы', callback_data='/?znak=gemini')
    keyboard.add(key_gemini)

    key_cancer = types.InlineKeyboardButton(text='Рак', callback_data='/?znak=cancer')
    keyboard.add(key_cancer)

    key_leo = types.InlineKeyboardButton(text='Лев', callback_data='/?znak=leo')
    keyboard.add(key_leo)

    key_virgo = types.InlineKeyboardButton(text='Дева', callback_data='/?znak=virgo')
    keyboard.add(key_virgo)

    key_libra = types.InlineKeyboardButton(text='Весы', callback_data='/?znak=libra')
    keyboard.add(key_libra)

    key_scorpio = types.InlineKeyboardButton(text='Скорпион', callback_data='/?znak=scorpio')
    keyboard.add(key_scorpio)

    key_sagittarius = types.InlineKeyboardButton(text='Стрелец', callback_data='/?znak=sagittarius')
    keyboard.add(key_sagittarius)

    key_capricorn = types.InlineKeyboardButton(text='Козерог', callback_data='/?znak=capricorn')
    keyboard.add(key_capricorn)

    key_aquarius = types.InlineKeyboardButton(text='Водолей', callback_data='/?znak=aquarius')
    keyboard.add(key_aquarius)

    key_pisces = types.InlineKeyboardButton(text='Рыба', callback_data='/?znak=pisces')
    keyboard.add(key_pisces)

    bot.send_message(message.from_user.id, text='choose your zodiac sign', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_horoscope(callback):
    if callback.data[:6] == "/?znak":
        url = "https://1001goroskop.ru" + callback.data
        html = urllib.request.urlopen(url).read().decode(encoding='cp1251')
        bot.send_message(callback.message.chat.id, html[html.find('<div itemprop="description">') + 31:html.find("<", html.find('<div itemprop="description">') + 31)])
    else:
        pass


@bot.message_handler(commands=["weatherme"])
def weather_me(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_geo = types.KeyboardButton(text="Send location", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Send me your location for this function", reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        owm = OWM("64bb872cc3a41a75c241d41959081523")
        mgr = owm.weather_manager()
        data = mgr.one_call(lat=message.location.latitude, lon=message.location.longitude)
        bot.send_message(message.chat.id,
                            f"Temperature in your location for today: {data.current.temperature('celsius').get('temp')}°C, "
                            f"feels like: {data.current.temperature('celsius').get('feels_like')}°C. "
                            f"Pressure for today: {data.current.pressure.get('press')} hPa. "
                            f"Clouds: {data.current.clouds}%. "
                            f"Humidity: {data.current.humidity}%. "
                            f"Wind speed: {data.current.wind().get('speed')} m/s", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["weather"])
def weather(message):
    try:
        location = str(message.text.replace("/weather", "").split()[0])
        owm = OWM("64bb872cc3a41a75c241d41959081523")
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(location)
        weather = observation.weather

        bot.send_message(message.chat.id, f"Temperature in {location} for today: {weather.temperature('celsius').get('temp')}°C, "
                                              f"feels like: {weather.temperature('celsius').get('feels_like')}°C. "
                                              f"Pressure for today: {weather.pressure.get('press')} hPa. "
                                              f"Clouds: {weather.clouds}%. "
                                              f"Humidity: {weather.humidity}%. "
                                              f"Wind speed: {weather.wind().get('speed')} m/s")

    except:

        bot.send_message(message.chat.id, "ehm something go wrong, try again with correct format")


@bot.message_handler(commands=["quadratic_eq"])
def quadratic_equation(message):
    try:
        odds = [int(i) for i in message.text.replace("/quadratic_eq ", "").split(" ")]
        discriminant = odds[1] ** 2 - 4 * odds[0] * odds[2]

        if discriminant > 0:
            bot.send_message(message.chat.id, f"x1 = {(-odds[1] + discriminant ** 0.5) / (2 * odds[0])} "
                                              f"x2 = {(-odds[1] - discriminant ** 0.5) / (2 * odds[0])}")

        elif discriminant == 0:
            bot.send_message(message.chat.id, f"x = {-odds[1] / (2 * odds[0])}")

        else:
            bot.send_message(message.chat.id, "no roots of the equation")

    except TypeError:
        bot.send_message(message.chat.id, "what is this arguments? letters O.o")

    except IndexError:
        if len(odds) == 2:
            bot.send_message(message.chat.id, f"x1 = {-odds[1] / odds[0]} "
                                              f"x2 = 0")
        else:
            bot.send_message(message.chat.id, "too much arguments")
    except ValueError:
        bot.send_message(message.chat.id, "amm, wheres args")


@bot.message_handler(commands=["from_numeral_system"])
def from_numeral_system(message):
    try:
        num_base = message.text.replace("/from_numeral_system ", "").split()
        bot.send_message(message.chat.id, int(num_base[0], base=int(num_base[1])))

    except IndexError:
        bot.send_message(message.chat.id, "you need to enter number and base!")

    except ValueError:
        bot.send_message(message.chat.id, "base should be integer number!")


@bot.message_handler(func=lambda message: True)
def random_message(message):
    bot.send_message(message.chat.id, "wrong command")


bot.polling(none_stop=True, interval=0)
