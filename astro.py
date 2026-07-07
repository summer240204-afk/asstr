import telebot
from telebot import types
from dotenv import load_dotenv
import os


load_dotenv()
bot = telebot.TeleBot(os.environ['TOKEN'])



@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('АСТРОРАЗБОР'))
    markup.add(types.KeyboardButton('ПРИВОРОТ, МОРОК И Т.Д.'))
    markup.add(types.KeyboardButton('ПРАКТИКИ'))
    markup.add(types.KeyboardButton('КОД-ПРИВЯЗКА'))

    bot.send_message(
        message.chat.id,
        text=f"""*Привет, {message.from_user.first_name}!* Этот бот поможет тебе узнать:
1. Ответ на вопрос при помощи хорарной астрологии;
2. Подобрать личную практику специально для тебя по твоей дате рождения;
3. Составить личный любовный код для партнера
5. А также ты можешь здесь оставить свой запрос на морок, привязку, приворот и т.п.🔮

_(у тебя есть только одна бесплатная (первая) попытка, так что выбирай, что для тебя в приоритете)_

Для продолжения выбери кнопку ниже ⬇️""",
        parse_mode='Markdown',
        reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def on_click(message):
    @bot.callback_query_handler(func=lambda call: call.data == 'magic_read')
    def magic_read(call):
        bot.answer_callback_query(call.id)

        main_menu = types.InlineKeyboardMarkup()
        main_menu.add(types.InlineKeyboardButton(text='МОРОК', callback_data='МОРОК'))
        main_menu.add(types.InlineKeyboardButton(text='ПРИВОРОТ', callback_data='ПРИВОРОТ'))
        main_menu.add(types.InlineKeyboardButton(text='ПРИСУШКА', callback_data='ПРИСУШКА'))
        main_menu.add(types.InlineKeyboardButton(text='ПРИВЯЗКА', callback_data='ПРИВЯЗКА'))
        main_menu.add(types.InlineKeyboardButton(text='ОТВОРОТ/ОСТУДА', callback_data='ОТВОРОТ/ОСТУДА'))
        main_menu.add(types.InlineKeyboardButton(text='РАССОРКА', callback_data='РАССОРКА'))

        bot.send_message(
            call.message.chat.id,
            'Теперь выбери то, что тебе нужно:',
            reply_markup=markup)

    @bot.callback_query_handler(
        func=lambda call: call.data in ['МОРОК', 'ПРИВОРОТ', 'ПРИСУШКА', 'ПРИВЯЗКА', 'ОТВОРОТ/ОСТУДА', 'РАССОРКА'])
    def magic_choice(call):
        bot.answer_callback_query(call.id)

        names = {
            'МОРОК': 'Морок',
            'ПРИВОРОТ': 'Приворот',
            'ПРИСУШКА': 'Присушка',
            'ПРИВЯЗКА': 'Привязка',
            'ОТВОРОТ/ОСТУДА': 'Отворот/остуда',
            'РАССОРКА': 'Рассорка'
        }

        bot.send_message(
            call.message.chat.id,
            f'Ты выбрала: {names[call.data]}. Опиши свою ситуацию одним сообщением.')

    if message.text == 'АСТРОРАЗБОР':
        bot.send_message(message.chat.id, text = '''Перед тем как ты опишешь свою ситуацию прочитай текст ниже чтобы лучше понимать что такое хорарная астрология: 

🔮<em><b>Хорарная астрология</b> - это часовая или вопросная астрология. Т.е. это астрология, которая отвечает на ЛЮБОЙ КОНКРЕТНЫЙ вопрос.
Для того, чтобы получить астрологический ответ, нужно:
1)правильно задать вопрос;
2)отметить время рождения вопроса;
3)ждать ответ.

Хорарная астрология отвечает на любые конкретные вопросы:
- выйду ли я замуж за Пашу,
- куплю ли я эту квартиру,
-поступлю ли я в этот ВУЗ
-будет ли мне комфортно в этом городе, этой стране и т.д.</em>

Теперь подробно опиши свою ситуацию и задай конкретный вопрос🙏🏻

Для создания твоей индивидуальной астральной карты необходимо <b>твоя дата рождения и город</b> (из которого задаётся вопрос)
❗<u><b>️пиши всё в одном сообщении</b></u>❗️''', parse_mode = 'html')


    elif message.text == 'ПРИВОРОТ, МОРОК И Т.Д.':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text='Я ПРОЧИТАЛ(-А)',
            callback_data='magic_read'))

        bot.send_message(
            message.chat.id,
            text='''Перед тем как выбрать, что тебе нужно, ниже представлено краткое описание оказываемых нами услуг:

    🔮<em><b>Морок</b></em>. Его ещё называют оморочка. Воздействие на теменную и головную чакру, с целью внушить жертве какую-то мысль, запутать, что-то внушить.

    🔮<em><b>Приворот</b></em> – это энергоинформационная программа, направленная на привлечение какого-то лица к любовному контакту.

    🔮<em><b>Присушка</b></em> – разновидность приворота, с целью привлечь внимание конкретного человека.

    🔮<em><b>Привязка</b></em> – тоже разновидность приворота, может использоваться для сохранности дружбы, рабочих отношений.

    🔮<em><b>Отворот/остуда</b></em> – это энергоинформационная программа, направленная на разрыв какой-то связи между людьми.

    🔮<em><b>Рассорка</b></em> – большие конфликты по мелочам в семье.''', parse_mode='html', reply_markup=markup)









    elif message.text == 'ПРАКТИКИ':
        bot.send_message(message.chat.id, text= '''Напиши свою <em><b>дату рождения и время</b></em> (время по возможности, если знаешь), также напиши свое <em><b>имя и город</b></em> в котором родился(-ась)

При помощи этих данных мы создадим индивидуальную подобранную лично под тебя практику💞
<em>Слова этой практики ты сможешь использовать на любой твоей личной вещи, с которой ты соприкасаешься каждый день (например: расческа, резинка для волос, кольцо и т.п.)</em>''', parse_mode = 'html')







    elif message.text == 'КОД-ПРИВЯЗКА':
        bot.send_message(message.chat.id, text='''Чтобы создать персональный код потребуется ваше <em><b>имя и дата рождения</b></em>, а также имя и дата рождения человека на которого создается код:
       <em>(например: 
       Алина 12.03.2003
       Иван: 13.08.2000)
       <u>Пиши ниже👇🏻</u></em>''', parse_mode='html')













bot.polling(none_stop=True)
