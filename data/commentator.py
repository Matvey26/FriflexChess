import json
import os
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML
from prompts import commenting_prompt, vivid_interesting_prompt, dry_interesting_prompt

class DumbAnalyzer:
    def __init__(self, folder_id, api_key):
        self.sdk = YCloudML(folder_id=folder_id, auth=api_key)
        self.model_commentator = self.sdk.models.completions('yandexgpt', model_version='rc')
        self.model_analyzer = self.sdk.models.completions('yandexgpt', model_version='rc')
        self.model_analyzer = self.model_analyzer.configure(response_format='json')

    def analyze(self, pgn_path, start, end, style='vivid'):
        with open(pgn_path) as file:
            pgn_text = file.read()
            
            chat = [
                {'role': 'system', 'text': commenting_prompt},
                {'role': 'user', 'text': pgn_text},
            ]
            
            annotated_pgn = self.model_commentator.run(chat)[0].text
            
            if style == 'dry':
                interesting_prompt = dry_interesting_prompt
            else:
                interesting_prompt = vivid_interesting_prompt
            
            analysis_chat = [
                {'role': 'system', 'text': interesting_prompt},
                {'role': 'user', 'text': f'''
                    PGN с комментариями:
                    {annotated_pgn}
                    Анализируемый диапазон: {start} — {end}
                '''}
            ]
            
            result = self.model_analyzer.run(analysis_chat)
            return json.loads(result[0].text)
