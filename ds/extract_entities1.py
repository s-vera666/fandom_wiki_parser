# Извлекаем из data.csv уникальные сущности (PER, LOC) и связи "документ-сущность"
# В результате получаем entities.csv и doc_entities.csv

import pandas as pd
from natasha import Segmenter, NewsEmbedding, NewsNERTagger, Doc

# 1. Инициализация Natasha
segmenter = Segmenter() # разбивает текст на слова и предложения
emb = NewsEmbedding() # встраивания слов (нужны для NER)
ner_tagger = NewsNERTagger(emb) # модель для поиска имён и мест

print("Модель Natasha загружена")

# 2. Читаем data.csv
df = pd.read_csv("../fandom_project/data/data.csv")
print(f"Загружено {len(df)} документов")

# 3. Словари для хранения
entities_dict = {} # имя сущности -> {'type': 'PER'/'LOC', 'count': ..., 'docs': set()}
doc_entity_pairs = [] # список связей (doc_id, entity_id)

# 4. Проходим по каждому документу
for idx, row in df.iterrows():
    doc_id = idx + 1 # номер строки как id документа (начинается с 1)
    content = row['content']
    print(f"Обрабатываем документ {doc_id}: {row['title']}")

    # Обработка текста Natasha
    doc = Doc(content) # обёртка над текстом
    doc.segment(segmenter) # разбиваем на предложения/токены
    doc.tag_ner(ner_tagger) # ищем именованные сущности

    # Результаты – в doc.spans
    for span in doc.spans:
        if span.type in ('PER', 'LOC'):
            name = span.text.strip()
            typ = span.type

            # Если сущность встретилась впервые – создаём запись
            if name not in entities_dict:
                entities_dict[name] = {'type': typ, 'count': 0, 'docs': set()}
            entities_dict[name]['count'] += 1
            entities_dict[name]['docs'].add(doc_id)

# 5. Присваиваем каждой сущности уникальный id
entities_rows = []
entity_id_counter = 0
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

# 6. Строим список связей doc_entities
for name, info in entities_dict.items():
    eid = name_to_id[name]
    for doc_id in info['docs']:
        doc_entity_pairs.append({
            'doc_id': doc_id,
            'entity_id': eid
        })

# 7. Сохраняем в CSV
entities_df = pd.DataFrame(entities_rows)
entities_df.to_csv("../fandom_wiki_parser/data/processed/entities.csv", index=False, encoding="utf-8")
print(f"Сохранено {len(entities_df)} уникальных сущностей в entities.csv")

doc_entities_df = pd.DataFrame(doc_entity_pairs)
doc_entities_df.to_csv("../fandom_wiki_parser/data/processed/doc_entities.csv", index=False, encoding="utf-8")
print(f"Сохранено {len(doc_entities_df)} связей в doc_entities.csv")

print("Готово для импортирта CSV в PostgreSQL")