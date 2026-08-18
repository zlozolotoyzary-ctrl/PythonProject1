import os

from api import PetFriends
from env import valid_email, valid_password


pf = PetFriends()

# --- Тест 1: [GET] /api/key Запрос к API сервера, возвращает статус запроса и результат. ---
def test_get_api_key_for_valid_user(email=valid_email,password=valid_password):
    status,result = pf.get_api_key(email,password)
    assert status == 200
    assert 'key' in result
# --- Тест 2: [GET] /api/pets Запрос к API сервера, возвращает список питомцев. ---
def test_get_all_pets_with_valid_key(filter=""):
    _, auth_key = pf.get_api_key(valid_email,valid_password)
    status,result = pf.get_list_of_pets(auth_key,filter)
    assert status == 200
    assert len(result['pets']) > 0

def _get_auth_key_dict():
    """Возвращает ключ в формате {'key': '...'}, который ожидает класс PetFriends."""
    status, result = pf.get_api_key(valid_email, valid_password)
    assert status == 200, f"Не удалось получить API-ключ. Статус: {status}, ответ: {result}"
    assert 'key' in result, f"В ответе нет поля 'key'. Ответ: {result}"
    return {'key': result['key']}


def _get_auth_key_dict():
    status, result = pf.get_api_key(valid_email, valid_password)
    assert status == 200, f"Не удалось получить ключ. Статус: {status}"
    assert 'key' in result, "В ответе нет ключа"
    return {'key': result['key']}
# --- Тест 3: Добавление питомца (с реальной картинкой) ---
def test_add_new_pet():
    auth_key = _get_auth_key_dict()

    name = "Лёся"
    animal_type = "котяра"
    age = "40"

    # Путь к картинке
    photo_filename = "test_photo.jpg"
    pet_photo_path = os.path.join(os.getcwd(), photo_filename)

    # Проверка: если картинки нет, сразу падаем с понятным сообщением
    if not os.path.exists(pet_photo_path):
        pytest.fail(f"Файл '{photo_filename}' не найден! Положи его в папку проекта: {os.getcwd()}")

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo_path)

    assert status == 200, f"Ожидался статус 200, но получен {status}. Ответ: {result}"
    assert 'id' in result, f"В ответе нет ID. Ответ: {result}"
    assert result['name'] == name, f"Имя не совпадает. Ожидалось '{name}'"


# --- Тест 4: Удаление питомца ---
def test_delete_pet():
    auth_key = _get_auth_key_dict()

    # 1. Создаем питомца (обязательно с фото)
    name_to_delete = "Удаляемый_питомец"
    photo_filename = "test_photo.jpg"
    pet_photo_path = os.path.join(os.getcwd(), photo_filename)

    if not os.path.exists(pet_photo_path):
        pytest.fail(f"Файл '{photo_filename}' нужен для теста удаления.")

    status_create, pet = pf.add_new_pet(auth_key, name_to_delete, "собака", "2", pet_photo_path)
    assert status_create == 200 and 'id' in pet, f"Не удалось создать питомца. Ответ: {pet}"

    pet_id = pet['id']

    # 2. Удаляем его
    status_delete, result_delete = pf.delete_pet(auth_key, pet_id)
    assert status_delete == 200, f"Ошибка при удалении. Статус: {status_delete}, ответ: {result_delete}"

    # 3. Проверяем, что его нет в списке
    status_get, list_pets = pf.get_list_of_pets(auth_key, "")
    assert status_get == 200
    pets_ids = [p['id'] for p in list_pets.get('pets', [])]
    assert pet_id not in pets_ids, f"Питомец с ID '{pet_id}' всё ещё в списке!"


# --- Тест 5: Обновление информации о питомце ---
def test_update_pet_info():
    auth_key = _get_auth_key_dict()

    # 1. Создаем питомца
    name_initial = "Прежний_Лёсик"
    photo_filename = "test_photo.jpg"
    pet_photo_path = os.path.join(os.getcwd(), photo_filename)

    if not os.path.exists(pet_photo_path):
        pytest.fail(f"Файл '{photo_filename}' нужен для теста обновления.")

    status_create, pet = pf.add_new_pet(auth_key, name_initial, "кот", "55", pet_photo_path)
    assert status_create == 200 and 'id' in pet, "Не удалось создать питомца"

    pet_id = pet['id']
    new_name = "Новый_Лёсик"
    new_age = 6
    new_type = "персидский жмот"

    # 2. Обновляем данные
    status_update, result_update = pf.update_pet_info(
        auth_key,
        pet_id,
        new_name,
        new_type,
        new_age
    )

    assert status_update == 200, f"Ошибка при обновлении. Статус: {status_update}"
    assert result_update['name'] == new_name, f"Имя не обновилось. Ожидалось '{new_name}'"
    assert str(result_update['age']) == str(new_age), f"Возраст не обновился."
    assert result_update['id'] == pet_id, "ID питомца изменился!"

# --- Тест 6: POST /api/pets/set_photo/{pet_id} Загрузка фото для существующего питомца ---
def test_set_pet_photo():
    """Тест загрузки фото для существующего питомца (/api/pets/set_photo/{pet_id})"""
    auth_key = _get_auth_key_dict()

    # 1. Подготовка: имя файла и путь
    photo_filename = "test_photo.jpg"
    pet_photo_path = os.path.join(os.getcwd(), photo_filename)

    # ВАЖНАЯ ПРОВЕРКА: Если картинки нет, тест упадет сразу с понятным сообщением
    if not os.path.exists(pet_photo_path):
        pytest.fail(
            f"Файл '{photo_filename}' не найден!\n"
            f"Положи картинку в папку: {os.getcwd()}\n"
            f"Без неё тест set_pet_photo не может работать."
        )

    # 2. Создаем питомца, на которого будем ставить фото
    name_to_create = "ФотоКот_Тестовый"
    animal_type = "кот"
    age = "5"

    status_create, pet = pf.add_new_pet(
        auth_key,
        name_to_create,
        animal_type,
        age,
        pet_photo_path  # При создании тоже нужна картинка
    )

    assert status_create == 200, f"Не удалось создать питомца для теста. Статус: {status_create}, ответ: {pet}"
    assert 'id' in pet, "В ответе от создания питомца нет поля 'id'"

    pet_id = pet['id']
    print(f" Питомец создан. ID: {pet_id}")

    # 3. Загружаем фото через новый метод set_pet_photo
    # Можно использовать ту же самую картинку или другую
    status_upload, result_upload = pf.set_pet_photo(auth_key, pet_id, pet_photo_path)

    # 4. Проверки результата
    assert status_upload == 200, (
        f"Ожидался статус 200 при загрузке фото, но получен {status_upload}.\n"
        f"Ответ сервера: {result_upload}"
    )

    # Сервер обычно возвращает объект питомца с обновленным полем pet_photo
    assert 'pet_photo' in result_upload or 'id' in result_upload, (
        f"Странный формат ответа сервера. Ожидалось поле 'pet_photo' или 'id', а получено: {result_upload}"
    )

    print(f" Фото успешно загружено для питомца ID: {pet_id}")
    print(f"Ответ сервера: {result_upload}")


import os
import pytest
from api import PetFriends
from env import valid_email, valid_password

pf = PetFriends()


def _get_auth_key_dict():
    """Вспомогательная функция для получения ключа авторизации."""
    status, result = pf.get_api_key(valid_email, valid_password)
    assert status == 200, f"Не удалось получить ключ. Статус: {status}"
    assert 'key' in result, "В ответе нет ключа"
    return {'key': result['key']}


# --- Тест 7: Неверный пароль ---
def test_get_api_key_with_wrong_password():
    """Пытаемся получить ключ с неверным паролем."""
    status, result = pf.get_api_key(valid_email, "wrong_password_123")
    assert status != 200
    print("Тест пройден: неверный пароль отклонен.")


# --- Тест 8: Пустое имя при создании ---
def test_add_pet_with_empty_name():
    """Создаем питомца с пустым именем."""
    auth_key = _get_auth_key_dict()
    photo_path = os.path.join(os.getcwd(), "test_photo.jpg")

    if not os.path.exists(photo_path):
        pytest.skip("Нет картинки 'test_photo.jpg' для теста")

    status, result = pf.add_new_pet(auth_key, "", "собака", "5", photo_path)
    assert status == 400
    print("Тест пройден: пустое имя отклонено.")


# --- Тест 9: Длинное имя (граничные значения) ---
def test_add_pet_with_long_name():
    """Имя длиной 255 символов."""
    auth_key = _get_auth_key_dict()
    photo_path = os.path.join(os.getcwd(), "test_photo.jpg")
    long_name = "A" * 255

    if not os.path.exists(photo_path):
        pytest.skip("Нет картинки 'test_photo.jpg' для теста")

    status, result = pf.add_new_pet(auth_key, long_name, "кот", "1", photo_path)
    assert status in [200, 400]
    print(f"Тест пройден: реакция на длинное имя (статус {status}).")


# --- Тест 10: Получение всех питомцев ---
def test_get_all_pets():
    """Получаем полный список питомцев."""
    auth_key = _get_auth_key_dict()
    status, result = pf.get_list_of_pets(auth_key)

    assert status == 200
    assert isinstance(result, dict)
    assert 'pets' in result
    assert isinstance(result['pets'], list)
    print(f"Тест пройден: получено {len(result['pets'])} питомцев.")


# --- Тест 11: Фильтр 'my_pets' ---
def test_get_my_pets_filter():
    """Проверяем фильтр 'my_pets'."""
    auth_key = _get_auth_key_dict()
    status, result = pf.get_list_of_pets(auth_key, pet_filter="my_pets")

    assert status == 200
    assert 'pets' in result and isinstance(result['pets'], list)
    print("Тест пройден: фильтр 'my_pets' работает.")


# --- Тест 12: Отрицательный возраст (негативный) ---
def test_update_pet_age_negative():
    """Пробуем установить отрицательный возраст."""
    auth_key = _get_auth_key_dict()
    photo_path = os.path.join(os.getcwd(), "test_photo.jpg")

    if not os.path.exists(photo_path):
        pytest.skip("Нет картинки 'test_photo.jpg' для теста")

    # Создаем питомца
    status_create, pet = pf.add_new_pet(auth_key, "GrumpyCat", "кот", "3", photo_path)
    assert status_create == 200 and 'id' in pet
    pet_id = pet['id']

    # Пытаемся обновить возраст на -10
    status_update, result = pf.update_pet_info(auth_key, pet_id, "GrumpyCat", "кот", -10)
    assert status_update == 400
    print("Тест пройден: отрицательный возраст отклонен.")


# --- Тест 13: Удаление несуществующего питомца ---
def test_delete_non_existent_pet():
    """Пытаемся удалить питомца с фейковым ID."""
    auth_key = _get_auth_key_dict()
    fake_id = "00000000-0000-0000-0000-000000000000"

    status, result = pf.delete_pet(auth_key, fake_id)
    assert status != 200
    assert status != 500
    print(f"Тест пройден: попытка удаления несуществующего ID обработана (статус {status}).")


# --- Тест 14: Уникальность ID ---
def test_pet_ids_are_unique():
    """Создаем двух питомцев и проверяем уникальность ID."""
    auth_key = _get_auth_key_dict()
    photo_path = os.path.join(os.getcwd(), "test_photo.jpg")

    if not os.path.exists(photo_path):
        pytest.skip("Нет картинки 'test_photo.jpg' для теста")

    _, pet1 = pf.add_new_pet(auth_key, "First", "dog", "1", photo_path)
    _, pet2 = pf.add_new_pet(auth_key, "Second", "cat", "2", photo_path)

    id1 = pet1['id']
    id2 = pet2['id']

    assert id1 != id2
    print(f"Тест пройден: ID уникальны. {id1[:8]}... != {id2[:8]}...")


# --- Тест 15: Структура JSON ответа ---
def test_response_structure_is_valid():
    """Проверяем структуру ответа при создании питомца."""
    auth_key = _get_auth_key_dict()
    photo_path = os.path.join(os.getcwd(), "test_photo.jpg")

    if not os.path.exists(photo_path):
        pytest.skip("Нет картинки 'test_photo.jpg' для теста")

    # 1. Создаем питомца
    status, result = pf.add_new_pet(auth_key, "StructTest", "bird", "2", photo_path)
    assert status == 200, f"Не удалось создать питомца. Статус: {status}"
    assert isinstance(result, dict), "Ответ сервера должен быть словарем (JSON)"

    required_keys = ['id', 'name', 'animal_type', 'age']

    # 2. Проверяем наличие всех обязательных ключей
    for key in required_keys:
        assert key in result, f"В ответе отсутствует обязательное поле '{key}'"

    # 3. Проверяем типы данных
    assert isinstance(result['name'], str), "Поле 'name' должно быть строкой"
    # Возраст может прийти строкой ("2") или числом (2), проверяем оба варианта
    assert isinstance(result['age'], (str, int)), "Поле 'age' должно быть строкой или числом"

    print(f"Структура ответа валидна. Ключи найдены: {required_keys}")

    # 4. ЧИСТКА: Удаляем тестового питомца, чтобы не копился мусор
    pet_id = result['id']
    del_status, _ = pf.delete_pet(auth_key, pet_id)
    if del_status == 200:
        print(f"Тестовый питомец ID: {pet_id} успешно удален.")
    else:
        print(f"Не удалось автоматически удалить питомца ID: {pet_id}. Придется удалить вручную.")


