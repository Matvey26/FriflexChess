import streamlit as st
import json
import io


def process_files(video_bytes, pgn_text, json_data, theme):
    """
    process_files: заглушка для обработки файлов
    Args:
        video_bytes: bytes загруженного видео
        pgn_text: строка с контентом PGN-файла
        json_data: объект, загруженный из JSON-файла
        theme: выбранная тема генерации
    Returns:
    """
    # TODO:
    return video_bytes


def main():
    st.set_page_config(page_title="Файловый загрузчик и плеер", layout="wide")
    st.title("Загрузка файлов и воспроизведение видео")

    with st.sidebar:
        st.header("Загрузить файлы")
        video_file = st.file_uploader("Выберите видео", type=["mp4", "mov", "avi"] )
        pgn_file = st.file_uploader("Выберите PGN-файл", type=["pgn"] )
        json_file = st.file_uploader("Выберите JSON-файл", type=["json"] )
        theme = st.selectbox("Выберите тему генерации", ["dry", "vivit", "meme"])
        run = st.button("Запустить обработку")

    if run:
        if not video_file:
            st.error("Пожалуйста, загрузите видео файл.")
            return

        video_bytes = video_file.read()
        pgn_text = pgn_file.read().decode('utf-8') if pgn_file else None
        try:
            json_data = json.loads(json_file.read()) if json_file else None
        except Exception as e:
            st.error(f"Ошибка при чтении JSON: {e}")
            return

        with st.spinner("Обработка файлов..."):
            processed_video = process_files(video_bytes, pgn_text, json_data, theme)

        if processed_video:
            st.success("Обработка завершена! Воспроизведение видео ниже.")
            st.markdown("### Просмотр видео")
            st.video(processed_video, format="video/mp4", start_time=0)
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
