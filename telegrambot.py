from datetime import datetime
import wikipedia
from telebot import types
from pyowm import OWM
import time
import telebot
import json
import requests
import re

bot = telebot.TeleBot("1235868231:AAH7bJMZmyOswO8xcXpJfu7URMQr8V8qCbA")


def dict_load(path, thread):
    with open(path, "w") as f:
        json.dump(thread, f)


def dict_get(path):
    with open(path) as f:
        thread = json.load(f)
    return thread


def date_check(dateinp):
    min_date = datetime(1992, 7, 1)
    max_date = datetime.today()

    return min_date <= dateinp <= max_date


def get_key(dic, value):
    lst = list()
    for k, v in dic.items():
        if v[0] == value:
            lst.append(k)
    return lst


def parse_html(html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleanhtml = re.sub(cleanr, '', html["threads"][0]["comment"])
    photo = html["threads"][0]["files"][0]["path"]
    return cleanhtml, photo


@bot.message_handler(commands=["currency"])
def currency(message):
    try:
        message_str = str(message.text.replace("/currency", ""))

        if len(message_str) >= 15:
            currency = message_str[1:4].upper()
            date = datetime.strptime(message_str[5:15], "%Y-%m-%d")

            if date_check(date):
                date = datetime.strftime(date, "%d/%m/%Y")
                html = requests.get("http://www.cbr.ru/scripts/XML_daily.asp?date_req=" + date).text
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
    text_splitted = message.text.split()
    del text_splitted[0]

    if text_splitted[-1] in wikipedia.languages():
        language_code = text_splitted[-1]
        del text_splitted[-1]
    else:
        language_code = "en"

    wikipedia.set_lang(language_code)

    request = " ".join(text_splitted)

    bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        bot.send_message(message.chat.id, wikipedia.summary(request, sentences=2))
    except BaseException:
        bot.send_message(message.chat.id, "amm, something goes wrong")


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
        html = requests.get("https://1001goroskop.ru" + callback.data).text
        bot.send_message(callback.message.chat.id, html[html.find('<div itemprop="description">') + 31:html.find("<",
                                                                                                                 html.find(
                                                                                                                     '<div itemprop="description">') + 31)])
    else:
        pass


@bot.message_handler(commands=["weatherme"])
def weather_me(message):
    try:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        button_geo = types.KeyboardButton(text="Send location", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id, "Send me your location for this function", reply_markup=keyboard)
    except:
        bot.send_message(message.chat.id, "something go wrong, try again")


@bot.message_handler(content_types=["location"])
def location(message):
    try:
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
                             f"Wind speed: {data.current.wind().get('speed')} m/s",
                             reply_markup=types.ReplyKeyboardRemove())
    except:
        bot.send_message(message.chat.id, "something go wrong, try again")


@bot.message_handler(commands=["weather"])
def weather(message):
    try:
        location = str(message.text.replace("/weather", "").split()[0])
        owm = OWM("64bb872cc3a41a75c241d41959081523")
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(location)
        weather = observation.weather

        bot.send_message(message.chat.id,
                         f"Temperature in {location} for today: {weather.temperature('celsius').get('temp')}°C, "
                         f"feels like: {weather.temperature('celsius').get('feels_like')}°C. "
                         f"Pressure for today: {weather.pressure.get('press')} hPa. "
                         f"Clouds: {weather.clouds}%. "
                         f"Humidity: {weather.humidity}%. "
                         f"Wind speed: {weather.wind().get('speed')} m/s")

    except:

        bot.send_message(message.chat.id, "ehm something go wrong, try again with correct format")


@bot.message_handler(commands=["sub2ch"])
def two_chan_sub(message):
    try:
        threads_message = message.text[7:].split()
        thread = {}
        thread_list_check = True
        threads_list = "d b o soc media r rf int po news hry au bi biz bo c em fa fiz fl ftb hh hi me mg mlp mo mov mu " \
                       "ne psy re sci sf sn sp spc tv un w tes v vg wr a fd ja ma vn" \
                       "wh wm wp zog de di diy mus pa p wrk trv gd hw mobi pr ra s t web bg cg gsg ruvn"

        for i in threads_message:
            if i in threads_list:
                thread_in_for = {i: [True, None]}
                thread.update(thread_in_for)
            elif thread_list_check:
                bot.send_message(message.chat.id, "some sections has wrong format, sections that was entered correctly are added")
        thread_main = dict_get("F:/telebot/user_data.json")
        try:
            thread_main[str(message.chat.id)]["threads"].update(thread)
        except:
            thread_id = {str(message.chat.id): {"threads": {}}}
            thread_main.update(thread_id)
            thread_main[str(message.chat.id)]["threads"].update(thread)

        try:
            thread_main[str(message.chat.id)]["checks"]

        except KeyError:
            thread_checks = {"checks": {"check_running": False, "two_chan_wait": 600}}
            thread_main[str(message.chat.id)].update(thread_checks)

        dict_load("F:/telebot/user_data.json", thread_main)

    except:
        bot.send_message(message.chat.id, "wrong sections name")


@bot.message_handler(commands=["unsub2ch"])
def two_chan_unsub(message):
    try:
        threads_message = message.text[9:].split()
        thread = dict_get("F:/telebot/user_data.json")

        for i in threads_message:
            del thread[str(message.chat.id)]["threads"][i]

        dict_load("F:/telebot/user_data.json", thread)

    except:
        bot.send_message(message.chat.id, "wrong sections name")


@bot.message_handler(commands=["start2ch"])
def two_chan_start(message):
    thread = dict_get("F:/telebot/user_data.json")
    thread[str(message.chat.id)]["checks"]["check_running"] = True
    dict_load("F:/telebot/user_data.json", thread)

    while thread[str(message.chat.id)]["checks"]["check_running"]:
        threads_true = get_key(thread[str(message.chat.id)]["threads"], True)

        for i in threads_true:
            html = json.loads(requests.get("https://2ch.hk/" + i + "/catalog_num.json").text)

            if thread[str(message.chat.id)]["threads"][i][1] != html["threads"][0]["num"]:
                answer, photo = parse_html(html)
                thread[str(message.chat.id)]["threads"][i][1] = html["threads"][0]["num"]

                if not html["threads"][0]["comment"] == "":
                    bot.send_message(message.chat.id, answer)
                else:
                    bot.send_message(message.chat.id, "no text in thread")

                try:
                    bot.send_photo(message.chat.id, requests.get("https://2ch.hk" + photo).content)
                except telebot.apihelper.ApiTelegramException:
                    try:
                        bot.send_video(message.chat.id, requests.get("https://2ch.hk" + photo).content)
                    except telebot.apihelper.ApiTelegramException:
                        pass
        dict_load("F:/telebot/user_data.json", thread)
        time.sleep(thread[str(message.chat.id)]["checks"]["two_chan_wait"])
        thread = dict_get("F:/telebot/user_data.json")


@bot.message_handler(commands=["cooldown2ch"])
def two_chan_cooldown(message):
    try:
        thread = dict_get("F:/telebot/user_data.json")
        thread[str(message.chat.id)]["checks"]["two_chan_wait"] = int(message.text[12:len(message.text)])
        dict_load("F:/telebot/user_data.json", thread)
    except ValueError:
        bot.send_message(message.chat.id, "argument must be integer number")
    except:
        bot.send_message(message.chat.id, "idk what did you entered")


@bot.message_handler(commands=["stop2ch"])
def two_chan_stop(message):
    thread = dict_get("F:/telebot/user_data.json")
    thread[str(message.chat.id)]["checks"]["check_running"] = False
    dict_load("F:/telebot/user_data.json", thread)


@bot.message_handler(commands=["help2ch"])
def two_chan_help(message):
    bot.send_message(message.chat.id, f"/sub2ch [thread1] [thread2] ... this command uses for subscribe on 2ch section "
                                      f"and then when you use /star2ch send to you newest thread every "
                                      f"[cooldown2ch] seconds example: /sub2ch a b (subs on a/ and b/)\n"
                                      f"/unsub2ch [thread1] [thread2] ... with this command you can unsubscribe from "
                                      f"2ch section example: /unsub2ch a b (unsubs from a/ and b/) \n"
                                      f"/start2ch command with no arguments, after you write this command bot will "
                                      f"send you newest thread every [coldown2ch] seconds example: /start2ch\n"
                                      f"/cooldown2ch [time in seconds] time intervals through which threads will"
                                      f"be sended to you example: /cooldown2ch 800 (will send thread every 800 secs)\n"
                                      f"/stop2ch stop sending thread without updating subscribed sections "
                                      f"example: /stop2ch")


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


bot.polling()
