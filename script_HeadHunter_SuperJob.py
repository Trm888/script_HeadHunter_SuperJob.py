from statistics import mean

import requests
from environs import Env
from terminaltables import AsciiTable


def get_quantity_vacancies_for_superJob(language):
    env = Env()
    env.read_env()
    secret_key = env.str("SECRET_KEY")
    api_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': secret_key}
    params = {'srws': 1,
              'skwc': 'particular',
              'keys': f'{language}',
              'town': 4,
              'count': 100,
              'page': 0}
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['total']


def predict_rub_salary_for_superJob(language):
    env = Env()
    env.read_env()
    secret_key = env.str("SECRET_KEY")
    api_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': secret_key}
    params = {'srws': 1,
              'skwc': 'particular',
              'keys': f'{language}',
              'town': 4,
              'count': 100,
              'page': 0}
    salaries = []
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    for i in response.json()['objects']:
        if i['currency'] == 'rub' and (i['payment_from'] != 0 or i['payment_to'] != 0):
            if i['payment_from'] != 0 and i['payment_to'] != 0:
                salaries.append((i['payment_from'] + i['payment_to']) // 2)
            elif i['payment_to'] == 0:
                salaries.append(i['payment_from'] * 1.2)
            elif i['payment_from'] == 0:
                salaries.append(i['payment_to'] * 0.8)
    return salaries


def get_table_vacancies_superjob(languages):
    information_on_vacancies_table = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']
    ]
    for language in languages:
        if predict_rub_salary_for_superJob(language):
            information_on_vacancies_table.append([language, get_quantity_vacancies_for_superJob(language),
                                                   len(predict_rub_salary_for_superJob(language)),
                                                   int(mean(predict_rub_salary_for_superJob(language)))])
        else:
            information_on_vacancies_table.append([language, get_quantity_vacancies_for_superJob(language),
                                                   len(predict_rub_salary_for_superJob(language)),
                                                   0])
    title = '+SuperJob Moscow'
    table_instance = AsciiTable(information_on_vacancies_table, title)
    return table_instance.table


def get_quantity_vacancies(language):
    api_url = 'https://api.hh.ru/vacancies'
    params = {'text': f'программист {language}',
              'area': 1,
              'period': 30}
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    return response.json()['found']


def predict_rub_salary_headhunter(vacancy):
    salaries = []
    api_url = 'https://api.hh.ru/vacancies'
    page = 0
    pages_number = 1
    while page < pages_number:
        params = {'text': f'программист {vacancy}',
                  'area': 1,
                  'period': 30,
                  'only with salary': 'true',
                  'page': page
                  }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        for i in response.json()['items']:
            if i['salary'] is not None:
                if i['salary']['currency'] == 'RUR':
                    if i['salary']['from'] and i['salary']['to']:
                        salaries.append((i['salary']['from'] + i['salary']['to']) // 2)
                    elif i['salary']['from']:
                        salaries.append(i['salary']['from'] * 1.2)
                    elif i['salary']['to']:
                        salaries.append(i['salary']['to'] * 0.8)
        pages_number = response.json()['pages']
        page += 1
    return salaries


def get_table_vacancies_headhunter(languages):
    information_on_vacancies_table = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        if predict_rub_salary_headhunter(language):
            information_on_vacancies_table.append([language, get_quantity_vacancies(language),
                                                   len(predict_rub_salary_headhunter(language)),
                                                   int(mean(predict_rub_salary_headhunter(language)))])
        else:
            information_on_vacancies_table.append([language, get_quantity_vacancies(language),
                                                   len(predict_rub_salary_headhunter(language)),
                                                   0])
    title = '+HeadHunter Moscow'
    table_instance = AsciiTable(information_on_vacancies_table, title)
    return table_instance.table


if __name__ == '__main__':
    languages = ['Java', 'Javascript', 'Python', 'C++', 'Swift', 'Go', 'Ruby', 'C#']
    print(get_table_vacancies_superjob(languages))
    print()
    print(get_table_vacancies_headhunter(languages))
