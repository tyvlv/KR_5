import json

import requests
import time


class HH:
    """Класс получения вакансий с сайта hh.ru"""

    URL = 'https://api.hh.ru/vacancies'

    def __init__(self, search: int):
        self.search = search
        self.params = {'employer_id': f'{self.search}',  # подстановка id работодателя
                       'page': 0,  # Количество страниц поиска
                       'per_page': 100  # Количество вакансий на одной странице
                       }
        self.vacancy_list = []

    def get_request(self) -> list:
        """Получает информацию через API"""

        try:
            response = requests.get(self.URL, self.params)
            if response.status_code == 200:
                return response.json()

        except requests.RequestException:
            print('Не удается получить данные')

    @staticmethod
    def get_info(data: dict) -> tuple:
        """Выбирает нужную информацию о вакансии"""

        vacancy_id = int(data['id'])
        name = data['name']
        employer_id = int(data['employer']['id'])
        city = data.get('area').get('name')
        url = data['alternate_url']
        salary = 0 if data.get('salary') is None \
            else 0 if data.get('salary', {}).get('from') is None \
            else data.get('salary', {}).get('from')

        vacancy = (vacancy_id, name, employer_id, city, salary, url)

        return vacancy

    def get_vacancies(self) -> list:
        """Формирует список вакансий"""

        while True:
            data = self.get_request()

            for vacancy in data.get('items'):
                if vacancy.get('salary') is not None and vacancy.get('salary').get('currency') is not None:
                    # если зп рубли, добавляем в список, если нет, пропускаем
                    if vacancy.get('salary').get('currency') == "RUR":
                        self.vacancy_list.append(self.get_info(vacancy))
                    else:
                        continue

                # если зп не указана, добавляем в список
                else:
                    self.vacancy_list.append(self.get_info(vacancy))

            self.params['page'] += 1
            time.sleep(0.2)

            # если была последняя страница, заканчиваем сбор данных
            if data.get('pages') == self.params['page']:
                break

        return self.vacancy_list


# hh = HH(3776)
# print(json.dumps(hh.get_request(), indent=2, ensure_ascii=False))
#
# print(json.dumps(hh.get_vacancies(), indent=2, ensure_ascii=False))
# print(len(hh.vacancy_list))
