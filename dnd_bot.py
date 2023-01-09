import telebot
from telebot import types
import random
from time import sleep


bot = telebot.TeleBot('5883583512:AAGS5mivEXo2WT4rTCVuuha1uO1aj9cwsL8')

# Уровни сложности броска
diff_lvl = ['легкая', 'средняя', 'тяжелая']
# Сообщения в случае крит. успеха
crit_success = ['Невероятный бросок! Это критический успех!',
                'Критический успех! Судьба сегодня на Вашей стороне.',
                'Вам невероятно повезло! Критический успех!']
# Сообщения в случае крит. неудачи
crit_fail = ['Критическая неудача! С такой удачей сегодня лучше не выходить из дома.',
             'Вы с треском провалили проверку, критический провал.',
             'Критическая неудача! Судьба отвернулась от Вас.']
# Сообщения в случае успеха
success = ['Успех! Вам с легкостью получается воплотить задуманное.',
           'Успех! У Вас все получилось, поздравляем!',
           'Успех! Удача улыбнулась Вам.']
# Сообщения в случае неудачи
fail = ['Провал, Вам не получилось совершить задуманное.',
        'Увы, этого недостаточно, действие провалено.',
        'Вам не повезло, удача отвернулась от вас.']
# Сюда записывается уровень сложности, делая переменную глобальной
difficulty = []


# Функция определяет уровень сложности игры
def diff_lvl_func():
    diff = random.choice(diff_lvl)
    if diff == diff_lvl[0]:
        edge = 7
    if diff == diff_lvl[1]:
        edge = 10
    if diff == diff_lvl[2]:
        edge = 15
    return edge, diff


# Функция имитирует бросок кубика и возвращает сообщение о результате
def dice_throw(edge):
    result = random.randint(1, 20)
    if result == 20:
        mess_1 = 'Вам выпало {}'.format(result)
        mess_2 = random.choice(crit_success)
    if result == 1:
        mess_1 = 'Вам выпало {}'.format(result)
        mess_2 = random.choice(crit_fail)
    if result >= edge and result != 20:
        mess_1 = 'Вам выпало {}'.format(result)
        mess_2 = random.choice(success)
    if result < edge and result != 1:
        mess_1 = 'Вам выпало {}'.format(result)
        mess_2 = random.choice(fail)
    return mess_1, mess_2


# Режим стандартной игры, где игроку нужно самому нажать на кнопку, чтобы выполнить бросок кубика
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, '''Привет! Я бот, который имитирует бросок кубика в игровой ситуации, да, как в DnD.
В режиме /go начнется игра, где тебе нужно будет написать действие и кинуть кубик самому, все происходит последовательно.
В режиме /fast_game нужно сначала написать твое действие, а потом выбрать этот режим, я сам кину кубик и напишу результат. Все просто =)
Удачи!''')


@bot.message_handler(commands=['go'])
def start_game(message):
    bot.send_message(message.chat.id, "Какое действие Вы хотите совершить? Нажмите /, затем введите действие")
    bot.register_next_step_handler(message, next_step)


def next_step(message):
    bot.message_handler(content_types=["text"])
    sleep(0.3)
    edge, diff = diff_lvl_func()
    bot.reply_to(message, 'Начнем')
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Кинуть кубик', callback_data='yes')
    keyboard.add(key_yes)
    bot.send_message(message.chat.id,
                     text="Сложность определена как {}, бросайте один d20 кубик. "
                          "Вам нужно выкинуть {} или больше".format(diff, edge),
                     reply_markup=keyboard)
    difficulty.clear()
    difficulty.append(edge)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        mess_1, mess_2 = dice_throw(difficulty[0])
        bot.send_message(call.message.chat.id, mess_1)
        sleep(0.2)
        bot.send_message(call.message.chat.id, mess_2)


# Режим быстрой игры, где не требуются действия игрока
@bot.message_handler(commands=['fast_game'])
def fast_game(message):
    edge, diff = diff_lvl_func()
    bot.send_message(message.chat.id, "Сложность определена как {}. "
                                      "Вам нужно выкинуть {} или больше. Бросаю кубик...".format(diff, edge))
    sleep(1)
    mess_1, mess_2 = dice_throw(edge)
    bot.send_message(message.chat.id, mess_1)
    sleep(0.2)
    bot.send_message(message.chat.id, mess_2)


# Функция вызова бота, вариант быстрой игры в одно сообщение
@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(query):
    edge, diff = diff_lvl_func()
    result = random.randint(1, 20)
    if result == 20:
        message = 'Сложность определена как {}. Вам нужно выкинуть {} или больше.\nВам выпало {}.\n{}'\
            .format(diff, edge, result, random.choice(crit_success))
    if result == 1:
        message = 'Сложность определена как {}. Вам нужно выкинуть {} или больше.\nВам выпало {}.\n{}'\
            .format(diff, edge, result, random.choice(crit_fail))
    if result >= edge and result != 20:
        message = 'Сложность определена как {}. Вам нужно выкинуть {} или больше.\nВам выпало {}.\n{}'\
            .format(diff, edge, result, random.choice(success))
    if result < edge and result != 1:
        message = 'Сложность определена как {}. Вам нужно выкинуть {} или больше.\nВам выпало {}.\n{}'\
            .format(diff, edge, result, random.choice(fail))

    r = types.InlineQueryResultArticle(
        id='1', title="Узнай свои шансы",
        description='Нажми, чтобы узнать',
        input_message_content=types.InputTextMessageContent(message_text='{}\n{}'.format(query.query, message)))
    bot.answer_inline_query(query.id, [r])


bot.polling(none_stop=True)
