from moviepy import VideoFileClip, concatenate_videoclips
from moviepy.video.VideoClip import ColorClip
import json

def extract_segments_by_move(ts_path: str, in_video: str, out_video: str, start, end):
    with open(ts_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    clip = VideoFileClip(in_video)
    total = clip.duration
    
    result = ColorClip(size=clip.size, color=(0, 0, 0), duration=0.1)

    smove = max(0, int(start * 2 - 1))
    emove = max(smove, min(int(end * 2), len(data)))

    for move in range(smove, emove):
        stime, etime = get_timecode(ts_path, move)
        print(stime, etime)

        start = max(0.0, min(float(stime), total))
        end   = max(stime, min(float(etime), total))

        segment = clip.subclipped(start, end)
        # result = concatenate_videoclips(
        #     [result, segment],
        #     method="compose")
        # segment.close()

    result.write_videofile(
        out_video,
        codec="libx264",
        audio=False,
        ffmpeg_params=["-movflags", "+faststart"]
    )
    result.close()
    clip.close()

    return get_timecode(ts_path, moves_range[0][0])[0], \
        get_timecode(ts_path, moves_range[-1][-1])[1]



def get_timecode(ts_path: str, move):
    with open(ts_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    result, _move = 0, min(len(data), move) 
    for id in range(_move):
        result += data[id]["end_ts"] - data[id]["start_ts"]

    return result / 1000, (result + data[_move]["fragment_before_ts"]) / 1000``