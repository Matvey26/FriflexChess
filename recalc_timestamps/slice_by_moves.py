from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.VideoClip import ColorClip
import json

def extract_segments_by_move(ts_path: str, in_video: str, out_video: str, moves_range: list):
    with open(ts_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    clip = VideoFileClip(in_video)
    total = clip.duration
    
    result = ColorClip(size=clip.size, color=(0, 0, 0), duration=0.1)

    for fr, to in moves_range:
        smove = int(max(0, fr * 2 - 1))
        emove = int(max(smove, min(to * 2, len(data))))

        for move in range(smove, emove):
            stime = (data[move]["start_ts"] - data[0]["start_ts"]) / 1000
            etime = (data[move]["start_ts"] - data[0]["start_ts"] + data[move]["fragment_before_ts"]) / 1000

            start = max(0.0, min(float(stime), total))
            end   = max(stime, min(float(etime), total))

            segment = clip.subclipped(start, end)
            result = concatenate_videoclips(
                [result, segment],
                method="compose")
            segment.close()

    result.write_videofile(
        out_video,
        codec="libx264",
        audio=False,
        ffmpeg_params=["-movflags", "+faststart"]
    )
    result.close()
    clip.close()

    # TODO: debug
    start_ts = max(0, data[moves_range[0][0]]["start_ts"] - data[0]["start_ts"])
    end_ts = min(
        data[moves_range[-1][-1]]["start_ts"] - data[0]["start_ts"] + data[moves[-1][-1]]["fragment_before_ts"], 
        data[-1]["end_ts"] - data[0]["start_ts"]
    )
    return start_ts, end_ts
        