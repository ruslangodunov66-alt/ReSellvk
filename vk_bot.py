import os
import sqlite3
from vkbottle import Bot
from vkbottle.bot import BotLabeler, Message

VK_TOKEN = os.getenv("VK_TOKEN")
if not VK_TOKEN:
    raise ValueError("VK_TOKEN not set")

DATA_DIR = os.getenv("DATA_DIR", "/app/data")
DB_PATH = os.path.join(DATA_DIR, "game.db")
os.makedirs(DATA_DIR, exist_ok=True)

labeler = BotLabeler()
bot = Bot(token=VK_TOKEN, labeler=labeler)

def get_or_create_player(vk_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nickname, balance FROM players WHERE vk_id = ?", (vk_id,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return {"id": row[0], "nickname": row[1], "balance": row[2]}
    nickname = f"VK_{vk_id}"
    cursor.execute("INSERT INTO players (vk_id, nickname, balance) VALUES (?, ?, ?)", (vk_id, nickname, 5000))
    conn.commit()
    player_id = cursor.lastrowid
    # Дополнительные таблицы (referrals, learning, skins) можно создать по необходимости
    conn.close()
    return {"id": player_id, "nickname": nickname, "balance": 5000}

@labeler.private_message(text="/start")
async def start_handler(message: Message):
    player = get_or_create_player(message.from_id)
    await message.answer(f"Добро пожаловать, {player['nickname']}!\n💰 Баланс: {player['balance']}₽")

@labeler.private_message(text="Баланс")
async def balance_handler(message: Message):
    player = get_or_create_player(message.from_id)
    await message.answer(f"💰 Ваш баланс: {player['balance']}₽")

if __name__ == "__main__":
    print("VK бот запущен")
    bot.run_forever()