import json

import requests

from classes import DBManager, HH
from config import config
from utils import read_json, get_employers

PATH_TO_EMPLOYERS = 'data/employers.json'
PATH_TO_DBiniFile = 'data/database.ini'


def main():
    params = config(PATH_TO_DBiniFile)
    db = DBManager('headhunter', params)
    # db.create_database()
    #
    # employers = get_employers(read_json(PATH_TO_EMPLOYERS))
    # db.insert('employers', employers)
    #
    # for i in range(len(employers)):
    #     hh = HH(employers[i][0]).get_vacancies()
    #     db.insert('vacancies', hh)

    fun1 = db.get_companies_and_vacancies_count()
    fun2 = db.get_all_vacancies()
    fun3 = db.get_avg_salary()
    fun4 = db.get_vacancies_with_higher_salary()
    fun5 = db.get_vacancies_with_keyword('инженер')
    for item in fun5:
        print(item)
    print(fun3)
    print(fun3[0][0])
    print(len(fun5))


if __name__ == '__main__':
    main()
