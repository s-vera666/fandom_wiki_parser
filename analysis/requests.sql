CREATE SCHEMA IF NOT EXISTS parser_wiki;
SET search_path TO parser_wiki;

-- DROP SCHEMA parser_wiki;

-- DROP TABLE IF EXISTS doc_entities;
-- DROP TABLE IF EXISTS entities;
-- DROP TABLE IF EXISTS documents;

-- DROP TABLE doc_entities CASCADE;
-- DROP TABLE entities CASCADE;
-- DROP TABLE documents CASCADE;

-- Таблица для исходных текстов (data.csv)
CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    url TEXT,
    content TEXT
);

-- Таблица для сущностей (entities.csv)
CREATE TABLE entities (
    entity_id SERIAL PRIMARY KEY,
    entity_name TEXT,
    type TEXT,
    count INTEGER
);

-- Таблица связей (doc_entities.csv)
CREATE TABLE doc_entities (
    doc_id INTEGER REFERENCES documents(doc_id),
    entity_id INTEGER REFERENCES entities(entity_id)
);


-- В русскоязычной модели SpiCy - PER, в англияйской - PERSON

-----------------------------------------------------------------------------
-- Запросы для проверки адекватности системы на фандоме "Властелин колец"
-----------------------------------------------------------------------------

-- 1. Топ-10 персонажей локации 'Мордор'

WITH docs_with_mordor AS (
    SELECT de.doc_id
    FROM doc_entities de
    JOIN entities e ON de.entity_id = e.entity_id
    WHERE e.entity_name = 'Мордор' AND e.type = 'LOC'
)
SELECT e.entity_name, COUNT(*) AS mentions
FROM doc_entities de
JOIN entities e ON de.entity_id = e.entity_id
WHERE de.doc_id IN (SELECT doc_id FROM docs_with_mordor)
  AND e.type = 'PER'
GROUP BY e.entity_name
ORDER BY mentions DESC
LIMIT 10;

-- 2. Список локаций персонажа 'Гэндальф'

WITH docs_with_gandalf AS (
    SELECT de.doc_id
    FROM doc_entities de
    JOIN entities e ON de.entity_id = e.entity_id
    WHERE e.entity_name = 'Гэндальф' AND e.type = 'PER'
)
SELECT e_loc.entity_name
FROM docs_with_gandalf d
JOIN doc_entities de ON d.doc_id = de.doc_id
JOIN entities e_loc ON de.entity_id = e_loc.entity_id
WHERE e_loc.type = 'LOC'
GROUP BY e_loc.entity_name;

-- 3. Часто упоминаемые персонажи вместе с 'Фродо Бэггинс'

WITH docs_with_frodo AS (
    SELECT de.doc_id
    FROM doc_entities de
    JOIN entities e ON de.entity_id = e.entity_id
    WHERE e.entity_name = 'Фродо Бэггинс' AND e.type = 'PER'
)
SELECT e2.entity_name, COUNT(*) AS co_occurrence
FROM docs_with_frodo d
JOIN doc_entities de ON d.doc_id = de.doc_id
JOIN entities e2 ON de.entity_id = e2.entity_id
WHERE e2.type = 'PER' AND e2.entity_name != 'Фродо Бэггинс'
GROUP BY e2.entity_name
ORDER BY co_occurrence DESC;

-- 4. Документы в которых упоминается 'Ривенделл'

WITH docs_with_rivendell AS (
    SELECT de.doc_id
    FROM doc_entities de
    JOIN entities e ON de.entity_id = e.entity_id
    WHERE e.entity_name = 'Ривенделл'
)
SELECT d.doc_id, d.title, d.url
FROM docs_with_rivendell dr
JOIN documents d ON dr.doc_id = d.doc_id;

-----------------------------------------------------------------------------
-- Запросы для проверки адекватности системы на фандоме "Леди Баг"
-----------------------------------------------------------------------------

-- 1. Топ-10 персонажей локации 'Париж'

WITH docs_with_paris AS (
    SELECT de.doc_id
    FROM doc_entities de
    JOIN entities e ON de.entity_id = e.entity_id
    WHERE e.entity_name = 'Париж' AND e.type = 'LOC'
)
SELECT e.entity_name, COUNT(*) AS mentions
FROM doc_entities de
JOIN entities e ON de.entity_id = e.entity_id
WHERE de.doc_id IN (SELECT doc_id FROM docs_with_paris)
  AND e.type = 'PER'
GROUP BY e.entity_name
ORDER BY mentions DESC
LIMIT 10;

-- 2. Список локаций персонажа 'Маринетт Дюпен-Чен'

WITH docs_with_ladybug AS (
    SELECT de.doc_id
    FROM doc_entities de
    JOIN entities e ON de.entity_id = e.entity_id
    WHERE e.entity_name = 'Маринетт Дюпен-Чен' AND e.type = 'PER'
)
SELECT DISTINCT e_loc.entity_name
FROM docs_with_ladybug d
JOIN doc_entities de ON d.doc_id = de.doc_id
JOIN entities e_loc ON de.entity_id = e_loc.entity_id
WHERE e_loc.type = 'LOC';

-- 3. Часто упоминаемые персонажи вместе с 'Супер Кот'

WITH docs_with_catnoir AS (
    SELECT de.doc_id
    FROM doc_entities de
    JOIN entities e ON de.entity_id = e.entity_id
    WHERE e.entity_name = 'Супер Кот' AND e.type = 'PER'
)
SELECT e2.entity_name, COUNT(*) AS co_occurrence
FROM docs_with_catnoir d
JOIN doc_entities de ON d.doc_id = de.doc_id
JOIN entities e2 ON de.entity_id = e2.entity_id
WHERE e2.type = 'PER' AND e2.entity_name != 'Супер Кот'
GROUP BY e2.entity_name
ORDER BY co_occurrence DESC;

-- 4. Документы, где упоминается локация 'Париж'

SELECT d.doc_id, d.title, d.url
FROM documents d
WHERE d.doc_id IN (
    SELECT de.doc_id
    FROM doc_entities de
    JOIN entities e ON de.entity_id = e.entity_id
    WHERE e.entity_name = 'Париж'
);