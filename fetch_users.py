import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Telegram API данные
api_id = '*'
api_hash = '*'

# Название сессии
session_name = input("Введите название сессии (без .session): ")
session_path = os.path.join('sessions', f"{session_name}.session")

# Файл для сохранения пользователей
USERS_FILE = 'users.txt'

client = TelegramClient(session_path, api_id, api_hash)


async def fetch_users_from_group(group_link):
    """Собирает пользователей из общедоступной группы по её ссылке."""
    await client.connect()

    if not await client.is_user_authorized():
        print("Сессия не авторизована.")
        return

    try:
        # Получаем сущность группы (канала)
        group = await client.get_entity(group_link)

        # Проверка на тип сущности: должна быть группа или канал
        if not hasattr(group, 'username'):
            print(f"Ошибка: не удалось получить группу/канал по ссылке '{group_link}'.")
            return

        # Проверка, является ли объект каналом или супергруппой
        if hasattr(group, 'megagroup') and group.megagroup:
            print(f"Получаем участников из группы: {group.title}")
        else:
            print(f"Получаем участников из канала: {group.title}")

        # Сбор всех участников
        participants = await client.get_participants(group)

        print(f"Найдено {len(participants)} участников.")
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            for user in participants:
                username = user.username if user.username else f"Без_имени_{user.id}"
                f.write(f"{username}\n")
                print(f"Сохранён пользователь: {username}")

        print(f"Участники успешно сохранены в {USERS_FILE}.")

    except SessionPasswordNeededError:
        print("Требуется ввод пароля для двухфакторной аутентификации.")
    except Exception as e:
        print(f"Ошибка при сборе участников: {e}")


with client:
    group_link = input("Введите ссылку на группу или канал (например, https://t.me/example): ")
    client.loop.run_until_complete(fetch_users_from_group(group_link))




