from telethon import TelegramClient
import os

# Ваши API ID и Hash
api_id = input("Введите API ID: ")
api_hash = input("Введите API Hash: ")

# Название сессии
session_name = input("Введите название для сессии (без .session): ")
session_path = os.path.join('sessions', f"{session_name}.session")

# Проверка папки для хранения сессий
if not os.path.exists('sessions'):
    os.makedirs('sessions')

# Инициализация клиента
client = TelegramClient(session_path, api_id, api_hash)


async def authorize():
    await client.connect()

    # Если пользователь ещё не авторизован
    if not await client.is_user_authorized():
        phone = input("Введите номер телефона: ")
        await client.send_code_request(phone)

        code = input("Введите код из Telegram: ")
        try:
            await client.sign_in(phone, code)
            print(f"Авторизация завершена. Сессия сохранена как {session_path}")
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
    else:
        print("Пользователь уже авторизован.")

    await client.disconnect()


with client:
    client.loop.run_until_complete(authorize())
