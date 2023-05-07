import json


def read_json(file) -> list:
    """Читает json-файл"""
    with open(file, 'r', encoding='UTF-8') as file:
        data = json.load(file)
    return data


def get_employers(data: list) -> list:
    """Получает список кортежей из списка словарей"""
    employers = []
    for item in data:
        employers.append((item['id'], item['title']))
    return employers

