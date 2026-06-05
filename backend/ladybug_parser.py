# Парсер для вселенной «Леди Баг»

import requests
from bs4 import BeautifulSoup
from base_parser import BaseParser

class LadybugParser(BaseParser):
    # 1. Получаем список страниц для парсинга (ключ = название, значение = URL)
    def get_pages(self):
        return {
            # Персонажи
            "Леди Баг (Маринетт)": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9C%D0%B0%D1%80%D0%B8%D0%BD%D0%B5%D1%82%D1%82_%D0%94%D1%8E%D0%BF%D1%8D%D0%BD-%D0%A7%D1%8D%D0%BD",
            "Супер-Кот (Адриан)": "https://miraculousladybug.fandom.com/ru/wiki/%D0%90%D0%B4%D1%80%D0%B8%D0%B0%D0%BD_%D0%90%D0%B3%D1%80%D0%B5%D1%81%D1%82",
            "Бражник (Габриэль)": "https://miraculousladybug.fandom.com/ru/wiki/%D0%93%D0%B0%D0%B1%D1%80%D0%B8%D1%8D%D0%BB%D1%8C_%D0%90%D0%B3%D1%80%D0%B5%D1%81%D1%82",
            "Майюра (Натали)": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9D%D0%B0%D1%82%D0%B0%D0%BB%D0%B8_%D0%A1%D0%B0%D0%BD%D0%BA%D1%91%D1%80",
            "Рена Руж (Алья)": "https://miraculousladybug.fandom.com/ru/wiki/%D0%90%D0%BB%D1%8C%D1%8F_%D0%A1%D0%B5%D0%B7%D0%B5%D1%80",
            "Карапакс (Нино)": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9D%D0%B8%D0%BD%D0%BE_%D0%9B%D0%B5%D0%B9%D1%84",
            "Королева Пчела (Хлоя)": "https://miraculousladybug.fandom.com/ru/wiki/%D0%A5%D0%BB%D0%BE%D1%8F_%D0%91%D1%83%D1%80%D0%B6%D1%83%D0%B0",
            "Тикки": "https://miraculousladybug.fandom.com/ru/wiki/%D0%A2%D0%B8%D0%BA%D0%BA%D0%B8",
            "Плагг": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9F%D0%BB%D0%B0%D0%B3%D0%B3",
            "Мастер Фу": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9C%D0%B0%D1%81%D1%82%D0%B5%D1%80_%D0%A4%D1%83",
            # Локации
            "Париж": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9F%D0%B0%D1%80%D0%B8%D0%B6",
            "Коллеж Франсуа Дюпон": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9A%D0%BE%D0%BB%D0%BB%D0%B5%D0%B6_%22%D0%A4%D1%80%D0%B0%D0%BD%D1%81%D1%83%D0%B0_%D0%94%D1%8E%D0%BF%D0%BE%D0%BD%22",
            "Особняк Агрестов": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9E%D1%81%D0%BE%D0%B1%D0%BD%D1%8F%D0%BA_%D0%90%D0%B3%D1%80%D0%B5%D1%81%D1%82%D0%BE%D0%B2",
            "Булочная Тома и Сабин": "https://miraculousladybug.fandom.com/ru/wiki/%D0%91%D1%83%D0%BB%D0%BE%D1%87%D0%BD%D0%B0%D1%8F-%D0%BA%D0%BE%D0%BD%D0%B4%D0%B8%D1%82%D0%B5%D1%80%D1%81%D0%BA%D0%B0%D1%8F",
            "Отель Гранд Париж": "https://miraculousladybug.fandom.com/ru/wiki/%D0%9E%D1%82%D0%B5%D0%BB%D1%8C_%22%D0%93%D1%80%D0%B0%D0%BD%D0%B4_%D0%9F%D0%B0%D1%80%D0%B8%D0%B6%22"
        }

    # 2. Скачиваем HTML
    def fetch_html(self, url):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")
            return ""

    # 3. Извлекаем текст из HTML
    def extract_text(self, html):
        soup = BeautifulSoup(html, "html.parser")
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            return ""
        paragraphs = content_div.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs)
        return text