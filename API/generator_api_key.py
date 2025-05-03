import secrets
import string
import hashlib
from datetime import datetime, timedelta


def generate_api_key(length=32):
    """Генерация случайного API ключа"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_secure_api_key(prefix='api_'):
    """Генерация более безопасного API ключа с хешированием"""
    # Генерируем случайную строку
    random_string = secrets.token_hex(32)
    # Добавляем временную метку для уникальности
    timestamp = str(datetime.utcnow().timestamp())
    # Создаем хеш
    hash_object = hashlib.sha256((random_string + timestamp).encode())
    # Возвращаем ключ с префиксом
    return prefix + hash_object.hexdigest()


def generate_api_key_with_expiry(days=30, prefix='api_'):
    """Генерация API ключа с указанием срока действия"""
    # Генерируем ключ
    key = generate_secure_api_key(prefix)
    # Вычисляем дату истечения срока
    expiry_date = datetime.utcnow() + timedelta(days=days)
    return {
        'api_key': key,
        'expires_at': expiry_date.isoformat()
    }


if __name__ == "__main__":
    print("Простой API ключ:", generate_api_key())
    print("\nБезопасный API ключ:", generate_secure_api_key())

    key_with_expiry = generate_api_key_with_expiry()
    print("\nAPI ключ с сроком действия:")
    print("Ключ:", key_with_expiry['api_key'])
    print("Истекает:", key_with_expiry['expires_at'])