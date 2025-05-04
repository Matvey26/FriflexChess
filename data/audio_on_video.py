from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip


def parse_timecode(tc_str: str) -> float:
    """
    Переводит таймкод из строкового формата в секунды.
    """
    parts = [float(p) for p in tc_str.split(':')]
    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = parts
        return m * 60 + s
    elif len(parts) == 1:
        return parts[0]
    else:
        raise ValueError(f"Неверный формат таймкода: {tc_str}")


def overlay_audio_on_video(video_path: str, audio_path: str, timecode: str, output_path: str) -> None:
    """
    Накладывает аудио на видео в заданный таймкод и сохраняет результат.
    """
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    start_t = parse_timecode(timecode)
    delayed_audio = audio_clip.with_start(start_t)

    if video_clip.audio:
        mixed_audio = CompositeAudioClip([video_clip.audio, delayed_audio])
    else:
        mixed_audio = CompositeAudioClip([delayed_audio])

    final_clip = video_clip.with_audio(mixed_audio)
    final_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )

