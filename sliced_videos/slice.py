from moviepy import VideoFileClip

def extract_chess_segment(input_path, output_path, start, end, event_ts):
    """
    Выбирает из видео отрезок [start, end], сохраняет его в output_path
    и возвращает скорректированный внутрифрагментный таймстамп (или None).
    """
    clip = VideoFileClip(input_path)
    total = clip.duration
    start = max(0.0, min(float(start), total))
    end   = max(start, min(float(end), total))

    segment = clip.subclipped(start, end)
    segment.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        ffmpeg_params=["-movflags", "+faststart"]
    )

    if event_ts < start or event_ts > end:
        new_ts = None
    else:
        new_ts = round(event_ts - start, 2)

    clip.close()
    segment.close()
    return new_ts