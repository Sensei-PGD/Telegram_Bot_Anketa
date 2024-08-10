import telebot
from telebot import types
import json

# Создаем телеграм-бота и устанавливаем токен
token = "Your Token"
bot = telebot.TeleBot(token)

survey = [
    {
        "question": "Ваш любимый вид отдыха?",
        "answers": {
            "Активный отдых": 1,
            "Пассивный отдых": -1
        }
    },
    {
        "question": "Что вы предпочитаете говорить?",
        "answers": {
            "Положительные утверждения": 1,
            "Отрицательные утверждения": -1
        }
    },
    {
        "question": "Что вас больше всего вдохновляет?",
        "answers": {
            "Достижения других людей": 1,
            "Отдых и релаксация": -1
        }
    },
    {
        "question": "Как вы относитесь к переменам?",
        "answers": {
            "Люблю новые возможности": 1,
            "Предпочитаю стабильность": -1
        }
    },
    {
        "question": "Ваша реакция на неудачу?",
        "answers": {
            "Мотивация действовать": 1,
            "Утомление и разочарование": -1
        }
    }
]

user_answers = {}


def filter_begin(message):
    words = ["начать", "начинаем", "пройдем", "начинай", "поехали", "пошли", "давай", "начнем", "вперед"]
    return any(map(lambda word: word in message.text.lower(), words))


@bot.message_handler(commands=["start"])
def say_start(message):
    bot.send_message(message.chat.id, "Привет, я бот-анкета!\n"
                                      "\nЯ Бот-анкета, могу предложить Вам психологический тест на тему «Я оптимист или пессимист?»\n"
                                      "\n Доступные команды 📋:"
                                      "\n/start - начать диалог"
                                      "\n/help - справочная информация"
                                      "\n/info - получить подробную информацию о тесте"
                                      "\n/start_test - начать прохождение теста")


@bot.message_handler(commands=["help"])
def say_help(message):
    bot.send_message(message.chat.id,
                     "\n Доступные команды 📋:"
                     "\n/start - начать диалог"
                     "\n/help - справочная информация"
                     "\n/info - получить подробную информацию о тесте"
                     "\n /start_test - начать прохождение теста")


# Обработка команды /info
@bot.message_handler(commands=["info"])
def say_info(message):
    bot.send_message(message.chat.id, "\nТест «Я оптимист или пессимист?» предлагает вам узнать к какому вы относитесь типу личности." 
                                        "\nПринцип работы теста."
                                        "\nТест имеет шкалу от 1 до 5 баллов, где наименьший балл – пессимист, средний балл – сбалансированный и самый высокий балл – оптимист."
                                        "\nЗа один вопрос про оптимиста начисляется 1 балл. "
                                        "\nЗа один вопрос про пессимиста отнимается -1 балл.\n"
                                        "\nДля того чтобы начать проходить вы можете обратиться к /start_test либо же написать в чате: начать, начинаем, пройдем, начинай, поехали, пошли, давай, начнем, вперед.")


@bot.message_handler(commands=['start_test'])
def start_survey(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет ещё раз! Хочешь пройти тест? (да/нет)")
    bot.register_next_step_handler(message, handle_start_survey)


@bot.message_handler(func=filter_begin)
def start_survey(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет ещё раз! Хочешь пройти тест? (да/нет)")
    bot.register_next_step_handler(message, handle_start_survey)


def handle_start_survey(message):
    if message.text.lower() == "да":
        user_answers[message.chat.id] = {}
        send_question(message.chat.id)
    elif message.text.lower() == "нет":
        bot.send_message(message.chat.id, "Ну как решишь!")
    else:
        bot.send_message(message.chat.id, "Извините, я вас не понимаю. Пожалуйста, выберите 'да' или 'нет'")
        bot.register_next_step_handler(message, handle_start_survey)  # Регистрируем следующий обработчик для повторного ввода


# Отправка вопроса пользователю
def send_question(chat_id):
    question_number = len(user_answers[chat_id])
    if question_number < len(survey):
        question = survey[question_number]["question"]
        answers = survey[question_number]["answers"]

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for answer in answers:
            markup.add(answer)

        bot.send_message(chat_id, question, reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message: handle_user_answer(message, answers))  # Добавляем обработчик ответа
    else:
        show_result(chat_id)
        save_results(chat_id, user_answers[chat_id])
        ask_to_repeat(chat_id)


# Обработка ответа пользователя
def handle_user_answer(message, answers):
    chat_id = message.chat.id
    # Здесь можно добавить проверку на то, что пользователь выбирает только один ответ
    answer = message.text
    if answer not in answers:
        bot.send_message(chat_id, "❕ Я не понял ваше действие, повторите еще раз ваш выбор")
        send_question(chat_id)  # Приглашаем пользователя выбрать из предложенных вариантов ответа заново
    else:
        user_answers[chat_id][survey[len(user_answers[chat_id])]["question"]] = answer
        send_question(chat_id)  # Отправляем следующий вопрос


# Показ результата теста
def show_result(chat_id):
    answers_score_optimist = 0
    answers_score_pessimist = 0
    detailed_results = {}

    for question in survey:
        answer = user_answers[chat_id][question["question"]]
        question_score = question["answers"][answer]

        if question_score > 0:
            answers_score_optimist += question_score
        else:
            answers_score_pessimist += abs(question_score)

        # Сохраняем детальные результаты по каждому вопросу
        detailed_results[question["question"]] = question_score

    result_message = f"Ты набрал {answers_score_optimist} баллов у оптимиста и {answers_score_pessimist} баллов у пессимиста\n"

    if answers_score_optimist > answers_score_pessimist:
        result_message += "Ты - оптимист! 😊"
        image_path = "Optimist.png"
    elif answers_score_optimist < answers_score_pessimist:
        result_message += "Ты - пессимист! 😞"
        image_path = "Pessimist.png"
    else:
        result_message += "Ты - балансированный 😐"
        image_path = "Balanced.png"

    bot.send_photo(chat_id, open(image_path, 'rb'))
    bot.send_message(chat_id, result_message)

    # Отправляем более детальную информацию по каждому вопросу
    detailed_result_message = "Детальные результаты по каждому вопросу:\n"
    for question, score in detailed_results.items():
        detailed_result_message += f"{question}: {score} баллов\n"
    bot.send_message(chat_id, detailed_result_message)

# Сохранение результатов (вы можете использовать базу данных или файл)
def save_results(chat_id, answers):
    user_results = {
        "chat_id": chat_id,
        "answers": answers
    }
    with open('user_results.json', 'a') as file:
        json.dump(user_results, file)
        file.write('\n')


# Запрос повторного прохождения теста
def ask_to_repeat(chat_id):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_yes = types.KeyboardButton(text="Пройти ещё раз 🔄")
    button_no = types.KeyboardButton(text="Нет, закончить 🚪")
    button_help = types.KeyboardButton(text="Меню команд 📋")
    keyboard.add(button_yes, button_no, button_help)

    bot.send_message(chat_id, "Хочешь пройти тест еще раз?", reply_markup=keyboard)


# Обработка повторного прохождения теста
@bot.message_handler(func=lambda message: True)
def handle_repeat_test(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if text == "пройти ещё раз 🔄":
        user_answers[chat_id] = {}  # Сбрасываем результаты пользователя
        send_question(chat_id)  # Начинаем тест заново
    elif text == "нет, закончить 🚪":
        bot.send_message(chat_id, "Спасибо за прохождение теста! До свидания! 👋")
    elif text == "меню команд 📋":
        bot.send_message(chat_id, "\nДоступные команды 📋:"
                                  "\n/start - начать тест заново"
                                  "\n/help - получить информацию о доступных командах"
                                  "\n/info - получить подробную информацию о тесте "
                                  "\n/start_test - начать прохождение теста")
        ask_to_repeat(chat_id)  # Вызываем функцию повторного прохождения теста после отправки сообщения
    else:
        bot.send_message(chat_id, "Я не понимаю вашего выбора, выберите 'Пройти ещё раз 🔄' или 'Нет, закончить 🚪', или запросите 'Меню команд 📋'", reply_markup=ask_to_repeat(chat_id))


bot.polling()
