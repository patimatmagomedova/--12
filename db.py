import aiosqlite
import logging

DB_NAME = 'quiz_bot.db'

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()

async def update_score(user_id, score):
    async with aiosqlite.connect(DB_NAME) as db:
        logging.info(f"Updating score for user {user_id} to {score}")
        await db.execute('UPDATE quiz_state SET score = ? WHERE user_id = ?', (score, user_id))
        await db.commit()
        # Проверка после обновления
        async with db.execute('SELECT score FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            logging.info(f"Score after update for user {user_id}: {result}")
            return result  # Возвращаем результат для проверки

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
                            user_id INTEGER PRIMARY KEY,
                            question_index INTEGER,
                            score INTEGER DEFAULT 0)''')
        await db.commit()

async def check_database():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM quiz_state') as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                logging.info(f"Database row: {row}")
