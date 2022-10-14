from statistics import mean

import requests
from environs import Env
from terminaltables import AsciiTable


def get_quantity_vacancies_for_superJob(language, secret_key):
    api_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': secret_key}
    moscow_id = 4
    params = {'srws': 1,
              'skwc': 'particular',
              'keys': f'{language}',
              'town': moscow_id}
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['total']


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
        for vacancy in response.json()['objects']:
            if vacancy['currency'] == 'rub' and (vacancy['payment_from'] or vacancy['payment_to']):
                if vacancy['payment_from'] and vacancy['payment_to']:
                    salaries.append((vacancy['payment_from'] + vacancy['payment_to']) // 2)
                elif not vacancy['payment_to']:
                    salaries.append(vacancy['payment_from'] * 1.2)
                elif not vacancy['payment_from']:
                    salaries.append(vacancy['payment_to'] * 0.8)
        pages_number = (response.json()['total'] - 1) / 100
        page += 1
    return salaries


def get_information_on_vacancies_superjob(languages, secret_key):
    information_on_vacancies = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']
    ]
    for language in languages:
        quantity_vacancies = get_quantity_vacancies_for_superJob(language, secret_key)
        salaries_from_superjob = predict_rub_salary_for_superJob(language, secret_key)
        average_salary = 0
        if salaries_from_superjob:
            average_salary = int(mean(salaries_from_superjob))
        information_on_vacancies.append([language, quantity_vacancies,
                                        len(salaries_from_superjob), average_salary])
    return information_on_vacancies


def get_table_vacancies_superjob(information_on_vacancies):
    title = '+SuperJob Moscow'
    table_instance = AsciiTable(information_on_vacancies, title)
    return table_instance.table


def get_quantity_vacancies(language):
    api_url = 'https://api.hh.ru/vacancies'
    moscow_id = 1
    params = {'text': f'программист {language}',
              'area': moscow_id,
              'period': 30}
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    return response.json()['found']


def predict_rub_salary_headhunter(vacancy):
    salaries = []
    api_url = 'https://api.hh.ru/vacancies'
    moscow_id = 1
    page = 0
    pages_number = 1
    while page < pages_number:
        params = {'text': f'программист {vacancy}',
                  'area': moscow_id,
                  'period': 30,
                  'only with salary': 'true',
                  'page': page
                  }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        for vacancy in response.json()['items']:
            if vacancy['salary'] is not None:
                if vacancy['salary']['currency'] == 'RUR':
                    if vacancy['salary']['from'] and vacancy['salary']['to']:
                        salaries.append((vacancy['salary']['from'] + vacancy['salary']['to']) // 2)
                    elif vacancy['salary']['from']:
                        salaries.append(vacancy['salary']['from'] * 1.2)
                    elif vacancy['salary']['to']:
                        salaries.append(vacancy['salary']['to'] * 0.8)
        pages_number = response.json()['pages']
        page += 1
    return salaries


def get_information_on_vacancies_headhunter(languages):
    information_on_vacancies = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        quantity_vacancies = get_quantity_vacancies(language)
        salaries_from_headhunter = predict_rub_salary_headhunter(language)
        average_salary = 0
        if salaries_from_headhunter:
            average_salary = int(mean(salaries_from_headhunter))
        information_on_vacancies.append([language, quantity_vacancies,
                                        len(salaries_from_headhunter),
                                         average_salary])
    return information_on_vacancies


def get_table_vacancies_headhunter(information_on_vacancies_headhunter):
    title = '+HeadHunter Moscow'
    table_instance = AsciiTable(information_on_vacancies_headhunter, title)
    return table_instance.table


def main():
    env = Env()
    env.read_env()
    secret_key = env.str("SECRET_KEY_SUPERJOB")
    languages = ['Java', 'Javascript', 'Python', 'C++', 'Swift', 'Go', 'Ruby', 'C#']
    information_on_vacancies_superjob = get_information_on_vacancies_superjob(languages, secret_key)
    information_on_vacancies_headhunter = get_information_on_vacancies_headhunter(languages)
    print(get_table_vacancies_superjob(information_on_vacancies_superjob))
    print()
    print(get_table_vacancies_headhunter(information_on_vacancies_headhunter))

if __name__ == '__main__':
    main()

    # print()
    # print(get_table_vacancies_headhunter(languages))
