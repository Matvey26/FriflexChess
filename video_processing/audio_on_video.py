import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip


def overlay_audio_on_video(
    video_path: str,
    audio_path: str,
    start_time_seconds: float,
    output_path: str
) -> None:
    """
    Накладывает аудио на видео, начиная с указанного времени (в секундах),
    и сохраняет результат в output_path.

    Args:
        video_path: Путь к исходному видеофайлу
        audio_path: Путь к аудиофайлу для наложения
        start_time_seconds: Время начала аудио в секундах (может быть float)
        output_path: Путь для сохранения результата

    Raises:
        ValueError: Если start_time_seconds отрицательное или выходит за пределы видео
        IOError: Если файлы не найдены или недоступны
    """
    # Проверка корректности start_time_seconds
    if start_time_seconds < 0:
        raise ValueError("Время начала не может быть отрицательным")

    try:
        # Загружаем видео и аудио
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)

        # Проверяем, что аудио не выходит за пределы видео
        if start_time_seconds + audio_clip.duration > video_clip.duration:
            raise ValueError(
                f"Аудио выходит за пределы видео. Длительность видео: {video_clip.duration} сек, "
                f"а аудио заканчивается на {start_time_seconds + audio_clip.duration} сек"
            )

        # Создаем отложенное аудио
        delayed_audio = audio_clip.set_start(start_time_seconds)

        # Микшируем аудио (исходное + новое)
        audio_tracks = [delayed_audio]
        if video_clip.audio:
            audio_tracks.insert(0, video_clip.audio)

        mixed_audio = CompositeAudioClip(audio_tracks)

        # Создаем финальный клип
        final_clip = video_clip.set_audio(mixed_audio)

        # Сохраняем результат
        try:
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True
            )
        finally:
            # Всегда закрываем клипы
            final_clip.close()
            video_clip.close()
            audio_clip.close()

    except Exception as e:
        # Закрываем клипы в случае ошибки
        if 'video_clip' in locals():
            video_clip.close()
        if 'audio_clip' in locals():
            audio_clip.close()
        raise e