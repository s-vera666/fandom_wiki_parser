# Запускаем парсинг

# from lotr_parser import LotrParser
from ladybug_parser import LadybugParser

if __name__ == "__main__":
    
    # Создаём объект парсера
    # parser = LotrParser()
    parser = LadybugParser()

    # Запускаем парсинг, сохраняем в папку data/ (как CSV)
    parser.parse_to_csv("../fandom_wiki_parser/data/raw/data.csv")
    print("Парсинг закончен. Файл data.csv создан.")
