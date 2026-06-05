# Парсер для конкретного фандома - Властелина колец.

import requests
from bs4 import BeautifulSoup
from base_parser import BaseParser # импортируем родительский класс

class LotrParser(BaseParser):
    # 1. Получаем список страниц для парсинга
    def get_pages(self):
        return {
            # Персонажи
            "Бильбо Бэггинс": "https://lotr.fandom.com/ru/wiki/%D0%91%D0%B8%D0%BB%D1%8C%D0%B1%D0%BE_%D0%91%D1%8D%D0%B3%D0%B3%D0%B8%D0%BD%D1%81",
            "Фродо Бэггинс": "https://lotr.fandom.com/ru/wiki/%D0%A4%D1%80%D0%BE%D0%B4%D0%BE_%D0%91%D1%8D%D0%B3%D0%B3%D0%B8%D0%BD%D1%81",
            "Сэмуайз Гэмджи": "https://lotr.fandom.com/ru/wiki/%D0%A1%D1%8D%D0%BC%D1%83%D0%B0%D0%B9%D0%B7_%D0%93%D1%8D%D0%BC%D0%B4%D0%B6%D0%B8",
            "Гэндальф": "https://lotr.fandom.com/ru/wiki/%D0%93%D1%8D%D0%BD%D0%B4%D0%B0%D0%BB%D1%8C%D1%84",
            "Арагорн": "https://lotr.fandom.com/ru/wiki/%D0%90%D1%80%D0%B0%D0%B3%D0%BE%D1%80%D0%BD",
            "Леголас": "https://lotr.fandom.com/ru/wiki/%D0%9B%D0%B5%D0%B3%D0%BE%D0%BB%D0%B0%D1%81",
            "Гимли": "https://lotr.fandom.com/ru/wiki/%D0%93%D0%B8%D0%BC%D0%BB%D0%B8",
            "Боромир": "https://lotr.fandom.com/ru/wiki/%D0%91%D0%BE%D1%80%D0%BE%D0%BC%D0%B8%D1%80",
            "Саурон": "https://lotr.fandom.com/ru/wiki/%D0%A1%D0%B0%D1%83%D1%80%D0%BE%D0%BD",
            "Арвен": "https://lotr.fandom.com/ru/wiki/%D0%90%D1%80%D0%B2%D0%B5%D0%BD",
            # Локации
            "Шир": "https://lotr.fandom.com/ru/wiki/%D0%A8%D0%B8%D1%80",
            "Ривенделл": "https://lotr.fandom.com/ru/wiki/%D0%A0%D0%B8%D0%B2%D0%B5%D0%BD%D0%B4%D0%B5%D0%BB%D0%BB",
            "Мордор": "https://lotr.fandom.com/ru/wiki/%D0%9C%D0%BE%D1%80%D0%B4%D0%BE%D1%80",
            "Гондор": "https://lotr.fandom.com/ru/wiki/%D0%93%D0%BE%D0%BD%D0%B4%D0%BE%D1%80",
            "Рохан": "https://lotr.fandom.com/ru/wiki/%D0%A0%D0%BE%D1%85%D0%B0%D0%BD",
            "Лотлориэн": "https://lotr.fandom.com/ru/wiki/%D0%9B%D0%BE%D1%82%D0%BB%D0%BE%D1%80%D0%B8%D1%8D%D0%BD",
            "Изенгард": "https://lotr.fandom.com/ru/wiki/%D0%98%D0%B7%D0%B5%D0%BD%D0%B3%D0%B0%D1%80%D0%B4",
            "Мория": "https://lotr.fandom.com/ru/wiki/%D0%9C%D0%BE%D1%80%D0%B8%D1%8F",
            "Одинокая Гора": "https://lotr.fandom.com/ru/wiki/%D0%9E%D0%B4%D0%B8%D0%BD%D0%BE%D0%BA%D0%B0%D1%8F_%D0%93%D0%BE%D1%80%D0%B0",
            "Осгилиат": "https://lotr.fandom.com/ru/wiki/%D0%9E%D1%81%D0%B3%D0%B8%D0%BB%D0%B8%D0%B0%D1%82"
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
