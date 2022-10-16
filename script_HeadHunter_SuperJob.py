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


def get_job_stats_superJob(language, secret_key):
    api_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': secret_key}
    moscow_id = 4
    page = 0
    pages_number = 1
    keyword_job_search_option = 1
    salaries = []
    while page < pages_number:
        params = {'srws': keyword_job_search_option,
                  'skwc': 'particular',
                  'keys': f'{language}',
                  'town': moscow_id,
                  'count': 100,
                  'page': page}
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        vacancies = response.json()
        for vacancy in vacancies['objects']:
            salary_from = vacancy['payment_from']
            salary_to = vacancy['payment_to']
            if vacancy['currency'] == 'rub' and (salary_from or salary_to):
                salaries.append(calculate_expected_salary(salary_from, salary_to))
        pages_number = (vacancies['total'] - 1) / 100
        page += 1
    job_stats = [vacancies['total'], salaries]
    return job_stats


def get_vacancies_superjob(languages, secret_key):
    vacancies = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']
    ]
    for language in languages:
        job_stats = get_job_stats_superJob(language, secret_key)
        average_salary = 0
        if job_stats[1]:
            average_salary = int(mean(job_stats[1]))
        vacancies.append([language, job_stats[0],
                          len(job_stats[1]), average_salary])
    return vacancies


def get_table_vacancies_superjob(information_on_vacancies):
    title = '+SuperJob Moscow'
    table_instance = AsciiTable(information_on_vacancies, title)
    return table_instance.table


def get_job_stats_headhunter(language):
    salaries = []
    api_url = 'https://api.hh.ru/vacancies'
    moscow_id = 1
    page = 0
    pages_number = 1
    while page < pages_number:
        params = {'text': f'программист {language}',
                  'area': moscow_id,
                  'only with salary': 'true',
                  'page': page
                  }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        vacancies = response.json()
        for vacancy in vacancies['items']:
            if vacancy['salary'] is not None:
                salary_from = vacancy['salary']['from']
                salary_to = vacancy['salary']['to']
                if vacancy['salary']['currency'] == 'RUR':
                    salaries.append(calculate_expected_salary(salary_from, salary_to))
        pages_number = vacancies['pages']
        page += 1
    job_stats = [vacancies['found'], salaries]
    return job_stats


def get_vacancies_headhunter(languages):
    vacancies = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        job_stats = get_job_stats_headhunter(language)
        average_salary = 0
        if job_stats[1]:
            average_salary = int(mean(job_stats[1]))
        vacancies.append([language, job_stats[0],
                          len(job_stats[1]),
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
    vacancies_superjob = get_vacancies_superjob(languages, secret_key)
    vacancies_headhunter = get_vacancies_headhunter(languages)
    print(get_table_vacancies_superjob(vacancies_superjob))
    print()
    print(get_table_vacancies_headhunter(vacancies_headhunter))


if __name__ == '__main__':
    main()
