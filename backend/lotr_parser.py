# Парсер для конкретного фандома - Властелина колец.

import requests
from bs4 import BeautifulSoup
from base_parser import BaseParser # импортируем родительский класс

class LotrParser(BaseParser):
    # 1. Получаем список страниц для парсинга
    def get_pages(self):
        return {
            "Фродо Бэггинс": "https://lotr.fandom.com/ru/wiki/%D0%A4%D1%80%D0%BE%D0%B4%D0%BE_%D0%91%D1%8D%D0%B3%D0%B3%D0%B8%D0%BD%D1%81",
            "Гэндальф": "https://lotr.fandom.com/ru/wiki/%D0%93%D1%8D%D0%BD%D0%B4%D0%B0%D0%BB%D1%8C%D1%84",
            "Мордор": "https://lotr.fandom.com/ru/wiki/%D0%9C%D0%BE%D1%80%D0%B4%D0%BE%D1%80",
            "Ривенделл": "https://lotr.fandom.com/ru/wiki/%D0%A0%D0%B8%D0%B2%D0%B5%D0%BD%D0%B4%D0%B5%D0%BB%D0%BB",
            "Шир": "https://lotr.fandom.com/ru/wiki/%D0%A8%D0%B8%D1%80"
        }

    # 2. Скачиваем HTML
    def fetch_html(self, url):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # если статус не 200, вызовет исключение
            return response.text
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")
            return "" # вернём пустую строку, чтобы не ломать программу

    # 3. Извлекаем текст из HTML
    def extract_text(self, html):
        soup = BeautifulSoup(html, "html.parser")
        # На вики Фэндома основной текст лежит внутри div с классом "mw-parser-output"
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            return ""
        # Находим все абзацы <p> внутри этого div
        paragraphs = content_div.find_all("p")
        # Берём текст каждого абзаца, убираем лишние пробелы и соединяем через \n
        text = "\n".join(p.get_text(strip=True) for p in paragraphs)
        return text

