import psycopg2
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
        vacancy_name = data['name']
        employer_id = int(data['employer']['id'])
        city = data.get('area').get('name')
        url = data['alternate_url']
        salary = 0 if data.get('salary') is None \
            else 0 if data.get('salary', {}).get('from') is None \
            else data.get('salary', {}).get('from')

        vacancy = (vacancy_id, vacancy_name, employer_id, city, salary, url)

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


class DBManager:
    """Класс для работы с базой данных, инициализируется названием базы данных и данными из конфигурационного файла"""

    def __init__(self, dbname: str, params: dict):
        self.dbname = dbname
        self.params = params

    def create_database(self) -> None:
        """Создает базу данных и таблицы"""
        # Подключаемся к postgres, чтобы создать БД
        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"DROP DATABASE IF EXISTS {self.dbname}")
        cur.execute(f"CREATE DATABASE {self.dbname}")

        cur.close()
        conn.close()

        # Подключаемся к созданной БД и создаем таблицы
        conn = psycopg2.connect(dbname=self.dbname, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""CREATE TABLE IF NOT EXISTS employers (
                                employer_id int PRIMARY KEY,
                                employer_name varchar(255) NOT NULL)""")

                    cur.execute("""CREATE TABLE IF NOT EXISTS vacancies (
                                vacancy_id int PRIMARY KEY, 
                                vacancy_name varchar(255) NOT NULL, 
                                employer_id int REFERENCES employers(employer_id) NOT NULL, 
                                city varchar(255), 
                                salary int,
                                url text)""")
        finally:
            conn.close()

    def insert(self, table: str, data: list) -> None:
        """Добавляет данные в таблицы базы данных"""
        conn = psycopg2.connect(dbname=self.dbname, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    if table == 'employers':
                        cur.executemany("""INSERT INTO employers(employer_id, employer_name)
                                        VALUES(%s, %s)""", data)
                    elif table == 'vacancies':
                        cur.executemany("""INSERT INTO vacancies (vacancy_id, vacancy_name, employer_id, city, salary, url)
                                        VALUES(%s, %s, %s, %s, %s, %s)
                                        ON CONFLICT (vacancy_id) DO NOTHING""", data)
        finally:
            conn.close()

    def execute_query(self, query: str) -> list:
        """Возвращает результат запроса"""
        conn = psycopg2.connect(dbname=self.dbname, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    result = cur.fetchall()

        finally:
            conn.close()
        return result

    def get_companies_and_vacancies_count(self) -> list:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        result = self.execute_query("""SELECT employer_name, COUNT(*) as quantity_vacancies
                                       FROM vacancies
                                       LEFT JOIN employers USING(employer_id)
                                       GROUP BY employer_name
                                       ORDER BY quantity_vacancies DESC, employer_name""")
        return result

    def get_all_vacancies(self) -> list:
        """ Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        result = self.execute_query("""SELECT employers.employer_name, vacancy_name, salary, url
                                        FROM vacancies
                                        JOIN employers USING(employer_id)
                                        ORDER BY salary DESC, vacancy_name""")
        return result

    def get_avg_salary(self) -> list:
        """ Получает среднюю зарплату по вакансиям"""
        result = self.execute_query("""SELECT ROUND(AVG(salary))
                                       FROM vacancies""")
        return result

    def get_vacancies_with_higher_salary(self) -> list:
        """ Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        result = self.execute_query("""SELECT vacancy_name, salary
                                       FROM vacancies
                                       WHERE salary > (SELECT AVG(salary) FROM vacancies)
                                       ORDER BY salary DESC, vacancy_name""")
        return result

    def get_vacancies_with_keyword(self, word: str) -> list:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        result = self.execute_query(f"""SELECT vacancy_name
                                     FROM vacancies
                                     WHERE vacancy_name ILIKE '%{word}%'
                                     ORDER BY vacancy_name""")
        return result
