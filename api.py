import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from typing import Any, Dict, Tuple

class PetFriends:
    """API библиотека к веб приложению Pet Friends"""

    def __init__(self):
        self.base_url = "https://petfriends.skillfactory.ru/"

    def get_api_key(self, email: str, passwd: str) -> Tuple[int, Any]:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат."""
        headers = {
            'email': email,
            'password': passwd,
        }
        try:
            res = requests.get(self.base_url + 'api/key', headers=headers)
        except requests.RequestException as e:
            return 500, {"error": str(e)}

        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def get_list_of_pets(self, auth_key: Dict[str, str], pet_filter: str = "") -> Tuple[int, Any]:
        """Метод делает запрос к API сервера и возвращает список питомцев."""
        headers = {'auth_key': auth_key['key']}
        params = {'filter': pet_filter} if pet_filter else {}

        try:
            res = requests.get(self.base_url + 'api/pets', headers=headers, params=params)
        except requests.RequestException as e:
            return 500, {"error": str(e)}

        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_new_pet(self, auth_key: Dict[str, str], name: str, animal_type: str,
                    age: str, pet_photo: str) -> Tuple[int, Any]:
        """Метод отправляет на сервер данные о добавляемом питомце."""
        import os

        # Вариант 1: Если фото нет или файл не найден -> простой запрос
        if not pet_photo or not os.path.exists(pet_photo):
            data = {
                'name': name,
                'animal_type': animal_type,
                'age': age
            }
            headers = {'auth_key': auth_key['key'], 'Content-Type': 'application/x-www-form-urlencoded'}
            post_data = data
        else:
            # Вариант 2: Если фото есть -> Multipart запрос
            # Читаем файл сразу в память (байты), чтобы избежать проблемы "закрытого файла"
            with open(pet_photo, 'rb') as f:
                photo_bytes = f.read()

            encoder = MultipartEncoder(
                fields={
                    'name': name,
                    'animal_type': animal_type,
                    'age': age,
                    # Передаем байты напрямую. Это безопасно.
                    'pet_photo': ('pet_photo', photo_bytes, 'image/jpeg')
                }
            )
            headers = {'auth_key': auth_key['key'], 'Content-Type': encoder.content_type}
            post_data = encoder

        try:
            res = requests.post(self.base_url + 'api/pets', headers=headers, data=post_data)
        except requests.RequestException as e:
            return 500, {"error": str(e)}

        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def delete_pet(self, auth_key: Dict[str, str], pet_id: str) -> Tuple[int, Any]:
        """Метод удаляет питомца по ID."""
        headers = {'auth_key': auth_key['key']}

        try:
            res = requests.delete(self.base_url + 'api/pets/' + pet_id, headers=headers)
        except requests.RequestException as e:
            return 500, {"error": str(e)}

        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def update_pet_info(self, auth_key: Dict[str, str], pet_id: str, name: str,
                        animal_type: str, age: int) -> Tuple[int, Any]:
        """Метод обновляет данные питомца по ID."""
        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'age': str(age),
            'animal_type': animal_type
        }

        try:
            res = requests.put(self.base_url + 'api/pets/' + pet_id, headers=headers, data=data)
        except requests.RequestException as e:
            return 500, {"error": str(e)}

        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def set_pet_photo(self, auth_key: Dict[str, str], pet_id: str, pet_photo: str) -> Tuple[int, Any]:
        """Метод загружает фото для питомца по ID."""
        import os

        # Проверка: файл должен существовать
        if not pet_photo or not os.path.exists(pet_photo):
            return 400, {"error": "Файл изображения не найден"}

        # Читаем файл в байты (как и в add_new_pet, чтобы избежать ошибки закрытого файла)
        with open(pet_photo, 'rb') as f:
            photo_bytes = f.read()

        encoder = MultipartEncoder(
            fields={
                'pet_photo': ('pet_photo', photo_bytes, 'image/jpeg')
            }
        )

        headers = {
            'auth_key': auth_key['key'],
            'Content-Type': encoder.content_type
        }

        try:
            # URL именно такой: /api/pets/set_photo/{pet_id}
            res = requests.post(self.base_url + f'api/pets/set_photo/{pet_id}', headers=headers, data=encoder)
        except requests.RequestException as e:
            return 500, {"error": str(e)}

        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text

        return status, result
