import telebot
import time
from telebot import types
from telebot.apihelper import ApiTelegramException


bot = telebot.TeleBot('8842648661:AAGPFrR1OTTFXzYwgLAF4LKYVKOCTGWTrQM')
ADMIN_ID = 1244731064

admin_state = {}
broadcast_data = {}

def get_users():
    try:
        with open('users.txt', 'r', encoding='utf-8') as file:
            users = file.read().splitlines()

        users = list(set(users))
        return users

    except FileNotFoundError:
        return []

def send_broadcast_message(user_id, data):
    if data['type'] == 'text':
        bot.send_message(user_id, data['text'])

    elif data['type'] == 'photo':
        bot.send_photo(
            user_id,
            data['file_id'],
            caption=data.get('caption')
        )

    elif data['type'] == 'video':
        bot.send_video(
            user_id,
            data['file_id'],
            caption=data.get('caption'))

def run_broadcast(chat_id):
    users = get_users()

    if not users:
        bot.send_message(chat_id, 'Пока нет пользователей для рассылки')
        return

    sent_count = 0
    error_count = 0
    blocked_count = 0

    bot.send_message(chat_id, 'Рассылка началась 🚀')

    for user_id in users:
        try:
            send_broadcast_message(user_id, broadcast_data)
            sent_count += 1
            time.sleep(0.12)

        except ApiTelegramException as error:
            if error.error_code == 429:
                retry_after = error.result_json.get('parameters', {}).get('retry_after', 5)
                time.sleep(retry_after)

                try:
                    send_broadcast_message(user_id, broadcast_data)
                    sent_count += 1
                    time.sleep(0.12)
                except Exception:
                    error_count += 1

            elif error.error_code == 403:
                blocked_count += 1
                error_count += 1

            else:
                error_count += 1

        except Exception:
            error_count += 1

    bot.send_message(
        chat_id,
        f'Рассылка завершена ✅\n\n'
        f'Отправлено: {sent_count}\n'
        f'Ошибок: {error_count}\n'
        f'Заблокировали бота: {blocked_count}')

@bot.callback_query_handler(func=lambda call: call.data in ['send_broadcast_now', 'cancel_broadcast'])
def broadcast_callback(call):
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == 'cancel_broadcast':
        admin_state[ADMIN_ID] = None
        broadcast_data.clear()

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

        bot.send_message(call.message.chat.id, 'Рассылка отменена ❌')
        return

    if call.data == 'send_broadcast_now':
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

        run_broadcast(call.message.chat.id)

        admin_state[ADMIN_ID] = None
        broadcast_data.clear()

def show_broadcast_preview(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('✅ Отправить', callback_data='send_broadcast_now'),
        types.InlineKeyboardButton('❌ Отмена', callback_data='cancel_broadcast')
    )

    bot.send_message(message.chat.id, 'Предпросмотр рассылки 👇')

    if broadcast_data['type'] == 'text':
        bot.send_message(
            message.chat.id,
            broadcast_data['text'],
            reply_markup=markup
        )

    elif broadcast_data['type'] == 'photo':
        bot.send_photo(
            message.chat.id,
            broadcast_data['file_id'],
            caption=broadcast_data.get('caption'),
            reply_markup=markup
        )

    elif broadcast_data['type'] == 'video':
        bot.send_video(
            message.chat.id,
            broadcast_data['file_id'],
            caption=broadcast_data.get('caption'),
            reply_markup=markup)

SPONSOR_CHANNELS = [
    {
        'title': 'МОЙ АСТРО КАНАЛ',
        'chat_id': '@tarotiz',
        'url': 'https://t.me/tarotiz'
    },
    {
        'title': 'WB НАХОДКИ',
        'chat_id': '@wbmostril',
        'url': 'https://t.me/wbmostril'
    },
    {
        'title': 'ПРОМОКОДЫ',
        'chat_id': '@ziaaprom',
        'url': 'https://t.me/ziaaprom'
    },
    {
        'title': 'АКЦИИ ЗЯ',
        'chat_id': '@rrrteww',
        'url': 'https://t.me/rrrteww'
    }
]
def save_user(user_id):
    try:
        with open('users.txt', 'r', encoding='utf-8') as file:
            users = file.read().splitlines()
    except FileNotFoundError:
        users = []

    user_id = str(user_id)

    if user_id not in users:
        with open('users.txt', 'a', encoding='utf-8') as file:
            file.write(user_id + '\n')


def get_unsubscribed_channels(user_id):
    unsubscribed_channels = []

    for channel in SPONSOR_CHANNELS:
        try:
            member = bot.get_chat_member(channel['chat_id'], user_id)

            if member.status in ['left', 'kicked']:
                unsubscribed_channels.append(channel)

        except Exception:
            unsubscribed_channels.append(channel)

    return unsubscribed_channels

def send_typing_message(chat_id, text, delay=3, reply_markup=None, parse_mode='HTML'):
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(delay)
    bot.send_message(
        chat_id,
        text=text,
        parse_mode=parse_mode,
        reply_markup=reply_markup)


@bot.message_handler(commands=['start'])
def main(message):
    start_menu = types.InlineKeyboardMarkup()

    start_menu.add(types.InlineKeyboardButton(
        text='АСТРОРАЗБОР',
        callback_data='astro'))

    start_menu.add(types.InlineKeyboardButton(
        text='ПРИВОРОТ, МОРОК И Т.Д.',
        callback_data='magic'))

    start_menu.add(types.InlineKeyboardButton(
        text='ПРАКТИКИ',
        callback_data='practices'))

    start_menu.add(types.InlineKeyboardButton(
        text='КОД-ПРИВЯЗКА',
        callback_data='code'))
    save_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        text=f"""<b>Привет, {message.from_user.first_name}!</b> Этот бот поможет тебе узнать:

1. Ответ на вопрос при помощи хорарной астрологии;
2. Подобрать личную практику специально для тебя по твоей дате рождения;
3. Составить личный любовный код для партнера;
4. А также ты можешь здесь оставить свой запрос на морок, привязку, приворот и т.п.🔮

<i>(у тебя есть только одна бесплатная первая попытка, так что выбирай, что для тебя в приоритете)</i>

Для продолжения нажми на кнопку ниже ⬇️""",
        parse_mode='HTML',
        reply_markup=start_menu)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📢 Сделать рассылку')
    markup.add('📊 Статистика')

    bot.send_message(
        message.chat.id,
        'Админ-панель открыта 👇',
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def main_callback_handler(call):
    if call.data in ['send_broadcast_now', 'cancel_broadcast']:
        return

    bot.answer_callback_query(call.id)

    if call.data == 'astro':
        bot.send_message(
            call.message.chat.id,
            text="""Перед тем как ты опишешь свою ситуацию, прочитай текст ниже, чтобы лучше понимать, что такое хорарная астрология:

🔮<b><i>Хорарная астрология</i></b> — это часовая или вопросная астрология. Она помогает получить ответ на конкретный вопрос, который волнует человека в данный момент. Карта строится на момент задания вопроса, и по ней можно увидеть развитие ситуации, скрытые обстоятельства, намерения людей и возможный исход.

Теперь подробно опиши свою ситуацию и задай конкретный вопрос🙏🏻

Для создания твоей индивидуальной астральной карты необходима <b>твоя дата рождения и город</b>.""",
            parse_mode='HTML')

    elif call.data == 'magic':
        read_menu = types.InlineKeyboardMarkup()

        read_menu.add(types.InlineKeyboardButton(
            text='Я ПРОЧИТАЛ(-А)',
            callback_data='magic_read'))

        bot.send_message(
            call.message.chat.id,
            text="""Перед тем как выбрать, что тебе нужно, ниже представлено краткое описание оказываемых нами услуг:

🔮<b><i>Морок</i></b>. Его ещё называют оморочка. Воздействие на теменную и головную чакру, с целью внушить жертве какую-то мысль, запутать, что-то внушить.

🔮<b><i>Приворот</i></b> — это энергоинформационная программа, направленная на привлечение какого-то лица к любовному контакту. Без предмета своего обожания больной может сохнуть, страдать, худеет. Буквально тает на глазах.

🔮<b><i>Присушка</i></b> — это любовное воздействие, направленное на появление тоски, интереса, тяги и желания общения у конкретного человека. Человек начинает чаще думать о тебе, скучать и испытывать потребность выйти на контакт.

🔮<b><i>Привязка</i></b> — тоже разновидность приворота, может использоваться для сохранности дружбы, рабочих отношений. Как и все привороты, это создание зависимости: сексуальной, энергетической, физической, психической, сексуальной.

🔮<b><i>Отворот/остуда</i></b> — это энергоинформационная программа, направленная на разрыв какой-то связи между людьми. Ему могут подвергаться пары, партнеры по работе, подруги. Фактически портятся какие-то отношения.

🔮<b><i>Рассорка</i></b> — большие конфликты по мелочам в семье, так что после ссоры супруги думают, с чего вдруг они сорвались. Не видя друг друга, пара скучает, а как только встречаются, готовы друг друга испепелить по несущественным поводам.""",
            parse_mode='HTML',
            reply_markup=read_menu)

    elif call.data == 'magic_read':
        magic_choice_menu = types.InlineKeyboardMarkup()

        magic_choice_menu.add(types.InlineKeyboardButton(
            text='МОРОК',
            callback_data='morok'))

        magic_choice_menu.add(types.InlineKeyboardButton(
            text='ПРИВОРОТ',
            callback_data='privorot'))

        magic_choice_menu.add(types.InlineKeyboardButton(
            text='ПРИСУШКА',
            callback_data='prisushka'))

        magic_choice_menu.add(types.InlineKeyboardButton(
            text='ПРИВЯЗКА',
            callback_data='privyazka'))

        magic_choice_menu.add(types.InlineKeyboardButton(
            text='ОТВОРОТ/ОСТУДА',
            callback_data='otvorot'))

        magic_choice_menu.add(types.InlineKeyboardButton(
            text='РАССОРКА',
            callback_data='rassorka'))

        bot.send_message(
            call.message.chat.id,
            text='Теперь выбери то, что тебе нужно:',
            reply_markup=magic_choice_menu)

    elif call.data == 'practices':
        bot.send_message(
            call.message.chat.id,
            text="""Для подбора личной практики напиши одним сообщением:

1. Свое имя;
2. Дату рождения;
3. Время рождения, если знаешь;
4. Город рождения;
5. Какой результат ты хочешь получить от практики.

Например:

<i>Алина
12.03.2003
14:30
Москва
Хочу практику на раскрытие женской энергии, уверенности в себе и усиление привлекательности.</i>

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML')

    elif call.data == 'code':
        bot.send_message(
            call.message.chat.id,
            text="""Чтобы создать персональный любовный код-привязку, напиши одним сообщением:

1. Твое имя и дату рождения;
2. Имя и дату рождения человека, на которого создается код.

Например:

<i>Алина 12.03.2003
Иван 13.08.2000</i>

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML')

    elif call.data == 'morok':
        bot.send_message(
            call.message.chat.id,
            text="""Ты выбрала: <b>МОРОК</b>.

Теперь опиши свою ситуацию одним сообщением:

1. Твое имя и дату рождения;
2. Имя и дату рождения человека, если знаешь;
3. Какие отношения у вас сейчас;
4. Что именно ты хочешь внушить или изменить;
5. Какой результат ты хочешь получить.

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML')

    elif call.data == 'privorot':
        bot.send_message(
            call.message.chat.id,
            text="""Ты выбрала: <b>ПРИВОРОТ</b>.

Теперь опиши свою ситуацию одним сообщением:

1. Твое имя и дату рождения;
2. Имя и дату рождения человека;
3. Какие отношения у вас сейчас;
4. Что между вами произошло;
5. Какой результат ты хочешь получить.

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML')

    elif call.data == 'prisushka':
        bot.send_message(
            call.message.chat.id,
            text="""Ты выбрала: <b>ПРИСУШКА</b>.

Теперь опиши свою ситуацию одним сообщением:

1. Твое имя и дату рождения;
2. Имя и дату рождения человека;
3. Общаетесь ли вы сейчас;
4. Как давно знакомы;
5. Какой результат ты хочешь получить.

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML')

    elif call.data == 'privyazka':
        bot.send_message(
            call.message.chat.id,
            text="""Ты выбрала: <b>ПРИВЯЗКА</b>.

Теперь опиши свою ситуацию одним сообщением:

1. Твое имя и дату рождения;
2. Имя и дату рождения человека;
3. Какая связь между вами сейчас;
4. Что ты хочешь сохранить или усилить;
5. Какой результат ты хочешь получить.

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML')

    elif call.data == 'otvorot':
        bot.send_message(
            call.message.chat.id,
            text="""Ты выбрала: <b>ОТВОРОТ/ОСТУДА</b>.

Теперь опиши свою ситуацию одним сообщением:

1. Кого нужно отдалить друг от друга;
2. Какие отношения между этими людьми;
3. Как давно длится эта связь;
4. Почему ты хочешь сделать отворот/остуду;
5. Какой результат ты хочешь получить.

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML')

    elif call.data == 'rassorka':
        bot.send_message(
            call.message.chat.id,
            text="""Ты выбрала: <b>РАССОРКА</b>.

Теперь опиши свою ситуацию одним сообщением:

1. Между кем нужно создать конфликт;
2. Какие отношения между этими людьми;
3. Как давно они общаются;
4. Почему ты хочешь сделать рассорку;
5. Какой результат ты хочешь получить.

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML'
        )

    elif call.data == 'show_answer':
        continue_menu = types.InlineKeyboardMarkup()

        continue_menu.add(types.InlineKeyboardButton(
            text='ПРОДОЛЖИТЬ',
            callback_data='continue'))

        bot.send_message(
            call.message.chat.id,
            text="""Перед тем как перейти к следующему шагу, мы обязаны предупредить, что это не совсем бесплатно. Человек (то есть я и моя команда) НЕ МОЖЕТ тратить свою энергию, силы и время просто так, без какой либо "оплаты", поэтому мы требуем лишь подписку!

Спасибо за понимание!💘""",
            reply_markup=continue_menu)


    elif call.data == 'continue':

        subscribed_menu = types.InlineKeyboardMarkup(row_width=2)

        subscribed_menu.add(

            types.InlineKeyboardButton(

                text='🔮МОЙ КАНАЛ🔮',

                url='https://t.me/tarotiz'),

            types.InlineKeyboardButton(

                text='WB НАХОДКИ',

                url='https://t.me/wbmostril'))

        subscribed_menu.add(

            types.InlineKeyboardButton(

                text='ПРОМОКОДЫ',

                url='https://t.me/ziaaprom'),

            types.InlineKeyboardButton(

                text='АКЦИИ ЗЯ',

                url='https://t.me/rrrteww'))

        subscribed_menu.add(types.InlineKeyboardButton(

            text='✅Я ПОДПИСАЛСЯ(-АСЬ)',

            callback_data='subscribed'))

        bot.send_message(
            call.message.chat.id,
            text="""<b><i>❗️ВНИМАНИЕ❗️
Твой запрос на данный момент в обработке!</i></b>
Потребуется немного времени, чтобы наша команда помогла тебе с ним! 
<b>❗️ОТВЕТ ПОЛУЧАТ АБСОЛЮТНО ВСЕ, просто в порядке очереди, придется немного подождать</b>

<i>Чтобы получить все бесплатно, тебе необходимо подписаться на наших партнёров: 
(поймите, полностью бесплатно работать - в ущерб себе, поэтому мы просим лишь подписку💕)
После автоматической проверки подписки в течении нескольких суток вам напишет одна из наших пяти коллег (просим вас запастись терпением, так как вас много, а нас всего пятеро)</i> 

❗️<b>БЕЗ ПОДПИСКИ НА ВСЕХ СПОНСОРОВ БОТ ВАМ НИЧЕГО НЕ ОТПРАВИТ❗️</b>""",parse_mode='HTML',
            reply_markup=subscribed_menu)


    elif call.data == 'subscribed':

        unsubscribed_channels = get_unsubscribed_channels(call.from_user.id)

        if unsubscribed_channels:

            not_subscribed_menu = types.InlineKeyboardMarkup(row_width=1)

            for channel in unsubscribed_channels:
                not_subscribed_menu.add(types.InlineKeyboardButton(

                    text=f"Подписаться: {channel['title']}",

                    url=channel['url']

                ))

            not_subscribed_menu.add(types.InlineKeyboardButton(

                text='✅ Я подписался(-ась), проверить ещё раз',

                callback_data='subscribed'

            ))

            bot.answer_callback_query(

                call.id,

                'Ты подписался(-ась) не на всех спонсоров 💔',

                show_alert=True

            )

            bot.send_message(

                call.message.chat.id,

                text="""<b>Почти готово💘</b>
                
Я проверила подписку и вижу, что ты подписался(-ась) <b>не на всех спонсоров</b>.
Пожалуйста, подпишись на все каналы из списка ниже, а потом нажми кнопку:


<b>✅ Я подписался(-ась), проверить ещё раз</b>


    ⚠️ <i>Без подписки на всех спонсоров заявка не сможет попасть в очередь.</i>""",

                reply_markup=not_subscribed_menu,

                parse_mode='HTML'

            )

            return

        bot.send_message(

            call.message.chat.id,

            text="""<b>Спасибо!💘</b>

Твой запрос <b>принят</b> и поставлен в очередь на обработку.
⏳<b>Примерное время ожидания ответа:</b> <u>до 48 часов 31 минуты</u>.

<i>Я или одна из участниц моей команды обязательно вернёмся к твоему запросу, как только подойдёт твоя очередь.</i>


⚠️<b><u>Пожалуйста, не отписывайся от спонсоров до получения ответа.</u></b>


Если подписка будет отменена, бот может <b>не увидеть тебя в очереди</b>, и заявка автоматически потеряет приоритет :(
🔮<b>Энергообмен очень важен</b>, поэтому мы просим лишь подписку на партнёров💕


Если ты <b>не готов(-а) ждать бесплатный ответ</b> или хочешь получить помощь быстрее, ты можешь написать мне лично и заказать ритуал <b><u>на платной основе</u></b>.


📩<b>МОИ КОНТАКТЫ: @tarotmarian</b>""",

            parse_mode='HTML')


@bot.message_handler(content_types=['photo', 'video'])
def handle_admin_media(message):
    if message.from_user.id != ADMIN_ID:
        return

    if admin_state.get(ADMIN_ID) != 'waiting_broadcast':
        return

    if message.content_type == 'photo':
        broadcast_data.clear()
        broadcast_data.update({
            'type': 'photo',
            'file_id': message.photo[-1].file_id,
            'caption': message.caption
        })

    elif message.content_type == 'video':
        broadcast_data.clear()
        broadcast_data.update({
            'type': 'video',
            'file_id': message.video.file_id,
            'caption': message.caption
        })

    show_broadcast_preview(message)

@bot.message_handler(content_types=['text'])
def get_user_text(message):
    if message.from_user.id == ADMIN_ID:
        if message.text == '📢 Сделать рассылку':
            admin_state[ADMIN_ID] = 'waiting_broadcast'

            bot.send_message(
                message.chat.id,
                'Отправь текст, фото или видео для рассылки.\n\n'
                'Если отправляешь фото или видео, можешь добавить подпись.'
            )
            return

        if message.text == '📊 Статистика':
            users = get_users()

            bot.send_message(
                message.chat.id,
                f'Пользователей в базе: {len(users)}'
            )
            return

        if admin_state.get(ADMIN_ID) == 'waiting_broadcast':
            broadcast_data.clear()
            broadcast_data.update({
                'type': 'text',
                'text': message.text
            })

            show_broadcast_preview(message)
            return

    show_answer_menu = types.InlineKeyboardMarkup()

    show_answer_menu.add(types.InlineKeyboardButton(
        text='ПОКАЗАТЬ ОТВЕТ',
        callback_data='show_answer'
    ))

    send_typing_message(
        message.chat.id,
        text='<b><i>Анализ полученных данных...</i></b>',
        delay=3
    )

    send_typing_message(
        message.chat.id,
        text='<b><i>Еще чуть-чуть...</i></b>',
        delay=3
    )

    send_typing_message(
        message.chat.id,
        text='<b><i>Ответ получен! 🪐</i></b>',
        delay=3,
        reply_markup=show_answer_menu
    )


bot.polling(non_stop=True)
