from moviepy import VideoFileClip
import os

def slice_video(input_path, output_path, start, end) -> str:
    """
    Вырезает из видео отрезок [start, end] и сохраняет его в output_path.
    
    Args:
        input_path (str): Путь к исходному видеофайлу
        output_path (str): Путь для сохранения вырезанного сегмента
        start (float): Время начала сегмента в секундах от начала видео
        end (float): Время конца сегмента в секундах от начала видео
    
    Returns:
        str: Путь, по которому сохранено видео
    
    Raises:
        FileNotFoundError: Если исходный файл не существует
        ValueError: Если start > end или если временные метки некорректны
    """
    # Проверка существования входного файла
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Исходный файл не найден: {input_path}")
    
    # Проверка корректности временных меток
    if start < 0 or end < 0:
        raise ValueError("Временные метки не могут быть отрицательными")
    if start > end:
        raise ValueError("Время начала не может быть больше времени конца")
    
    try:
        # Загрузка видео
        clip = VideoFileClip(input_path)
        total = clip.duration
        
        # Корректировка временных меток, если они выходят за пределы видео
        start = max(0.0, min(float(start), total))
        end = max(start, min(float(end), total))
        
        # Вырезание сегмента
        segment = clip.subclipped(start, end)
        
        # Сохранение сегмента
        segment.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            ffmpeg_params=["-movflags", "+faststart"]
        )
        
        # Возвращаем длительность вырезанного сегмента
        return output_path
        
    finally:
        # Закрытие видеофайлов
        if 'clip' in locals():
            clip.close()
        if 'segment' in locals():
            segment.close()