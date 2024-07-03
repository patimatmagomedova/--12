import logging
import aiosqlite
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from test import quiz_data
from db import get_quiz_index, update_quiz_index, update_score

DB_NAME = 'quiz_bot.db'
user_scores = {}

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )
    builder.adjust(1)
    return builder.as_markup()

async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"{quiz_data[current_question_index]['options'][correct_option]} - Верный ответ!")

    # Обновление результата и номера текущего вопроса в базе данных
    current_question_index += 1
    user_id = callback.from_user.id
    # Инициализация счётчика sc, если его ещё нет
    if user_id not in user_scores:
        user_scores[user_id] = 0
    user_scores[user_id] += 1
    sc = user_scores[user_id]

    await update_quiz_index(user_id, current_question_index)
    update_result = await update_score(user_id, sc)  # Обновление результата с использованием счётчика
    logging.info(f"Update score result: {update_result}")

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Показать статистику"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    user_scores[user_id] = 0  # Сброс счётчика при начале нового квиза
    await update_quiz_index(user_id, current_question_index)
    await update_score(user_id, 0)  # Сброс счётчика в базе данных
    await get_question(message, user_id)

async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            logging.info(f"Fetched score for user {user_id}: {result}")
            if result:
                await message.answer(f"Ваш результат: {result[0]} правильных ответов.")
            else:
                await message.answer("У вас пока нет результатов.")
