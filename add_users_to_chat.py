import asyncio
import os
from telethon import TelegramClient
from telethon.errors import RPCError, ChatAdminRequiredError
from telethon.tl.functions.contacts import SearchRequest

# Конфигурация
API_ID = "*"
API_HASH = "*"
SESSIONS_DIR = "sessions"
FIRST_WORDS_FILE = "words/first_words.txt"
LAST_WORDS_FILE = "words/last_words.txt"
OUTPUT_FILE = "output.txt"
REQUEST_DELAY = 1.5  # Задержка между запросами для безопасности

async def search_public_chats():
    if not os.path.exists(SESSIONS_DIR):
        print("Папка с сессиями не найдена. Завершаю выполнение.")
        return

    # Загружаем ключевые слова
    if not os.path.exists(FIRST_WORDS_FILE) or not os.path.exists(LAST_WORDS_FILE):
        print("Файлы с ключевыми словами отсутствуют. Завершаю выполнение.")
        return

    with open(FIRST_WORDS_FILE, 'r', encoding='utf-8') as f:
        first_words = [line.strip() for line in f if line.strip()]

    with open(LAST_WORDS_FILE, 'r', encoding='utf-8') as f:
        last_words = [line.strip() for line in f if line.strip()]

    if not first_words and not last_words:
        print("Файлы с ключевыми словами пусты. Завершаю выполнение.")
        return

    session_files = [f"{SESSIONS_DIR}/{session}" for session in os.listdir(SESSIONS_DIR) if session.endswith(".session")]
    if not session_files:
        print("Сессии не найдены. Завершаю выполнение.")
        return

    async with TelegramClient(session_files[0], API_ID, API_HASH) as client:
        await client.connect()
        if not await client.is_user_authorized():
            print("Сессия не авторизована.")
            return

        found_chats = []

        # Поиск по ключевым словам
        for keyword in first_words + last_words:
            print(f"Ищу общедоступные чаты по ключевому слову: {keyword}")
            try:
                results = await client(SearchRequest(
                    q=keyword,         # Ключевое слово
                    limit=10           # Количество результатов
                ))
                for chat in results.chats:
                    # Проверяем доступ к участникам
                    try:
                        participants = await client.get_participants(chat)
                        if participants:
                            found_chats.append(f"{chat.title} ({chat.id}) - {chat.participants_count} участников")
                            print(f"Найден чат с доступом к участникам: {chat.title}, Участников: {chat.participants_count}")
                    except ChatAdminRequiredError:
                        print(f"Нет доступа к участникам чата: {chat.title}")
                    except Exception as e:
                        print(f"Ошибка при проверке доступа: {e}")
            except RPCError as e:
                print(f"Ошибка при поиске: {e}")

            # Задержка для безопасности
            await asyncio.sleep(REQUEST_DELAY)

        # Записываем результаты
        if found_chats:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                for chat in found_chats:
                    f.write(chat + "\n")
            print(f"Результаты записаны в файл {OUTPUT_FILE}")
        else:
            print("Общедоступные чаты не найдены.")

if __name__ == "__main__":
    asyncio.run(search_public_chats())



