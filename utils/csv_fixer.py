# Проверяем и пересохраняем csv-файлы в правильном формате для импорта в PostgreSQL
# Запускать из корневой папки fandom_wiki_parser командой: python utils/csv_fixer.py

import pandas as pd
import os

# Пути к файлам (относительно корневой папки fandom_wiki_parser )
files_config = {
    'data.csv': 'data/raw/data.csv',
    'entities.csv': 'data/processed/entities.csv',
    'doc_entities.csv': 'data/processed/doc_entities.csv'
}

for short_name, filepath in files_config.items():
    if not os.path.exists(filepath):
        print(f'Файл "{filepath}" не найден. Пропускаем.')
        continue
    
    print(f'Обрабатываю: {short_name}...')
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        print(f'- Успешно прочитан. Найдено строк: {len(df)}')
        
        # Очищаем data.csv от лишних переносов строк
        if short_name == 'data.csv' and 'content' in df.columns:
            df['content'] = df['content'].astype(str).str.replace('\n', ' ').str.replace('\r', ' ')
            print('- Выполнена очистка текста от переносов строк внутри ячеек')
        
        # Сохраняем (перезаписываем тот же файл)
        df.to_csv(filepath, index=False, encoding='utf-8', quoting=1)
        print(f'- Файл "{short_name}" пересохранён!\n')
        
    except Exception as e:
        print(f'- Ошибка при обработке файла "{short_name}": {e}\n')

print('Готово. Можно импортировать файлы в PostgreSQL')