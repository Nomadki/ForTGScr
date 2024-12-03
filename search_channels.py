import asyncio
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import InputPeerChannel, PeerChannel
from telethon.errors import ChatWriteForbiddenError
import os

# Папка и
api_id = '*'
api_hash = '*'
WORDS_FOLDER = "words"
FIRST_WORDS_FILE = os.path.join(WORDS_FOLDER, "first_words.txt")
LAST_WORDS_FILE = os.path.join(WORDS_FOLDER, "last_words.txt")
OUTPUT_FILE = "accessible_chats.txt"
SESSIONS_FOLDER = "sessions"

# Загрузка слов из файла
def load_words(file_path):
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

# Проверка доступности отправки сообщений
async def can_send_messages(client, chat):
    try:
        peer = await client.get_input_entity(chat)
        if isinstance(peer, InputPeerChannel) or isinstance(peer, PeerChannel):
            # Пробуем отправить сообщение
            await client.send_message(peer, "Проверка доступности сообщений", silent=True)
            return True
    except ChatWriteForbiddenError:
        return False
    except Exception as e:
        print(f"Ошибка при проверке доступности для {chat}: {e}")
    return False

# Основная функция поиска
async def search_accessible_chats():
    first_words = load_words(FIRST_WORDS_FILE)
    last_words = load_words(LAST_WORDS_FILE)

    if not first_words and not last_words:
        print("Нет ключевых слов для поиска. Завершение.")
        return

    # Загружаем сессии
    sessions = [os.path.join(SESSIONS_FOLDER, f) for f in os.listdir(SESSIONS_FOLDER) if f.endswith(".session")]
    if not sessions:
        print("Сессии не найдены.")
        return

    found_chats = []

    for session in sessions:
        print(f"Используется сессия: {session}")
        async with TelegramClient(session, api_id, api_hash) as client:
            for word in set(first_words + last_words):
                print(f"Поиск чатов по слову: {word}")
                results = await client(SearchRequest(
                    q=word,
                    limit=10
                ))

                for chat in results.chats:
                    if await can_send_messages(client, chat):
                        print(f"Добавлен доступный чат: {chat.title} ({chat.id})")
                        found_chats.append(f"{chat.title} - {chat.id}")

    # Сохраняем результаты
    if found_chats:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            file.write("\n".join(found_chats))
        print(f"Найдено чатов: {len(found_chats)}. Результаты сохранены в {OUTPUT_FILE}.")
    else:
        print("Не найдено чатов, в которые можно отправлять сообщения.")

# Запуск
if __name__ == "__main__":
    asyncio.run(search_accessible_chats())









