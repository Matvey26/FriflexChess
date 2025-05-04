import os
import streamlit as st
import json
import io
import tempfile
from dotenv import load_dotenv
from highlighter import find_highlight
from llm_commentator import Commentator
from video_processing.audio_on_video import overlay_audio_on_video
from video_processing.subtitles import add_centered_subtitles
from recalc_timestamps import extract_segments_by_move
from tts import (
    setup_translation_models,
    smart_translate,
    TTSEngine,
    setup_environment,
    create_output_dir
)

# Настраиваем окружение
load_dotenv()
setup_environment()
setup_translation_models()

# Настраиваем глобальные переменные
output_dir = create_output_dir('tmp')
folder_id = os.environ['folder_id']
api_key = os.environ['api_key']

# Создаём необходимые инструменты
commentator = Commentator(folder_id, api_key)
tts = TTSEngine()


def process_files(video_path, pgn_path, json_path, mode, lang):
    """
    process_files: заглушка для обработки файлов
    Args:
        video_path: путь к загруженному видео
        pgn_path: путь к PGN-файлу с партией из видео
        json_path: путь к JSON-файлу с информацией о ходах
        mode: режим генерации
    Returns:
    """

    # Ищем интересный момент
    interesting_moment = find_highlight(pgn_path)
    start, end = interesting_moment['start'], interesting_moment['end']

    # Генерируем комментарии
    comments = commentator.make_comments(pgn_path, start, end, 'vivid')

    # Обрезаем видео
    output_dir = '/'.join(video_path.split('/')[:-1])
    # start_ts, end_ts - от начала видео в секундах - таймкод начала момента и таймкод конца момента
    start_ts, end_ts = extract_segments_by_move(json_path, video_path, f'{output_dir}/result.mp4', [[start, end]])

    # Переводим комментарии
    if lang != 'ru':
        comments = {
            key: smart_translate(text, "ru", lang)
            for key, text in comments.items()
        }

    # Озвучиваем
    durations = {}
    for key, text in comments.item():
        out_path = os.path.join(output_dir, f'{key}.wav')
        dur = tts.synthesize(text, lang, out_path)
        durations[key] = dur

    # Вставляем аудио в видео
    tmp_video_path = os.path.join(output_dir, f'tmp.mp4')
    overlay_audio_on_video(
        video_path=f'{output_dir}/result.mp4',
        audio_path=audio_path,
        start_time_seconds=start_ts - durations['introduction'],
        output_path=tmp_video_path
    )
    overlay_audio_on_video(
        video_path=tmp_video_path,
        audio_path=audio_path,
        start_time_seconds=start_ts,
        output_path=tmp_video_path
    )
    overlay_audio_on_video(
        video_path=tmp_video_path,
        audio_path=audio_path,
        start_time_seconds=end_ts,
        output_path=tmp_video_path
    )

    # Добавляем субтитры
    _ = add_centered_subtitles(
        video_path=tmp_video_path,
        text=comments['introduction'],
        y_position=500,
        start_time=start_ts - durations['introduction'],
        duration=durations['introduction'],
        font_size=40,
        output_path=tmp_video_path
    )
    _ = add_centered_subtitles(
        video_path=tmp_video_path,
        text=comments['interesting_moment'],
        y_position=500,
        start_time=start_ts,
        duration=durations['interesting_moment'],
        font_size=40,
        output_path=tmp_video_path
    )
    _ = add_centered_subtitles(
        video_path=tmp_video_path,
        text=comments['conclusion'],
        y_position=500,
        start_time=end_ts,
        duration=durations['conclusion'],
        font_size=40,
        output_path=tmp_video_path
    )

    return tmp_video_path



def save_uploaded_file(uploaded_file, suffix=""):
    """Сохраняет загруженный файл во временный файл и возвращает его путь"""
    if not uploaded_file:
        return None
        
    # Создаем временный файл с правильным расширением
    file_ext = uploaded_file.name.split('.')[-1]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}')
    
    # Записываем содержимое загруженного файла во временный файл
    temp_file.write(uploaded_file.getvalue())
    temp_file.close()
    
    return temp_file.name


def main():
    st.set_page_config(page_title="Файловый загрузчик и плеер", layout="wide")
    st.title("Загрузка файлов и воспроизведение видео")

    with st.sidebar:
        st.header("Загрузить файлы")
        video_file = st.file_uploader("Выберите видео", type=["mp4", "mov", "avi"] )
        pgn_file = st.file_uploader("Выберите PGN-файл", type=["pgn"] )
        json_file = st.file_uploader("Выберите JSON-файл", type=["json"] )
        mode = st.selectbox("Выберите режим генерации", ["dry", "vivid", "meme"])
        lang = st.selectbox("Выберите язык генерации", ["ru", "en", "fr", "es", "de", "hi"])
        run = st.button("Запустить обработку")

    if run:
        if not video_file:
            st.error("Пожалуйста, загрузите видео файл.")
            return

        # Сохраняем загруженные файлы во временные файлы
        video_path = save_uploaded_file(video_file)
        pgn_path = save_uploaded_file(pgn_file)
        json_path = save_uploaded_file(json_file)

        # video_bytes = video_file.read()
        # pgn_text = pgn_file.read().decode('utf-8') if pgn_file else None
        # try:
        #     json_data = json.loads(json_file.read()) if json_file else None
        # except Exception as e:
        #     st.error(f"Ошибка при чтении JSON: {e}")
        #     return

        with st.spinner("Обработка файлов..."):
            processed_video = process_files(video_path, pgn_path, json_path, mode, lang)

        if processed_video:
            st.success("Обработка завершена! Воспроизведение видео ниже.")
            st.markdown("### Просмотр видео")
            st.video(processed_video, format="video/mp4", start_time=0)

            # Удаляем временные файлы после использования (по желанию)
            for path in [video_path, pgn_path, json_path, processed_video]:
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except:
                        pass
        else:
            st.warning("Видео не было обработано.")

        if pgn_text:
            with st.expander("Содержимое PGN файла"):
                st.text(pgn_text)
        if json_data:
            with st.expander("Содержимое JSON файла"):
                st.json(json_data)

if __name__ == "__main__":
    main()
