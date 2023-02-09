# Chat_Bot_Artifical_Rieltor
Создал чат-бота риэлтора для продажи дачи.

Стэк: telegram, annoy, transformers, torch, tensorflow, logging, re, glob, nltk, requests, pymongo, pymorphy2, stop_words, string

   Проект создавался в 2021 году, а с 2022 года MongoDB с Россией не работает. 
Поэтому папка database и файл mongodb.py не работают.
Из-за огромного размера не удалось загрузить папку pickled_files с бертовыми файлами. 
   -    Знакомство с проектом прошу начинать с файла PRESENTATION.pdf
   -    bot.py корневой файл программы
   -    utility.py и handlers.py содержат вспомогательные функции к файлу bot.py
   -    еще требуется файл setting.py, содержащий TELEGRAM_TOKEN, TELEGRAM_API_URL и переменные для работы с базой данных MongoDB.

   Предобработка данных производилась в ноутбуках: 
   -    Chat_bot_step1.ipynb предобработка датасета с вопросами - ответами от mail.ru
   -    Chat_bot_step2.ipynb получение бертовых эмбеддингов вопросов от mail.ru
   -    Chat_bot_step2_planeta_qwestions.ipynb получение бертовых эмбеддингов вопросов по поводу дачи

