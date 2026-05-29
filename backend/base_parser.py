# Общий шаблон для парсера любого фандома.

from abc import ABC, abstractmethod
import pandas as pd
import time

class BaseParser(ABC):
    # Возвращает словарь { 'Название страницы': 'URL' } для парсинга.
    @abstractmethod
    def get_pages(self):
        pass

    # Загружает HTML страницы по URL. Возвращает текст HTML.
    @abstractmethod
    def fetch_html(self, url):
        pass

    # Из HTML-кода достаёт только читаемый текст. Возвращает строку текста.
    @abstractmethod
    def extract_text(self, html):
        pass

    # Общий метод для всех парсеров
    def parse_to_csv(self, output_file="data.csv"):
        pages = self.get_pages() # получаем список страниц
        all_data = [] # здесь будут словари

        for title, url in pages.items():
            print(f"Парсим: {title}")
            html = self.fetch_html(url) # скачиваем HTML
            if html:
                text = self.extract_text(html)  # чистим текст
                if text:
                    all_data.append({
                        "title": title,
                        "url": url,
                        "content": text
                    })
                    print(f"    Сохранили, длина текста: {len(text)} символов")
            time.sleep(5)

        # Сохраняем в CSV с помощью pandas
        df = pd.DataFrame(all_data)
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"\nСохранено {len(df)} страниц в {output_file}")
        return df
        
