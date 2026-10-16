# NER: spaCy. Лемматизация: pymorphy3. Слияния: merge_similar + merge_substrings + ALIASES.


import os
import pandas as pd
import spacy
import pymorphy3
from collections import Counter

# Пути к файлам
DATA_RAW        = "../fandom_wiki_parser/data/raw/data.csv"
ALIASES_FILE    = "../fandom_wiki_parser/data/aliases.csv"
ENTITIES_OUT    = "../fandom_wiki_parser/data/processed/entities_spacy_new.csv"
DOC_ENTITIES_OUT = "../fandom_wiki_parser/data/processed/doc_entities_spacy_new.csv"

# Модели
nlp = spacy.load("ru_core_news_sm")
morph = pymorphy3.MorphAnalyzer()
print("Модели spaCy и pymorphy3 загружены")

# НАСТРОЙКИ

# Падежные окончания для merge_similar (порядок важен: длинные окончания проверяются первыми)
CASE_ENDINGS = (
    "ами", "ями", "ах", "ях", "ом", "ем", "ой", "ей", "ам", "ям",
    "а", "я", "у", "ю", "е", "ы", "и", "о",
)

# Союзы и предлоги (если в длинной сущности есть такое слово — значит spaCy склеил две сущности, и сливать нельзя)
CONJUNCTIONS = {"и", "или", "с", "в", "на", "из", "от", "до", "для"}

# Стоп-слова (короткий служебный мусор, который spaCy иногда захватывает вместе с именем)
STOPWORDS = {
    "и", "или", "с", "в", "на", "из", "от", "до", "для", "по", "к", "у",
    "был", "была", "было", "были", "есть", "это", "как", "что", "который",
    "свой", "свою", "своего", "всегда", "вместо", "когда", "она", "он",
    "его", "её", "ее", "их", "же", "ли", "бы", "не", "ни",
} 

# Приоритет тегов (частей речи) pymorphy3 (меньше число - более приоритетно)
TAG_PRIORITY = {
    'Name': 0, 'Surn': 1, 'Patr': 2, 'Geox': 3, 'Orgn': 4, 'Trad': 5,
    'NOUN': 10, 'ADJF': 20, 'ADJS': 21,
    'VERB': 90, 'INFN': 91, 'GRND': 92, 'PRTF': 93, 'PRTS': 94,
}

# ЗАГРУЗКА АЛИАСОВ ИЗ CSV
def load_aliases(path):
    """
    Читает CSV-файл с колонками "from" и "to".
    Возвращает словарь: {форма_в_тексте: каноническая_форма}.
    Если файла нет — возвращает пустой словарь, программа работает без алиасов.
    """
    if not os.path.exists(path):
        print(f"Файл алиасов не найден: {path}. Работаем без них.")
        return {}

    df = pd.read_csv(path)
    aliases = {}
    for i in range(len(df)):
        key = str(df.iloc[i]["from"]).strip()
        value = str(df.iloc[i]["to"]).strip()
        if key and value:
            aliases[key] = value

    print(f"Загружено алиасов: {len(aliases)}")
    return aliases

# ОЧИСТКА СПАНОВ

def split_glued_words(text):
    """
    Вставляет пробел на границе строчная-заглавная.
    'Леди Багдоверила' -> 'Леди Баг доверила'
    """
    result = ""
    for i in range(len(text)):
        result += text[i]
        if i + 1 < len(text) and text[i].islower() and text[i + 1].isupper():
            result += " "
    return result

def clean_entity_text(text):
    # Шаг 1. Убираем скобки
    while "(" in text and ")" in text:
        start = text.find("(")
        end = text.find(")")
        if start < end:
            text = text[:start] + " " + text[end + 1:]
        else:
            break

    # Шаг 2. Режем по разделителям на несколько частей
    parts = [text]
    for sep in ["•", "·", ",", ";"]:
        new_parts = []
        for p in parts:
            new_parts.extend(p.split(sep))
        parts = new_parts

    # Шаг 3. Каждую часть обрабатываем отдельно
    result = []
    for p in parts:
        # Разрезаем приклейки
        fixed = ""
        for i in range(len(p)):
            fixed += p[i]
            if i + 1 < len(p) and p[i].islower() and p[i + 1].isupper():
                fixed += " "

        # Убираем стоп-слова
        words = fixed.split()
        clean_words = []
        for w in words:
            if w.lower() not in STOPWORDS:
                clean_words.append(w)

        # Проверяем длину и добавляем
        if 1 <= len(clean_words) <= 4:
            result.append(" ".join(clean_words))

    return result

# ЛЕММАТИЗАЦИЯ

def lemmatize_word(w):
    """
    Лемматизация одного слова через pymorphy3.
    Из всех разборов выбирает тот, у которого приоритетнее часть речи.
    """
    cleaned = w.strip('.,!?;:()[]{}«»"\'')
    if not cleaned:
        return ""
    
    parsed = morph.parse(cleaned)
    if not parsed:
        return cleaned.lower()
    
    parsed = sorted(parsed, key=lambda p: TAG_PRIORITY.get(p.tag.POS, 50))
    return parsed[0].normal_form


def lemmatize_entity(text):
    """Лемматизация каждого слова сущности."""
    lemmas = []
    for w in text.split():
        lemma = lemmatize_word(w)
        if lemma:
            lemmas.append(lemma)
    return " ".join(lemmas)


# СЛИЯНИЯ

def _apply_remap(entities_dict, remap):
    """
    Вспомогательная: строит новый словарь сущностей с учётом правил замены.
    remap = {(старая_лемма, тип): (новая_лемма, тип)}
    """
    merged = {}
    for (lemma, typ), info in entities_dict.items():
        canon = remap.get((lemma, typ), (lemma, typ))
        if canon not in merged:
            merged[canon] = {"count": 0, "docs": set(), "forms": Counter()}
        merged[canon]["count"] += info["count"]
        merged[canon]["docs"] |= info["docs"]
        merged[canon]["forms"] += info["forms"]
    return merged


def merge_similar(entities_dict):
    """
    Нормализует падежные окончания в конце сущности.
    Если короткий вариант есть в словаре — сливаем.
    """
    existing = set(entities_dict.keys())
    remap = {}

    for (lemma, typ) in existing:
        # Нормализуем каждое слово: отрезаем падежное окончание
        normalized_words = []
        for w in lemma.split():
            for ending in CASE_ENDINGS:
                if w.endswith(ending) and len(w) - len(ending) >= 3:
                    w = w[: -len(ending)]
                    break
            normalized_words.append(w)
        normalized = " ".join(normalized_words)

        # Если нормализованная форма отличается и есть в словаре — сливаем
        if normalized != lemma and (normalized, typ) in existing:
            remap[(lemma, typ)] = (normalized, typ)

    return _apply_remap(entities_dict, remap)


def merge_substrings(entities_dict, max_extra_words=1):
    """
    Сливает короткую сущность в длинную, если короткая целиком в неё входит
    и встречается только там же.

    Не сливает, если в длинной есть союзы/предлоги (это склейка spaCy)
    или если длинная длиннее короткой больше чем на max_extra_words слов.
    """
    keys = list(entities_dict.keys())
    remap = {}

    for (short, styp) in keys:
        short_words = short.split()
        short_docs = entities_dict[(short, styp)]["docs"]
        best = None

        for (long, ltyp) in keys:
            if (long, ltyp) == (short, styp) or ltyp != styp:
                continue

            long_words = long.split()
            if not (len(short_words) < len(long_words) <= len(short_words) + max_extra_words):
                continue
            if not all(w in long_words for w in short_words):
                continue
            if any(w in CONJUNCTIONS for w in long_words):
                continue
            if not short_docs.issubset(entities_dict[(long, ltyp)]["docs"]):
                continue

            if best is None or len(long_words) > len(best[0].split()):
                best = (long, ltyp)

        if best is not None:
            remap[(short, styp)] = best
    return _apply_remap(entities_dict, remap)


def apply_aliases(entities_dict, aliases):
    """Приводит леммы к каноническим именам из словаря алиасов"""

    if not aliases:
        return entities_dict
    
    merged = {}
    for (lemma, typ), info in entities_dict.items():
        canon = aliases.get(lemma, lemma)
        key = (canon, typ)
        if key not in merged:
            merged[key] = {"count": 0, "docs": set(), "forms": Counter()}
        merged[key]["count"] += info["count"]
        merged[key]["docs"] |= info["docs"]
        merged[key]["forms"] += info["forms"]
    return merged

def merge_across_types(entities_dict):
    """
    Сливает сущности с одинаковой леммой, но разными типами (PER/LOC).
    Тип выбирается тот, где больше упоминаний.
    """
    by_lemma = {}
    for (lemma, typ), info in entities_dict.items():
        if lemma not in by_lemma:
            by_lemma[lemma] = []
        by_lemma[lemma].append((typ, info))

    merged = {}
    for lemma, items in by_lemma.items():
        # Считаем, сколько упоминаний у каждого типа
        count_by_type = {}
        for typ, info in items:
            count_by_type[typ] = count_by_type.get(typ, 0) + info["count"]

        # Берём тип с максимальным count
        best_type = None
        best_count = -1
        for typ in count_by_type:
            if count_by_type[typ] > best_count:
                best_count = count_by_type[typ]
                best_type = typ

        # Складываем все записи в одну
        merged_info = {"count": 0, "docs": set(), "forms": Counter()}
        for typ, info in items:
            merged_info["count"] += info["count"]
            merged_info["docs"] |= info["docs"]
            merged_info["forms"] += info["forms"]

        merged[(lemma, best_type)] = merged_info

    return merged

# ОСНОВНОЙ ЦИКЛ

df = pd.read_csv(DATA_RAW)
print(f"Загружено {len(df)} документов")

aliases = load_aliases(ALIASES_FILE)

# entities_dict: ключ = (лемма, тип), значение = {count, docs, forms}
entities_dict = {}
# Список связей (doc_id, entity_id) для второго CSV
doc_entity_pairs = []

for idx, row in df.iterrows():
    doc_id = idx + 1
    content = row["content"]
    print(f"Обрабатываем документ {doc_id}: {row['title']}")

    doc = nlp(content)
    for ent in doc.ents:
        if ent.label_ not in ("PER", "LOC"):
            continue

        typ = ent.label_
        for clean in clean_entity_text(ent.text):
            lemma = lemmatize_entity(clean)
            if not lemma:
                continue

            key = (lemma, typ)
            if key not in entities_dict:
                entities_dict[key] = {"count": 0, "docs": set(), "forms": Counter()}
            entities_dict[key]["count"] += 1
            entities_dict[key]["docs"].add(doc_id)
            entities_dict[key]["forms"][clean] += 1

# СЛИЯНИЯ
# Порядок важен: сначала падежи, потом короткие в длинные, потом алиасы, потом слияние разных типов
b = len(entities_dict); entities_dict = merge_similar(entities_dict)
print(f"merge_similar:    {b} → {len(entities_dict)}")

b = len(entities_dict); entities_dict = merge_substrings(entities_dict)
print(f"merge_substrings: {b} → {len(entities_dict)}")

b = len(entities_dict); entities_dict = apply_aliases(entities_dict)
print(f"apply_aliases:    {b} → {len(entities_dict)}")

b = len(entities_dict); entities_dict = merge_across_types(entities_dict)
print(f"merge_across_types: {b} → {len(entities_dict)}")

# СОХРАНЕНИЕ
entities_rows = []
name_to_id = {}

for entity_id, ((lemma, typ), info) in enumerate(entities_dict.items()):
    name_to_id[(lemma, typ)] = entity_id

    # Отображаемое имя - cамая частая исходная форма
    most_common = info["forms"].most_common(1)[0][0]

    # Последнее слово леммы и последнее слово самой частой формы
    last_lemma = lemma.split()[-1]
    last_common = most_common.split()[-1].lower()

    # Если pymorphy3 добавил "-а"/"-я" в конце, а в текстах этого нет - значит это вымышленное имя (Маринетта), берём форму из текста.
    if last_lemma.endswith(("а", "я")) and not last_common.endswith(("а", "я")):
        display = most_common
    else:
        # Иначе — красивая лемма: "кот нуар" -> "Кот Нуар"
        display = " ".join(w.capitalize() for w in lemma.split())

    entities_rows.append({
        "entity_id": entity_id,
        "entity_name": display,
        "type": typ,
        "count": info["count"],
        "forms": ", ".join(f"{f}×{c}" for f, c in info["forms"].most_common()),
    })

for (lemma, typ), info in entities_dict.items():
    eid = name_to_id[(lemma, typ)]
    for doc_id in info["docs"]:
        doc_entity_pairs.append({"doc_id": doc_id, "entity_id": eid})

pd.DataFrame(entities_rows).to_csv(ENTITIES_OUT, index=False, encoding="utf-8")
pd.DataFrame(doc_entity_pairs).to_csv(DOC_ENTITIES_OUT, index=False, encoding="utf-8")
print(f"Сохранено {len(entities_rows)} сущностей, {len(doc_entity_pairs)} связей")
