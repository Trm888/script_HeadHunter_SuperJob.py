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


def get_language_stats_superJob(language, secret_key):
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
    language_stats = [vacancies['total'], salaries]
    return language_stats


def collect_statistics_by_languages_superjob(languages, secret_key):
    stats = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']
    ]
    for language in languages:
        number_of_vacancies, salaries = get_language_stats_superJob(language, secret_key)
        average_salary = 0
        if salaries:
            average_salary = int(mean(salaries))
        stats.append([language, number_of_vacancies,
                      len(salaries), average_salary])
    return stats


def get_language_stats_headhunter(language):
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
    language_stats = [vacancies['found'], salaries]
    return language_stats


def collect_statistics_by_languages_headhunter(languages):
    stats = [
        ['Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        number_of_vacancies, salaries = get_language_stats_headhunter(language)
        average_salary = 0
        if salaries:
            average_salary = int(mean(salaries))
        stats.append([language, number_of_vacancies,
                      len(salaries), average_salary])
    return stats


def get_table_vacancies(information_on_vacancies_headhunter, title):
    table_instance = AsciiTable(information_on_vacancies_headhunter, title)
    return table_instance.table


def main():
    env = Env()
    env.read_env()
    secret_key = env.str("SECRET_KEY_SUPERJOB")
    languages = ['Java', 'Javascript', 'Python', 'C++', 'Swift', 'Go', 'Ruby', 'C#']
    job_statistics_superjob = collect_statistics_by_languages_superjob(languages, secret_key)
    job_statistics_headhunter = collect_statistics_by_languages_headhunter(languages)
    print(get_table_vacancies(job_statistics_superjob, title='+SuperJob Moscow'))
    print()
    print(get_table_vacancies(job_statistics_headhunter, title='+HeadHunter Moscow'))


if __name__ == '__main__':
    main()
