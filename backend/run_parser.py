# Запускаем парсинг

from lotr_parser import LotrParser

if __name__ == "__main__":
    # Создаём объект парсера
    parser = LotrParser()
    # Запускаем парсинг, сохраняем в папку data (как CSV)
    parser.parse_to_csv("C:\\progectsss\\uch.pr\\fandom_project\\data\\data.csv")
    print("Парсинг закончен. Файл data.csv создан.")
