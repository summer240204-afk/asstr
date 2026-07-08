import telebot
import time
import os
import json
import re
import html
from telebot import types
from telebot.apihelper import ApiTelegramException

bot = telebot.TeleBot('8842648661:AAGPFrR1OTTFXzYwgLAF4LKYVKOCTGWTrQM')
ADMIN_ID = 1244731064

admin_state = {}
broadcast_data = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.txt')
PROMO_FILE = os.path.join(BASE_DIR, 'promo_items.json')
REQUIRED_CHANNELS_FILE = os.path.join(BASE_DIR, 'required_channels.json')

print('Файл users.txt используется тут:', USERS_FILE)


def get_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
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
            caption=data.get('caption')
        )


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
        f'Заблокировали бота: {blocked_count}'
    )


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
            reply_markup=markup
        )


DEFAULT_REQUIRED_CHANNELS = [
    {
        'order': 10,
        'title': 'МОЙ АСТРО КАНАЛ',
        'chat_id': '@tarotiz',
        'url': 'https://t.me/tarotiz'
    },
    {
        'order': 20,
        'title': 'WB НАХОДКИ',
        'chat_id': '@wbmostril',
        'url': 'https://t.me/wbmostril'
    },
    {
        'order': 30,
        'title': 'ПРОМОКОДЫ',
        'chat_id': '@ziaaprom',
        'url': 'https://t.me/ziaaprom'
    },
    {
        'order': 40,
        'title': 'АКЦИИ ЗЯ',
        'chat_id': '@rrrteww',
        'url': 'https://t.me/rrrteww'
    }
]


def save_user(user_id):
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            users = file.read().splitlines()
    except FileNotFoundError:
        users = []

    user_id = str(user_id)

    if user_id not in users:
        with open(USERS_FILE, 'a', encoding='utf-8') as file:
            file.write(user_id + '\n')


def load_json_file(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return default


def save_json_file(path, data):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_promo_items():
    return load_json_file(PROMO_FILE, [])


def save_promo_items(items):
    save_json_file(PROMO_FILE, items)


def load_required_channels():
    data = load_json_file(REQUIRED_CHANNELS_FILE, [])

    if not data:
        return [dict(item) for item in DEFAULT_REQUIRED_CHANNELS]

    normalized = []
    for index, item in enumerate(data, 1):
        normalized_item = dict(item)
        normalized_item.setdefault('order', index * 10)
        normalized.append(normalized_item)

    return normalized


def save_required_channels(items):
    save_json_file(REQUIRED_CHANNELS_FILE, items)


PROMO_ITEMS = load_promo_items()
REQUIRED_CHANNELS = load_required_channels()


def get_unsubscribed_channels(user_id):
    unsubscribed_channels = []

    for channel in REQUIRED_CHANNELS:
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
        reply_markup=reply_markup
    )


def utf16_index_to_py_index(text, utf16_index):
    current = 0

    for index, char in enumerate(text):
        if current >= utf16_index:
            return index
        current += len(char.encode('utf-16-le')) // 2

    return len(text)


def get_message_text_and_entities(message):
    if getattr(message, 'text', None):
        return message.text, message.entities or []
    return getattr(message, 'caption', None) or '', message.caption_entities or []


def parse_imported_list_message(message):
    text, entities = get_message_text_and_entities(message)
    if not text:
        return []

    lines = text.splitlines()

    line_starts = []
    pos = 0
    for line in lines:
        line_starts.append(pos)
        pos += len(line) + 1

    items = []

    for index, line in enumerate(lines):
        match = re.match(r'^\s*(\d+)\s*[\.\)]\s*(.+?)\s*$', line)
        if not match:
            continue

        order = int(match.group(1))
        title = match.group(2).strip()

        line_start = line_starts[index]
        line_end = line_start + len(line)
        url = None

        for entity in entities:
            ent_start = utf16_index_to_py_index(text, entity.offset)
            ent_end = utf16_index_to_py_index(text, entity.offset + entity.length)

            if ent_start >= line_start and ent_start <= line_end:
                if entity.type == 'text_link':
                    url = entity.url
                    break
                elif entity.type == 'url':
                    url = text[ent_start:ent_end]
                    break

        items.append({
            'order': order,
            'title': title,
            'url': url,
            'type': 'link'
        })

    items.sort(key=lambda x: x['order'])
    return items


def parse_required_channels_text(text):
    channels = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = [part.strip() for part in line.split('|')]

        order = (len(channels) + 1) * 10

        if len(parts) == 4:
            order_text, title, chat_id, url = parts
            try:
                order = int(order_text)
            except ValueError:
                continue
        elif len(parts) == 3:
            title, chat_id, url = parts
        elif len(parts) == 2:
            title, url = parts
            chat_id = url
        else:
            continue

        if chat_id.startswith('https://t.me/'):
            chat_id = '@' + chat_id.replace('https://t.me/', '').strip('/').lstrip('@')

        channels.append({
            'order': order,
            'title': title,
            'chat_id': chat_id,
            'url': url
        })

    return channels


def build_items_text(items):
    items = sorted(items, key=lambda x: x.get('order', 10**9))

    if not items:
        return '<i>Список ссылок пока не загружен.</i>'

    lines = ['<b>Ссылки:</b>']

    for index, item in enumerate(items, 1):
        title = html.escape(item.get('title', 'Без названия'))
        url = item.get('url')

        if url:
            url = html.escape(url, quote=True)
            lines.append(f'{index}. <a href="{url}">{title}</a>')
        else:
            lines.append(f'{index}. {title}')

    return '\n'.join(lines)

def build_all_links_text():
    merged = []

    for channel in REQUIRED_CHANNELS:
        merged.append({
            'order': channel.get('order', 10**9),
            'title': channel.get('title', 'Без названия'),
            'url': channel.get('url'),
            'kind': 'required'
        })

    for item in PROMO_ITEMS:
        merged.append({
            'order': item.get('order', 10**9),
            'title': item.get('title', 'Без названия'),
            'url': item.get('url'),
            'kind': 'promo'
        })

    merged.sort(key=lambda x: x['order'])

    if not merged:
        return '<i>Список ссылок пока не загружен.</i>'

    lines = ['<b>Ссылки:</b>']

    for index, item in enumerate(merged, 1):
        title = html.escape(item['title'])
        url = item.get('url')
        prefix = '🔒 ' if item['kind'] == 'required' else ''

        if url:
            lines.append(f'{index}. {prefix}<a href="{html.escape(url, quote=True)}">{title}</a>')
        else:
            lines.append(f'{index}. {prefix}{title}')

    return '\n'.join(lines)

def send_long_html_message(chat_id, text):
    max_len = 3500
    chunks = []
    current = ''

    for line in text.split('\n'):
        candidate = line if not current else current + '\n' + line

        if len(candidate) > max_len:
            if current:
                chunks.append(current)
            current = line
        else:
            current = candidate

    if current:
        chunks.append(current)

    for chunk in chunks:
        bot.send_message(
            chat_id,
            chunk,
            parse_mode='HTML',
            disable_web_page_preview=True
        )


def build_required_channels_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)

    for channel in REQUIRED_CHANNELS:
        markup.add(
            types.InlineKeyboardButton(
                text=f"Подписаться: {channel['title']}",
                url=channel['url']
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            text='✅ Я подписался(-ась), проверить ещё раз',
            callback_data='subscribed'
        )
    )

    return markup


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
    markup.add('📥 Импорт ссылок')
    markup.add('⚙️ Каналы с проверкой')
    markup.add('📋 Показать ссылки')
    markup.add('📊 Статистика')
    markup.add('🗑 Очистить список ссылок')
    markup.add('♻️ Сбросить 4 проверочных канала')
    markup.add('❌ Отмена')

    bot.send_message(
        message.chat.id,
        'Админ-панель открыта 👇',
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def main_callback_handler(call):
    save_user(call.from_user.id)

    if call.data in ['send_broadcast_now', 'cancel_broadcast']:
        return

    bot.answer_callback_query(call.id)

    if call.data == 'astro':
        bot.send_message(
            call.message.chat.id,
            text="""Перед тем как ты опишешь свою ситуацию, прочитай текст ниже, чтобы лучше понимать, что такое хорарная астрология:

🔮<b><i>Хорарная астрология</i></b> — это часовая или вопросная астрология. Она помогает получить ответ на конкретный вопрос, который волнует человека в данный момент. Карта строится на момент задания вопроса, и по ней можно увидеть развитие ситуации, скрытые обстоятельства, намерения людей и возможный исход.

Хорарная астрология отвечает на любые конкретные вопросы:
- выйду ли я замуж за Пашу,
- куплю ли я эту квартиру,
- поступлю ли я в этот ВУЗ,
- будет ли мне комфортно в этом городе, этой стране и т.д.

Теперь подробно опиши свою ситуацию и задай конкретный вопрос🙏🏻

Для создания твоей индивидуальной астральной карты необходимо <b>твоя дата рождения и город</b> (из которого задаётся вопрос)
❗<u><b>пиши всё в одном сообщении</b></u>❗️.""",
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

🔮<b><i>Рассорка</i></b> — большие конфликты по мелочам в семье, так что после ссоры супруги думают, с чего вдруг они сорвались. Не видя друг друга, пара скучает, а как только встречаются, готовы друг друга испепелить по несущественным поводам.

🔮<b><i>Дьявольская красота</i></b> — это ритуал для раскрытия личной магнетики, харизмы и уверенности в себе. Он помогает принять свою красоту, почувствовать внутреннюю силу и начать проявляться ярче, благодаря чему человек становится более заметным, притягательным и уверенным в общении.""",
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

        magic_choice_menu.add(types.InlineKeyboardButton(
            text='ДЬЯВОЛЬСКАЯ КРАСОТА',
            callback_data='devil_beauty'))

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
            text="""Ты выбрал(-а): <b>МОРОК</b>.

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
            text="""Ты выбрал(-а): <b>ПРИВОРОТ</b>.

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
            text="""Ты выбрал(-а): <b>ПРИСУШКА</b>.

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
            text="""Ты выбрал(-а): <b>ПРИВЯЗКА</b>.

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
            text="""Ты выбрал(-а): <b>ОТВОРОТ/ОСТУДА</b>.

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
            text="""Ты выбрал(-а): <b>РАССОРКА</b>.

Теперь опиши свою ситуацию одним сообщением:

1. Между кем нужно создать конфликт;
2. Какие отношения между этими людьми;
3. Как давно они общаются;
4. Почему ты хочешь сделать рассорку;
5. Какой результат ты хочешь получить.

После этого я проведу анализ полученных данных...""",
            parse_mode='HTML'
        )

    elif call.data == 'devil_beauty':
        bot.send_message(
            call.message.chat.id,
            text="""Ты выбрал(-а): <b>ДЬЯВОЛЬСКАЯ КРАСОТА</b>.

Теперь опиши свою ситуацию одним сообщением:

1. Твое имя и дату рождения;
2. Что именно ты хочешь усилить в себе;
3. Есть ли сейчас неуверенность, зажимы или страх проявляться;
4. Какой результат ты хочешь получить.

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

        bot.send_message(

            call.message.chat.id,

            text=f"""<b>❗️ВНИМАНИЕ❗️</b>

Твой запрос на данный момент <b>в обработке</b>!
Потребуется <i>немного времени</i>, чтобы наша команда помогла тебе с ним.

<b>❗️ОТВЕТ ПОЛУЧАТ АБСОЛЮТНО ВСЕ</b>, просто <u>в порядке очереди</u>, поэтому придется немного подождать.

Чтобы получить все <b>бесплатно</b>, тебе необходимо подписаться на наших партнёров
<i>(поймите, полностью бесплатно работать — в ущерб себе, поэтому мы просим лишь подписку 💕)</i>

После <u>автоматической проверки подписки</u> в течение нескольких суток вам напишет <b>одна из наших пяти коллег</b>.
<i>Просим вас запастись терпением, так как вас много, а нас всего пятеро.</i>

<b>❗️БЕЗ ПОДПИСКИ НА ВСЕХ СПОНСОРОВ БОТ ВАМ НИЧЕГО НЕ ОТПРАВИТ❗️</b>


    {build_all_links_text()}""",

            parse_mode='HTML',

            disable_web_page_preview=True

        )

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
                'Ты подписался(-ась) не на всех обязательных каналах 💔',
                show_alert=True
            )

            bot.send_message(
                call.message.chat.id,
                text="""<b>Почти готово💘</b>

Я проверила подписку и вижу, что ты подписался(-ась) <b>не на всех обязательных каналах</b>.
Пожалуйста, подпишись на все каналы из списка ниже, а потом нажми кнопку:

<b>✅ Я подписался(-ась), проверить ещё раз</b>""",
                reply_markup=not_subscribed_menu,
                parse_mode='HTML'
            )
            return

        bot.send_message(
            call.message.chat.id,
            text="""<b>Спасибо!💘</b>

Твой запрос <b>принят</b> и поставлен в очередь на обработку.
⏳<u>Примерное время ожидания ответа:</u> <b>до 48 часов 31 минуты</b>.

<i>Я или одна из участниц моей команды обязательно вернёмся к твоему запросу, как только подойдёт твоя очередь.</i>

⚠️<u>Пожалуйста, не отписывайся от спонсоров до получения ответа.</u>

Если подписка будет отменена, бот может <b>не увидеть тебя в очереди</b>, и заявка автоматически потеряет приоритет :(
🔮<i>Энергообмен очень важен</i>, поэтому мы просим лишь <b>подписку на партнёров</b>💕

Если ты <u>не готов(-а) ждать бесплатный ответ</u> или хочешь получить помощь быстрее, ты можешь написать мне лично и заказать ритуал <b>на платной основе</b>.

📩<b>МОИ КОНТАКТЫ:</b> @tarotmarian""",
            parse_mode='HTML'
        )


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
    save_user(message.from_user.id)

    if message.from_user.id == ADMIN_ID:
        admin_state_value = admin_state.get(ADMIN_ID)

        if message.text == '❌ Отмена':
            admin_state[ADMIN_ID] = None
            broadcast_data.clear()

            bot.send_message(
                message.chat.id,
                'Действие отменено ❌\n\nСостояние сброшено, можешь выбрать новую команду.'
            )
            return

        if message.text == '🗑 Очистить список ссылок':
            PROMO_ITEMS.clear()
            save_promo_items(PROMO_ITEMS)

            bot.send_message(
                message.chat.id,
                'Список ссылок очищен ✅\n\nТеперь там нет ни одной промо-ссылки.'
            )
            return

        if message.text == '♻️ Сбросить 4 проверочных канала':
            REQUIRED_CHANNELS.clear()
            REQUIRED_CHANNELS.extend([dict(item) for item in DEFAULT_REQUIRED_CHANNELS])
            save_required_channels(REQUIRED_CHANNELS)

            bot.send_message(
                message.chat.id,
                'Проверочные каналы сброшены ✅\n\nОсталось только 4 стандартных канала.'
            )
            return
        if admin_state_value == 'waiting_import_list':
            items = parse_imported_list_message(message)

            if not items:
                bot.send_message(
                    message.chat.id,
                    'Не нашла ни одной номерной строки со ссылкой. Перешли именно оригинальное сообщение со списком.'
                )
                return

            PROMO_ITEMS.clear()
            PROMO_ITEMS.extend(items)
            save_promo_items(PROMO_ITEMS)

            admin_state[ADMIN_ID] = None

            bot.send_message(
                message.chat.id,
                f'Список ссылок успешно импортирован ✅\n\n'
                f'Добавлено пунктов: {len(items)}'
            )
            return

        if admin_state_value == 'waiting_required_channels':
            channels = parse_required_channels_text(message.text)

            if not channels:
                bot.send_message(
                    message.chat.id,
                    'Не получилось разобрать каналы. Пришли строки в формате:\n'
                    'Название | @username | https://t.me/username'
                )
                return

            REQUIRED_CHANNELS.clear()
            REQUIRED_CHANNELS.extend(channels)
            save_required_channels(REQUIRED_CHANNELS)

            admin_state[ADMIN_ID] = None

            bot.send_message(
                message.chat.id,
                f'Каналы для проверки сохранены ✅\n\n'
                f'Добавлено каналов: {len(channels)}'
            )
            return

        if message.text in ['📢 Сделать рассылку', '/broadcast']:
            admin_state[ADMIN_ID] = 'waiting_broadcast'

            bot.send_message(
                message.chat.id,
                'Отправь текст, фото или видео для рассылки.\n\n'
                'Если отправляешь фото или видео, можешь добавить подпись.'
            )
            return

        if message.text in ['📥 Импорт ссылок', '/importlist']:
            admin_state[ADMIN_ID] = 'waiting_import_list'

            bot.send_message(
                message.chat.id,
                'Перешли мне оригинальное сообщение со списком.\n\n'
                'Важно: мне нужен именно пересланный пост/сообщение, где ссылки кликабельные.\n'
                'Тогда я смогу вытащить их автоматически.'
            )
            return

        if message.text in ['⚙️ Каналы с проверкой', '/setrequired']:
            admin_state[ADMIN_ID] = 'waiting_required_channels'

            bot.send_message(
                message.chat.id,
                'Пришли 1-2 строки в формате:\n'
                'Название | @username | https://t.me/username\n\n'
                'Пример:\n'
                'МОЙ КАНАЛ | @tarotiz | https://t.me/tarotiz\n'
                'МОЙ ВТОРОЙ КАНАЛ | @wbmostril | https://t.me/wbmostril'
            )
            return

        if message.text == '📋 Показать ссылки':
            bot.send_message(
                message.chat.id,
                'Текущий список ссылок 👇'
            )
            send_long_html_message(message.chat.id, build_items_text(PROMO_ITEMS))
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
