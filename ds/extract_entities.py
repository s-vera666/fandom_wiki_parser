# Извлекаем из из data.csv уникальные сущности (PERSON, LOC) и связи "документ-сущность"
# В результате получаем entities.csv и doc_entities.csv

import pandas as pd
import spacy

# Загружаем русскую модель spaCy
nlp = spacy.load("ru_core_news_sm")
print("Модель spaCy загружена")

# 1. Читаем data.csv
df = pd.read_csv("../fandom_project/data/data.csv")
print(f"Загружено {len(df)} документов")

# 2. Словари для хранения
# entities_dict: ключ = имя сущности, значение = словарь с {'type', 'count', 'docs'}
entities_dict = {}
# связи: список кортежей (doc_id, entity_id)
doc_entity_pairs = []

# 3. Проходим по каждому документу
for idx, row in df.iterrows():
    doc_id = idx + 1        # номер строки = id документа???!!!
    content = row['content']
    print(f"Обрабатываем документ {doc_id}: {row['title']}")

    # Применяем spaCy
    doc = nlp(content)

    # Перебираем найденные сущности
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'LOC']:
            name = ent.text.strip()
            typ = ent.label_   # 'PERSON' или 'LOC'

            # Если сущность встретилась впервые, создаём запись
            if name not in entities_dict:
                entities_dict[name] = {'type': typ, 'count': 0, 'docs': set()}
            # Увеличиваем счётчик упоминаний
            entities_dict[name]['count'] += 1
            # Запоминаем id документа, где встретилась
            entities_dict[name]['docs'].add(doc_id)

# 4. Присваиваем каждой сущности уникальный id
# Создаём список для entities.csv
entities_rows = []
entity_id_counter = 0
# Таблица для быстрого поиска entity_id по имени
name_to_id = {}

for name, info in entities_dict.items():
    entity_id = entity_id_counter
    entity_id_counter += 1
    name_to_id[name] = entity_id
    entities_rows.append({
        'entity_id': entity_id,
        'entity_name': name,
        'type': info['type'],
        'count': info['count']
    })

# 5. Строим список связей doc_entities (doc_id, entity_id)
for name, info in entities_dict.items():
    eid = name_to_id[name]
    for doc_id in info['docs']:
        doc_entity_pairs.append({
            'doc_id': doc_id,
            'entity_id': eid
        })

# 6. Сохраняем в CSV
entities_df = pd.DataFrame(entities_rows)
entities_df.to_csv("../fandom_project/data/entities.csv", index=False, encoding="utf-8")
print(f"Сохранено {len(entities_df)} уникальных сущностей в entities.csv")

doc_entities_df = pd.DataFrame(doc_entity_pairs)
doc_entities_df.to_csv("../fandom_project/data/doc_entities.csv", index=False, encoding="utf-8")
print(f"Сохранено {len(doc_entities_df)} связей в doc_entities.csv")

print("Готово для импортирта CSV в PostgreSQL")
