from statistics import mean

import requests
from environs import Env
from terminaltables import AsciiTable


def calculate_expected_salary(salary_from, salary_to):
    salary = 0
    if salary_from and salary_to:
        salary = (salary_from + salary_to) // 2
    elif not salary_to:
        salary = salary_from * 1.2
    elif not salary_from:
        salary = salary_to * 0.8
    return salary



def predict_rub_salary_for_superJob(language, secret_key):
    api_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': secret_key}
    moscow_id = 4
    page = 0
    pages_number = 1
    salaries = []
    while page < pages_number:
        params = {'srws': 1,
                  'skwc': 'particular',
                  'keys': f'{language}',
                  'town': moscow_id,
                  'count': 100,
                  'page': page}

        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        vacancies = response.json()['objects']
        for vacancy in vacancies:
            salary_from = vacancy['payment_from']
            salary_to = vacancy['payment_to']
            if vacancy['currency'] == 'rub' and (salary_from or salary_to):
                salaries.append(calculate_expected_salary(salary_from, salary_to))
        pages_number = (response.json()['total'] - 1) / 100
        page += 1
    return salaries


def get_information_on_vacancies_superjob(languages, secret_key):
    vacancies = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']
    ]

    for language in languages:
        api_url = 'https://api.superjob.ru/2.0/vacancies/'
        headers = {'X-Api-App-Id': secret_key}
        moscow_id = 4
        params = {'srws': 1,
                  'skwc': 'particular',
                  'keys': f'{language}',
                  'town': moscow_id}
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        quantity_vacancies = response.json()['total']
        salaries_from_superjob = predict_rub_salary_for_superJob(language, secret_key)
        average_salary = 0
        if salaries_from_superjob:
            average_salary = int(mean(salaries_from_superjob))
        vacancies.append([language, quantity_vacancies,
                          len(salaries_from_superjob), average_salary])
    return vacancies


def get_table_vacancies_superjob(information_on_vacancies):
    title = '+SuperJob Moscow'
    table_instance = AsciiTable(information_on_vacancies, title)
    return table_instance.table



def predict_rub_salary_headhunter(vacancy):
    salaries = []
    api_url = 'https://api.hh.ru/vacancies'
    moscow_id = 1
    page = 0
    pages_number = 1
    while page < pages_number:
        params = {'text': f'программист {vacancy}',
                  'area': moscow_id,
                  'only with salary': 'true',
                  'page': page
                  }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        vacancies = response.json()['items']
        for vacancy in vacancies:
            if vacancy['salary'] is not None:
                salary_from = vacancy['salary']['from']
                salary_to = vacancy['salary']['to']
                if vacancy['salary']['currency'] == 'RUR':
                    salaries.append(calculate_expected_salary(salary_from, salary_to))
        pages_number = response.json()['pages']
        page += 1
    return salaries


def get_information_on_vacancies_headhunter(languages):
    vacancies = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        api_url = 'https://api.hh.ru/vacancies'
        moscow_id = 1
        params = {'text': f'программист {language}',
                  'area': moscow_id,
                  'period': 30}
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        quantity_vacancies = response.json()['found']
        salaries_from_headhunter = predict_rub_salary_headhunter(language)
        average_salary = 0
        if salaries_from_headhunter:
            average_salary = int(mean(salaries_from_headhunter))
        vacancies.append([language, quantity_vacancies,
                          len(salaries_from_headhunter),
                          average_salary])
    return vacancies


def get_table_vacancies_headhunter(information_on_vacancies_headhunter):
    title = '+HeadHunter Moscow'
    table_instance = AsciiTable(information_on_vacancies_headhunter, title)
    return table_instance.table


def main():
    env = Env()
    env.read_env()
    secret_key = env.str("SECRET_KEY_SUPERJOB")
    languages = ['Java', 'Javascript', 'Python', 'C++', 'Swift', 'Go', 'Ruby', 'C#']
    vacancies_superjob = get_information_on_vacancies_superjob(languages, secret_key)
    vacancies_headhunter = get_information_on_vacancies_headhunter(languages)
    print(get_table_vacancies_superjob(vacancies_superjob))
    print()
    print(get_table_vacancies_headhunter(vacancies_headhunter))


if __name__ == '__main__':
    main()
