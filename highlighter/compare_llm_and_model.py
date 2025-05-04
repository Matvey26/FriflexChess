import os
import csv
import json
import asyncio
import pandas as pd
from json.decoder import JSONDecodeError
from dotenv import load_dotenv
from highlighter.llm.analyze import AsyncDumbAnalyzer

load_dotenv()

folder_id = os.environ['folder_id']
api_key = os.environ['api_key']

csv_file = 'C:/Users/matvey/Documents/chess_data/dataset_for_comparsion/_info.csv'
output_path = 'comparsion3.csv'
BATCH_SIZE = 5  # Размер батча для параллельной обработки
MAX_RETRIES = 3  # Количество попыток для каждого запроса

async def process_game(analyzer: AsyncDumbAnalyzer, path: str) -> tuple | None:
    """Обрабатывает одну игру с несколькими попытками"""
    for _ in range(MAX_RETRIES):
        try:
            llm_response = await analyzer.analyze(path)
            llm_result = json.loads(llm_response)
            return (int(llm_result['start']) - 1) * 2, (int(llm_result['end']) - 1) * 2
        except JSONDecodeError:
            continue
        except Exception as e:
            print(f'Ошибка при обработке {path}: {e}')
            continue
    return None

async def process_batch(analyzer: AsyncDumbAnalyzer, batch: list[dict]) -> list:
    """Обрабатывает батч игр параллельно"""
    tasks = [process_game(analyzer, row['path_to_pgn']) for row in batch]
    return await asyncio.gather(*tasks)

async def main():
    analyzer = AsyncDumbAnalyzer(folder_id, api_key)
    data = {
        'start_dataset': [],
        'end_dataset': [],
        'start_llm': [],
        'end_llm': []
    }

    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = list(csv.DictReader(file))[200:400]  # Ограничиваем 100 записями
        
        # Обрабатываем данные батчами
        for i in range(0, len(reader), BATCH_SIZE):
            batch = reader[i:i+BATCH_SIZE]
            results = await process_batch(analyzer, batch)
            
            for row, llm_result in zip(batch, results):
                if llm_result is None:
                    continue

                marks = list(map(int, row['marks'].split(',')))
                data['start_dataset'].append(marks[0])
                data['end_dataset'].append(marks[1])
                data['start_llm'].append(llm_result[0])
                data['end_llm'].append(llm_result[1])
                print(marks, llm_result)

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)

if __name__ == '__main__':
    asyncio.run(main())