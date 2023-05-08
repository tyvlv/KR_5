from classes import DBManager, HH
from config import config
from utils import read_json, get_employers

PATH_TO_EMPLOYERS = 'data/employers.json'
PATH_TO_DBiniFile = 'data/database.ini'


def main():
    params = config(PATH_TO_DBiniFile)
    db = DBManager('headhunter', params)
    while True:
        print("Создать/обновить БД и таблицы данными о вакансиях с hh.ru?\n1 - Да\n2 - Нет")
        user_choice = input()
        if user_choice == '1':
            db.create_database()

            employers = get_employers(read_json(PATH_TO_EMPLOYERS))
            db.insert('employers', employers)

            for i in range(len(employers)):
                hh = HH(employers[i][0]).get_vacancies()
                db.insert('vacancies', hh)
            break
        elif user_choice == '2':
            break
        else:
            print("Введите '1' или '2'")

    while True:
        print("""Какие данные предоставить?\n\
1 - вывести список всех компаний и количество вакансий у каждой компании\n\
2 - вывести список всех вакансий\n\
3 - вывести среднюю зарплату по вакансиям\n\
4 - вывести список всех вакансий, у которых зарплата выше средней по всем вакансиям\n\
5 - вывести список всех вакансий, в названии которых содержатся переданное в метод слово\n\
любая другая клавиша - закончить работу""")
        user_method_choice = input()
        if user_method_choice == '1':
            for item in db.get_companies_and_vacancies_count():
                print(item)

        elif user_method_choice == '2':
            for item in db.get_all_vacancies():
                print(item)

        elif user_method_choice == '3':
            print(f"Средняя зарплата - {db.get_avg_salary()[0][0]} руб.")

        elif user_method_choice == '4':
            for item in db.get_vacancies_with_higher_salary():
                print(item)

        elif user_method_choice == '5':
            keyword = input("Введите слово, которое будем искать в названии вакансии\n")
            for item in db.get_vacancies_with_keyword(keyword):
                print(item)
        else:
            break

        print()
        print("Хотите сделать другой запрос?\n1 - Да\n2 - Нет")
        choice = input()
        if choice == '1':
            continue
        break


if __name__ == '__main__':
    main()
