# Проверяем и пересохраняем csv-файлы в правильном формате для импорта в PostgreSQL
import pandas as pd
import os

files_to_fix = ['data.csv', 'doc_entities.csv', 'entities.csv']

for filename in files_to_fix:
    if not os.path.exists(filename):
        print(f'Файл "{filename}" не найден. Пропускаем.')
        continue
    print(f'Обрабатываю файл: {filename}...')
    try:
        # 1. Читаем исходный файл
        df = pd.read_csv(filename, encoding='utf-8')
        print(f'- Успешно прочитан. Найдено строк: {len(df)}.')

        # Специальная проверка для data.csv (убираем длинный текст, который мог сломаться)
        if filename == 'data.csv':
            # Заменяем все проблемные символы переноса строки внутри ячеек на пробелы
            if 'content' in df.columns:
                df['content'] = df['content'].astype(str).str.replace('\n', ' ').str.replace('\r', ' ')
                print('- Выполнена очистка текста от переносов строк внутри ячеек.')

        # 2. Сохраняем в наиболее понятном для PostgreSQL формате
        df.to_csv(filename, index=False, encoding='utf-8', quoting=1)
        print(f'- Файл "{filename}" успешно пересохранён!\n')

    except Exception as e:
        print(f'- ОШИБКА при обработке файла {filename}: {e}\n')

print("Готово. Теперь можно пробовать импортировать эти файлы снова")
