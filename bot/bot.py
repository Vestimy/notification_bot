from os import getenv
import random
import uuid
import typing
import logging
import asyncio
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, Throttled

from models import Users, Schedule, ConcertHall
from config import Config

from templates import my_func
from get_sheets import GetSheets

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Config.API_TOKEN, parse_mode=types.ParseMode.HTML)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

sheets = GetSheets(filename='mypythonsheets-339911-57bc2e8e8e89.json', table_key=Config.GOOGLE_KEY)


# States
class Register(StatesGroup):
    first_name = State()
    last_name = State()  # Will be represented in storage as 'Form:name'
    alias = State()  # Will be represented in storage as 'Form:age'
    bool = State()  # Will be represented in storage as 'Form:gender'


POSTS = {
    str(uuid.uuid4()): {
        'title': f'Post {index}',
        'body': 'Lorem ipsum dolor sit amet, '
                'consectetur adipiscing elit, '
                'sed do eiusmod tempor incididunt ut '
                'labore et dolore magna aliqua',
        'votes': random.randint(-2, 5),
    } for index in range(1, 6)
}

posts_cb = CallbackData('post', 'id', 'action')  # post:<id>:<action>


def get_keyboard(data) -> types.InlineKeyboardMarkup:
    """
    Generate keyboard with list of posts
    """
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row_width = 2
    for item in data:
        markup.add(
            types.InlineKeyboardButton(
                item.title,
                callback_data=posts_cb.new(id=item.id, action='view')),
        )

    markup.row_width = data.page_count
    markup.row()
    for i in range(1, data.page_count + 1):
        if i == data.page:
            msg = f'❗{i}'
        else:
            msg = i
        if i > 8:
            markup.row()
        markup.insert(types.InlineKeyboardButton(msg, callback_data=posts_cb.new(id=i, action='item')))

    markup.row()
    if data.previous_page is not None:
        markup.insert(
            types.InlineKeyboardButton('👈', callback_data=posts_cb.new(id=data.previous_page, action='prev')))

    if data.next_page is not None:
        markup.insert(types.InlineKeyboardButton('👉', callback_data=posts_cb.new(id=data.next_page, action='next')))
    return markup


def format_post(post_id: str, post: dict) -> (str, types.InlineKeyboardMarkup):
    text = md.text(post.title,
                   md.text(post.city),
                   md.text(post.adress),
                   md.text(post.note),
                   md.text(post.contact_person),
                   # '',  # just new empty line
                   # f"Votes: {post['votes']}",
                   sep='\n',
                   )

    result = Schedule.get_by_number_of_days(7)
    text = my_func('playground_view.html', post=post)

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton('👍', callback_data=posts_cb.new(id=post_id, action='like')),
        types.InlineKeyboardButton('👎', callback_data=posts_cb.new(id=post_id, action='dislike')),
    )
    markup.add(types.InlineKeyboardButton('<< Back', callback_data=posts_cb.new(id='-', action='list')))
    return text, markup


@dp.message_handler(commands=['start', 'старт'])
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    if not Users.user_exists(message.from_user.id):
        await Register.first_name.set()
        await message.answer('Для начанала нужно зарегистрироваться!')
        await message.answer("Введите имя: ")


@dp.message_handler(commands=['week', 'неделя'])
async def cmd_week(message: types.Message):
    result = Schedule.get_by_number_of_days(7)
    await message.answer(my_func('index.html', glist=result))


@dp.message_handler(commands=['playground', 'площадки'])
async def cmd_test(message: types.Message):
    await message.answer('Posts', reply_markup=get_keyboard(ConcertHall.get_paginate_all()))


@dp.callback_query_handler(posts_cb.filter(action='list'))
async def query_show_list(query: types.CallbackQuery):
    await query.message.edit_text('Posts', reply_markup=get_keyboard(ConcertHall.get_paginate_all()))


@dp.callback_query_handler(posts_cb.filter(action='view'))
async def query_view(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    post_id = callback_data['id']

    post = ConcertHall.get_one_hall(post_id)
    if not post:
        return await query.answer('Unknown post!')

    text, markup = format_post(post_id, post)
    await query.message.edit_text(text, reply_markup=markup)


@dp.callback_query_handler(posts_cb.filter(action=['like', 'dislike']))
async def query_post_vote(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    try:
        await dp.throttle('vote', rate=1)
    except Throttled:
        return await query.answer('Too many requests.')

    post_id = callback_data['id']
    action = callback_data['action']

    post = POSTS.get(post_id, None)
    if not post:
        return await query.answer('Unknown post!')

    if action == 'like':
        post['votes'] += 1
    elif action == 'dislike':
        post['votes'] -= 1

    await query.answer('Vote accepted')
    text, markup = format_post(post_id, post)
    await query.message.edit_text(text, reply_markup=markup)


@dp.callback_query_handler(posts_cb.filter(action=['prev', 'next', 'item']))
async def query_post_vote(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    action = callback_data['action']
    next_page = callback_data['id']
    if action == 'next':
        await query.message.edit_text('Posts', reply_markup=get_keyboard(ConcertHall.get_paginate_all(page=next_page)))
    if action == 'prev':
        await query.message.edit_text('Posts', reply_markup=get_keyboard(ConcertHall.get_paginate_all(page=next_page)))
    if action == 'item':
        await query.message.edit_text('Posts', reply_markup=get_keyboard(ConcertHall.get_paginate_all(page=next_page)))


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Register.first_name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['first_name'] = message.text

    await Register.next()
    await message.answer("Введите фамилию: ")


@dp.message_handler(state=Register.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['last_name'] = message.text

    await Register.next()
    await message.answer("Введите короткую фамилию, из колонки исполнители например 'Вест' или 'БахмМ: ")


# Check age. Age gotta be digit
# @dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
@dp.message_handler(lambda message: not Users.get_exists_alias(message.text), state=Register.alias)
async def process_age_invalid(message: types.Message):
    """
    If age is invalid
    """
    return await message.answer("Введите короткую фамилию, из колонки исполнители")


@dp.message_handler(lambda message: Users.get_exists_alias(message.text), state=Register.alias)
async def process_age(message: types.Message, state: FSMContext):
    # Update state and data
    await Register.next()
    await state.update_data(alias=message.text)

    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Да", "Нет")
    # markup.add("Other")

    await message.reply("Хотите получать все изменения из таблицы", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ["Да", "Нет"], state=Register.bool)
async def process_gender_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply("Нажмите: ")


@dp.message_handler(state=Register.bool)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['bool'] = message.text

        # Remove keyboard
        markup = types.ReplyKeyboardRemove()
        Users.set_new_user(message.from_user.id,
                           data['first_name'],
                           data['last_name'],
                           data['alias'],
                           data['bool'] == 'Да')
        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Добро пожаловать,', md.bold(data['first_name'])),
                md.text('Имя:', md.code(data['first_name'])),
                md.text('Фамилия:', md.code(data['last_name'])),
                md.text('Сокращенное:', data['alias']),
                md.text('Все изменения:', data['bool']),
                md.text('Расписание на неделю: /week'),
                md.text('Список площадок: /playground'),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    # Finish conversation
    await state.finish()


# async def gg():
#     await bot.send_message(921318107, 'Првет')


@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


def get_update_sheets():
    results = sheets.get_sheet_table()
    results = sheets.search_data_changes_sheet(results)
    results = sheets.chech_in(results)
    return results


async def update_price():
    result = get_update_sheets()
    newsletter_alias = []
    not_newsletter = {}
    if result is not None:
        for i in result:
            res, _ = i
            executors = res.executor.split(' ')
            for executor in executors:
                user = Users.get_alias(executor) or Users.get_user_alias_for_last_name(executor)
                if user and user.newsletter is False:
                    if not user.user_id in not_newsletter.keys():
                        not_newsletter[user.user_id] = [i]
                    else:
                        not_newsletter.get(user.user_id).append(i)

        for user_id in not_newsletter:
            await bot.send_message(user_id, my_func('sheets_update.html', glist=not_newsletter.get(user_id)))
        users = Users.get_all_newsletter()
        for user in users:
            newsletter_alias.append(user.alias)
            await bot.send_message(user.user_id, my_func('sheets_update.html', glist=result))


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(DELAY, repeat, coro, loop)


if __name__ == '__main__':
    print(Config.DELAY)
    DELAY = Config.DELAY
    loop = asyncio.get_event_loop()
    loop.call_later(DELAY, repeat, update_price, loop)
    executor.start_polling(dp, skip_updates=True, loop=loop)
