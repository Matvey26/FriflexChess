from .prompts import commenting_prompt, find_interesting_prompt
from yandex_cloud_ml_sdk import AsyncYCloudML


class AsyncDumbAnalyzer:
    def __init__(self, folder_id, api_key):
        self.sdk = AsyncYCloudML(folder_id=folder_id, auth=api_key)
        self.model_commentator = self.sdk.models.completions('yandexgpt', model_version='rc')
        self.model_analyzer = self.sdk.models.completions('yandexgpt', model_version='rc')
        self.model_analyzer = self.model_analyzer.configure(response_format='json')

    def _extract_json_content(self, text):
        """Извлекает содержимое между первой '{' и последней '}' в тексте."""
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        return text  # Возвращаем оригинальный текст, если скобки не найдены

    async def analyze(self, pgn_path):
        with open(pgn_path) as file:
            pgn_text = file.read()
            chat = [
                {'role': 'system', 'text': commenting_prompt},
                {'role': 'user', 'text': pgn_text},
            ]
            
            # Асинхронный вызов для комментария
            analyze_result = await self.model_commentator.run(chat)
            
            chat[0]['text'] = find_interesting_prompt
            chat[1]['text'] = analyze_result[0].text
            
            # Асинхронный вызов для анализа интересных моментов
            interesting_moment = await self.model_analyzer.run(chat)
            
            return self._extract_json_content(interesting_moment[0].text)