import json
import os
from typing import Literal, Dict, Any, Optional
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML
from .prompts import (
    analyzing_prompt,
    vivid_commenting_prompt,
    dry_commenting_prompt,
    meme_commenting_prompt
)

class Commentator:
    """
    Класс для анализа шахматных партий с использованием моделей Yandex GPT.
    Предоставляет функциональность для анализа PGN файлов и генерации комментариев в различных стилях.
    """
    
    def __init__(self, folder_id: str, api_key: str):
        """
        Инициализация анализатора с учетными данными Yandex Cloud.
        
        Args:
            folder_id: ID папки в Yandex Cloud
            api_key: API ключ Yandex Cloud
        """
        try:
            self.sdk = YCloudML(folder_id=folder_id, auth=api_key)
            self.model_commentator = self.sdk.models.completions('yandexgpt', model_version='rc')
            self.model_analyzer = self.sdk.models.completions('yandexgpt', model_version='rc')
            self.model_analyzer = self.model_analyzer.configure(response_format='json')
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Yandex Cloud ML SDK: {str(e)}")
    
    def _extract_json_content(self, text):
        """Извлекает содержимое между первой '{' и последней '}' в тексте."""
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        return text  # Возвращаем оригинальный текст, если скобки не найдены

    def make_comments(self, pgn_path: str, start: int, end: int, style: Literal['vivid', 'dry', 'meme'] = 'vivid') -> Dict[str, Any]:
        """
        Анализирует шахматную партию из PGN файла и генерирует комментарии.
        
        Args:
            pgn_path: Путь к PGN файлу
            start: Номер начального хода для анализа
            end: Номер конечного хода для анализа
            style: Стиль комментариев ('vivid', 'dry' или 'meme')
            
        Returns:
            Словарь с результатами анализа
            
        Raises:
            FileNotFoundError: Если PGN файл не существует
            ValueError: Если номера ходов недопустимы
            RuntimeError: Если анализ модели не удался
        """
        if not os.path.exists(pgn_path):
            raise FileNotFoundError(f"PGN file not found: {pgn_path}")
            
        if start < 1 or end < start:
            raise ValueError(f"Invalid move range: start={start}, end={end}")
            
        try:
            with open(pgn_path, 'r', encoding='utf-8') as file:
                pgn_text = file.read()
                
            if not pgn_text.strip():
                raise ValueError("PGN file is empty")
                
            # Первый проход: Получаем аннотированный PGN
            chat = [
                {'role': 'system', 'text': analyzing_prompt},
                {'role': 'user', 'text': pgn_text},
            ]
            
            try:
                annotated_response = self.model_commentator.run(chat)
                if not annotated_response or not annotated_response[0].text:
                    raise RuntimeError("Failed to get annotated PGN from model")
                annotated_pgn = annotated_response[0].text
            except Exception as e:
                raise RuntimeError(f"Failed to get annotated PGN: {str(e)}")
            
            # Выбираем подходящий промпт для комментариев в зависимости от стиля
            commenting_prompt = None
            match style:
                case 'dry':
                    commenting_prompt = dry_commenting_prompt
                case 'vivid':
                    commenting_prompt = vivid_commenting_prompt
                case 'meme':
                    commenting_prompt = meme_commenting_prompt
                case _:
                    raise ValueError(f"Invalid style: {style}")

            # Второй проход: Анализируем аннотированный PGN
            analysis_chat = [
                {'role': 'system', 'text': commenting_prompt},
                {'role': 'user', 'text': f'''
                    PGN с комментариями:
                    {annotated_pgn}
                    Диапазон с интересным моментом: {start} — {end}
                '''}
            ]
            
            try:
                result = self._extract_json_content(self.model_analyzer.run(analysis_chat)[0].text)
                if not result:
                    raise RuntimeError("Failed to get analysis from model")
                return json.loads(result)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse model response as JSON: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"Failed to analyze PGN: {str(e)}")
                
        except Exception as e:
            raise RuntimeError(f"Analysis failed: {str(e)}")