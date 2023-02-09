# Импортируем необходимые компоненты
from glob import glob
from random import choice
import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode,\
    ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from utility import *
import nltk
nltk.download('stopwords')
import re

def start_message(bot, update):
    print('Кто-то отправил команду /start.')  # вывод сообщения в консоль при отправки команды /start
    bot.message.reply_text(f'Здравствуйте, {bot.message.chat.first_name}! Предлагаю к продаже участок с дом-баней гаражом и техэтажом под дом в элитном поселке.\n'
                           f'Есть все коммуникации. Прошу задавать вопросы по поселку, участку и любым элементам на участке.\n'
                           f'Чтобы увидеть фото какого-либо объекта/подобъекта достаточно написать - покажи ..., если чат-бот завис прошу набрать /start'
                           , reply_markup=get_keyboard())  # отправляем ответ

def grade_start(bot, update):
    bot.message.reply_text(
        'Какое у вас истинное имя?', reply_markup=ReplyKeyboardRemove())  # вопрос и убираем основную клавиатуру
    return "user_name"  # ключ для определения следующего шага

def grade_get_name(bot, update):
    update.user_data['name'] = bot.message.text  # временно сохраняем ответ
    bot.message.reply_text("Оцените чат-бот от 1 до 5")  # задаем вопрос
    reply_keyboard = [["1", "2", "3", "4", "5"]]  # создаем клавиатуру
    return "evaluation"   # ключ для определения следующего шага

def grade_get_evaluation(bot, update):
    update.user_data['evaluation'] = bot.message.text  # временно сохраняем ответ
    #reply_keyboard = [["1", "2", "3", "4", "5"]]  # создаем клавиатуру
    reply_keyboard = [["Пропустить"]]  # создаем клавиатуру
    bot.message.reply_text("Помогите сделать чат-бот лучше, напишите отзыв. Или нажмите кнопку пропустить этот шаг.",
                           reply_markup=ReplyKeyboardMarkup(
                               reply_keyboard, resize_keyboard=True, one_time_keyboard=True))  # клава исчезает
    return "comment"  # ключ для определения следующего шага

def grade_comment(bot, update):
    update.user_data['comment'] = bot.message.text  # временно сохраняем ответ
    text = """Результат опроса:
    <b>Имя:</b> {name}
    <b>Оценка:</b> {evaluation}
    <b>Комментарий:</b> {comment}
    """.format(**update.user_data)
    print(text)
    bot.message.reply_text(text, parse_mode=ParseMode.HTML)  # текстовое сообщение с форматированием HTML
    bot.message.reply_text("Спасибо вам за комментарий!", reply_markup=get_keyboard())  # сообщение и возвр. осн. клаву
    return ConversationHandler.END  # выходим из диалога

def grade_exit_comment(bot, update, db):
    update.user_data['comment'] = None
    text = """Результат опроса:
    <b>Имя:</b> {name}
    <b>Оценка:</b> {evaluation}""".format(**update.user_data)
    print(text)
    grade_data = update.user_data
    print(grade_data)
    db.create_post(grade_data)
    bot.message.reply_text(text, parse_mode=ParseMode.HTML)  # текстовое сообщение с форматированием HTML
    bot.message.reply_text("Спасибо!", reply_markup=get_keyboard())  # отправляем сообщение и возвращаем осн. клаву
    return ConversationHandler.END  # выходим из диалога

# функция отправляет случайную картинку
def send_photo(bot, update):
    lists = glob('images/*')  # создаем список из названий картинок
    picture = choice(lists)  # берем из списка одну картинку
    inl_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"оцените фото 👍", callback_data=1),
        InlineKeyboardButton(f"оцените фото 👎", callback_data=-1)
    ]])
    update.bot.send_photo(
        chat_id=bot.message.chat.id,
        photo=open(picture, 'rb'),
        reply_markup=inl_keyboard)  # отправляем картинку и inline клавиатуру

def inline_button_pressed(bot, update):
    print(bot.callback_query)
    query = bot.callback_query  # данные которые приходят после нажатия кнопки
    update.bot.edit_message_caption(
        caption='Спасибо вам за ваш выбор!',
        chat_id=query.message.chat.id,
        message_id=query.message.message_id)  # уберем inline клавиатуру выведем текст

# функция печатает и отвечает на полученный контакт
def get_contact(bot, update):
    print(bot.message.contact)
    bot.message.reply_text('{}, мы получили ваш номер телефона, обязательно перезвоним!'
                           .format(bot.message.chat.first_name))

def dontknow(bot, update):
    bot.message.reply_text("Пожалуйста, выберите правильную оценку на клавиатуре")

def currency_exchange(bot, update):
    USD_RUB = requests.get("https://api.coingate.com/v2/rates/merchant/USD/RUB")
    EUR_RUB = requests.get("https://api.coingate.com/v2/rates/merchant/EUR/RUB")
    bot.message.reply_text(f"Курс доллара: {USD_RUB.text}   Курс евро: {EUR_RUB.text}")

def preprocess_txt(line,morpher, sw, exclude):
    if line==None:
        return None
    else:
        line=re.sub(re.compile(r'[^\w\s]'), " ", line)
        line=re.sub(re.compile(r'[^a-zA-Zа-яА-Я0-9]'), " ", line)
        spls = "".join(i for i in line.strip() if i not in exclude).split()
        spls = [morpher.parse(i.lower())[0].normal_form for i in spls]
        spls = [i for i in spls if i not in sw and i != ""]
        #spls = [i for i in spls if i != ""]
        #return ' '.join(spls)
        return spls

def answer_text(bot, update):
    print(bot.message.text)  # печатаем на экран сообщение пользователя
    preprocess_text = preprocess_txt(bot.message.text, morpher, sw, exclude)
    bot.message.reply_text(preprocess_text)  # отправляем обратно текс который пользователь послал

def is_english(bot, update):
    return bot.message.reply_text("Извините, английскому языку я не обучен.")

def choice_data(question, morpher=morpher, sw=sw, exclude=exclude,
                morpher_qwest_tokens=morpher_qwest_tokens):
    spls = preprocess_txt(question, morpher, sw, exclude)
    cnt=0
    for i in spls:
        if i in morpher_qwest_tokens:
            cnt+=1
    question = ' '.join(spls)
    return cnt, question
