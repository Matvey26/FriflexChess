video_path = "C:/Users/matvey/Downloads/example_video.mp4"
audio_path = "C:/Users/matvey/Downloads/дроздов.wav"

"""
from video_processing.subtitles import add_subtitles_word_by_word, add_centered_subtitles

subtitle_text = "Кошка греется на солнце, лениво потягиваясь, а вдали слышен смех детей. Осенний ветер кружит золотые листья, будто приглашая их на последний танец."
start_time = 1.0  # начать через 5 секунд от начала видео
rectangle = ((100, 400), (700, 600))  # прямоугольник для размещения
duration = 10.0  # показывать субтитры 10 секунд

# Пример использования стандартной функции
# output_path = add_subtitles_word_by_word(
#     video_path, 
#     subtitle_text, 
#     start_time, 
#     rectangle, 
#     duration
# )

# Пример использования упрощенной функции с центрированием (80% ширины)
output_path = add_centered_subtitles(
    video_path=video_path,
    text=subtitle_text,
    y_position=500,  # только вертикальная позиция
    start_time=start_time,
    duration=duration,
    font_size=40  # увеличенный размер шрифта для наглядности
)
"""



"""
from video_processing.audio_on_video import overlay_audio_on_video


overlay_audio_on_video(
    video_path=video_path,
    audio_path=audio_path,
    start_time_seconds=0,  # начинаем с 10.5 секунды
    output_path="C:/Users/matvey/Downloads/output.mp4"
)
"""


import json
import os
from tts import setup_translation_models, smart_translate, TTSEngine, setup_environment, create_output_dir

# Инициализация
setup_environment()
output_dir = create_output_dir()

# Загрузка комментариев (внешний код)
def load_comments(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

rus_comments = load_comments("rus_comments.json")

# Перевод
setup_translation_models()
all_comments = {"ru": rus_comments}
for lang in ["en", "fr", "es", "de", "hi"]:
    all_comments[lang] = {
        key: smart_translate(txt, "ru", lang)
        for key, txt in rus_comments.items()
    }

# Сохранение переводов
with open(os.path.join(output_dir, "comments_translated.json"), "w", encoding="utf-8") as fp:
    json.dump(all_comments, fp, ensure_ascii=False, indent=2)

# Синтез речи
tts = TTSEngine()
for lang, comments in all_comments.items():
    for key, txt in comments.items():
        out_path = os.path.join(output_dir, f"{lang}_{key}.wav")
        tts.synthesize(txt, lang, out_path)