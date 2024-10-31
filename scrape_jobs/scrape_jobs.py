import requests
from bs4 import BeautifulSoup
import json
import re
import time

# URL для поиска вакансий
url = "https://hh.ru/search/vacancy?text=Python&area=1&area=2"

# Заголовки для запроса, чтобы сайт не заблокировал
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

# Функция для парсинга страницы с вакансиями
def parse_jobs(url):
    jobs = []  # Список для хранения вакансий

    # Запрос на страницу
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Проверка успешности запроса

    # Парсинг страницы
    soup = BeautifulSoup(response.text, "html.parser")

    # Поиск всех блоков с вакансиями
    vacancy_items = soup.find_all("div", {"class": "vacancy-serp-item"})

    for item in vacancy_items:
        # Название вакансии и ссылка
        title_tag = item.find("a", {"class": "serp-item__title"})
        title = title_tag.text
        link = title_tag["href"]

        # Описание вакансии
        description = item.find("div", {"class": "g-user-content"}).text.lower()

        # Проверка ключевых слов
        if "django" in description and "flask" in description:
            # Название компании
            company = item.find("a", {"data-qa": "vacancy-serp__vacancy-employer"}).text.strip()

            # Город
            city = item.find("div", {"data-qa": "vacancy-serp__vacancy-address"}).text

            # Вилка зарплаты
            salary_tag = item.find("span", {"data-qa": "vacancy-serp__vacancy-compensation"})
            salary = salary_tag.text if salary_tag else "не указана"

            # Создаем словарь для вакансии
            job_info = {
                "title": title,
                "link": link,
                "company": company,
                "city": city,
                "salary": salary
            }

            jobs.append(job_info)

    return jobs

# Сбор вакансий и сохранение в JSON
def save_jobs_to_json(jobs, filename="jobs.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=4)

# Выполнение скрипта
if __name__ == "__main__":
    all_jobs = []
    page = 0

    while True:
        # URL с параметром страницы
        paginated_url = f"{url}&page={page}"
        
        # Парсим вакансии на странице
        jobs_on_page = parse_jobs(paginated_url)
        
        if not jobs_on_page:
            break  # Останавливаемся, если вакансий на странице больше нет

        all_jobs.extend(jobs_on_page)
        print(f"Страница {page + 1} обработана")
        
        # Переход к следующей странице
        page += 1
        time.sleep(1)  # Добавляем задержку, чтобы избежать блокировки

    # Сохранение данных в JSON
    save_jobs_to_json(all_jobs)
    print(f"Найдено {len(all_jobs)} вакансий и сохранено в jobs.json")


