import asyncio
import sqlite3
import os
from vkbottle import Bot
from vkbottle.bot import BotLabeler, Message

# --- Настройки ---
# Получаем путь к общей папке для данных из переменной окружения.
# Если переменной нет, используем папку по умолчанию внутри контейнера.
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
DB_PATH = os.path.join(DATA_DIR, "game.db")

labeler = BotLabeler()
# Токен будет взят из переменной окружения VK_TOKEN, которую мы создадим на хостинге.
bot = Bot(token=os.getenv("VK_TOKEN"), labeler=labeler)

# --- Функции для работы с базой данных ---
def get_player(vk_id):
    """Получить данные игрока по его VK ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nickname, balance, total_sales FROM players WHERE vk_id = ?", (vk_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def create_player(vk_id, nickname):
    """Создать нового игрока, если он ещё не зарегистрирован."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO players (vk_id, nickname, shop_name, balance) VALUES (?, ?, ?, ?)",
        (vk_id, nickname, "Моя лавка", 5000)
    )
    conn.commit()
    player_id = cursor.lastrowid
    # Добавляем необходимые записи в служебные таблицы
    cursor.execute("INSERT INTO referrals (player_id) VALUES (?)", (player_id,))
    cursor.execute("INSERT INTO learning (player_id) VALUES (?)", (player_id,))
    cursor.execute("INSERT INTO skins (player_id, skin_id, equipped) VALUES (?, 'default', 1)", (player_id,))
    conn.commit()
    conn.close()
    return player_id

# --- Обработчики команд ---
@labeler.private_message(text="/start")
async def start_handler(message: Message):
    vk_id = message.from_id
    player = get_player(vk_id)
    if not player:
        # Игрок новый, создаём запись
        nickname = f"VK_{vk_id}"
        create_player(vk_id, nickname)
        await message.answer("🎉 Добро пожаловать в Resell Tycoon!\nВаш баланс: 5000₽\nИспользуйте кнопки меню ниже.")
    else:
        # Игрок уже существует
        await message.answer(f"👋 С возвращением, {player[1]}!\n💰 Ваш баланс: {player[2]}₽\n📦 Продано товаров: {player[3]}")

@labeler.private_message(text="Баланс")
async def balance_handler(message: Message):
    vk_id = message.from_id
    player = get_player(vk_id)
    if player:
        await message.answer(f"💰 Ваш баланс: {player[2]}₽")
    else:
        await message.answer("❌ Вы не зарегистрированы. Напишите /start")

# --- Запуск бота ---
if __name__ == "__main__":
    print("🤖 VK бот запущен")
    bot.run_forever()