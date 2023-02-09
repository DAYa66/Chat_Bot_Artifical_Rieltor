
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    ConversationHandler, CallbackQueryHandler
from settings import TG_TOKEN
from handlers import *
import logging
import annoy
import tensorflow as tf
from transformers import TFAutoModel, AutoTokenizer
import pickle
from database.db import Database


# дата и время, уровень важности, само сообщение
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

bert = TFAutoModel.from_pretrained("setu4993/LaBSE")
tokenizer = AutoTokenizer.from_pretrained("setu4993/LaBSE")

bert_index = annoy.AnnoyIndex(768, 'angular')
bert_index.load('./pickled_files/bert_index_planeta')

with open('./pickled_files/index_map_planeta.p', 'rb') as fp:
    index_map = pickle.load(fp)

bert_index_botalka = annoy.AnnoyIndex(768, 'angular')
bert_index_botalka.load('./pickled_files/bert_index_boltalka')

with open('./pickled_files/index_map_boltalka.p', 'rb') as fp:
    index_map_boltalka = pickle.load(fp)

def get_response(question, bert_index=bert_index, index_map=index_map):
    cnt, question = choice_data(question)
    if cnt > 0:
        tok = tokenizer(question, return_token_type_ids=False, return_tensors='tf')
        vector = bert(**tok)[1].numpy()[0]
        answer = bert_index.get_nns_by_vector(vector, 1, )[0]
        return index_map[answer]
    else:
        tok = tokenizer(question, return_token_type_ids=False, return_tensors='tf')
        vector = bert(**tok)[1].numpy()[0]
        answer_bolt = bert_index_botalka.get_nns_by_vector(vector, 1, )[0]
        return index_map_boltalka[answer_bolt]

def answer_text(bot, update):
    print(bot.message.text)  # печатаем на экран сообщение пользователя
    answer_text = get_response(bot.message.text)
    bot.message.reply_text(answer_text)  # отправляем обратно ответ

# Создаем ф-цию main, которая соединяется с  платформой Telegramm
def main():
    # создадим переменную my_bot, которая будет взаимодействовать с нашим ботом
    my_bot = Updater(TG_TOKEN, use_context=True)  # Токен API к Telegram
    logging.info('Start bot') # добавил свое информационное сообщение
    my_bot.dispatcher.add_handler(CommandHandler('start', start_message)) # когда нажмут команду /start CommandHandler вызывает ф-цию  sms
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex(r'[a-zA-Z]'), is_english)),
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex(CALLBACK_BUTTON_PICTURE), send_photo))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex(CALLBACK_BUTTON_START), start_message))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex(CALLBACK_CURRENCY_EXCHANGE), currency_exchange))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.contact, get_contact))
    my_bot.dispatcher.add_handler(CallbackQueryHandler(inline_button_pressed))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex(CALLBACK_BUTTON_PEN), grade_start)],
                            states={
                                "user_name": [MessageHandler(Filters.text, grade_get_name)],
                                "evaluation": [MessageHandler(Filters.regex('1|2|3|4|5'), grade_get_evaluation)],
                                "comment": [MessageHandler(Filters.regex('Пропустить'), grade_exit_comment),
                                            MessageHandler(Filters.text, grade_comment)],
                            },
                            fallbacks=[MessageHandler(
                                Filters.text | Filters.video | Filters.photo | Filters.document, dontknow)]
                            )
    )
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, answer_text))  # обработчик текстовых сообщений
    my_bot.start_polling() # проверяет наличие сообщений с платформы  Telegramm
    my_bot.idle() # бот будет работать пока его не остановят

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        requests.status_code = "Connection refused"