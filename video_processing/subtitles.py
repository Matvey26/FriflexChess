import os
import textwrap
from typing import Tuple, List
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

def create_text_frame(text, size, font_size=30, font_color="white", bg_color=None):
    """Create a frame with text using PIL instead of TextClip"""
    width, height = size
    # Create a transparent image (RGBA)
    img = Image.new('RGBA', size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Use a default font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw the text centered - use getbbox instead of textsize which is deprecated
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, font=font, fill=font_color)
    
    return np.array(img)

def add_subtitles(
    video_path: str,
    text: str,
    start_time: float,
    rectangle: Tuple[Tuple[int, int], Tuple[int, int]],
    duration: float,
    font: str = "Arial",
    font_size: int = 30,
    font_color: str = "white",
    bg_color: str = "black",
    output_path: str = None
) -> str:
    """
    Add subtitles to a video, gradually displaying words within a rectangle.
    
    Args:
        video_path: Path to the video file
        text: Subtitle text to display
        start_time: Time in seconds when subtitles should start
        rectangle: ((x1, y1), (x2, y2)) - Top left and bottom right points of the rectangle
        duration: Duration in seconds for the entire text to be displayed
        font: Font name
        font_size: Font size
        font_color: Font color
        bg_color: Background color for the text
        output_path: Path for the output video. If None, will use original filename + "_subtitled"
    
    Returns:
        Path to the output video file
    """
    # Load the video
    video = VideoFileClip(video_path)
    
    # Calculate rectangle dimensions
    (x1, y1), (x2, y2) = rectangle
    rect_width = x2 - x1
    rect_height = y2 - y1
    
    # Split text into words
    words = text.split()
    
    # Create a TextClip to estimate character width
    temp_clip = TextClip(" ", fontsize=font_size, color=font_color)
    char_width = temp_clip.w / 1
    
    # Estimate max chars per line based on rectangle width
    max_chars_per_line = int(rect_width / (char_width * 0.7))  # 0.7 is a safety factor
    
    # Wrap text into lines that fit in the rectangle
    wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
    
    # Create a list of subtitle clips
    subtitle_clips = []
    
    # Calculate time per line
    time_per_line = duration / len(wrapped_lines)
    
    # Create a clip for each line
    for i, line in enumerate(wrapped_lines):
        line_start_time = start_time + (i * time_per_line)
        
        txt_clip = (TextClip(line, fontsize=font_size, color=font_color, bg_color=bg_color, method='caption')
                   .set_position((x1, y1 + (i * font_size * 1.5)))
                   .set_start(line_start_time)
                   .set_duration(time_per_line))
                   
        subtitle_clips.append(txt_clip)
    
    # Overlay all subtitle clips on the video
    final_video = CompositeVideoClip([video] + subtitle_clips)
    
    # Set output path
    if output_path is None:
        filename, ext = os.path.splitext(video_path)
        output_path = f"{filename}_subtitled{ext}"
    
    # Write the result to a file
    final_video.write_videofile(output_path)
    
    return output_path


def add_subtitles_word_by_word(
    video_path: str,
    text: str,
    start_time: float,
    rectangle: Tuple[Tuple[int, int], Tuple[int, int]],
    duration: float,
    font_size: int = 30,
    font_color: str = "white",
    output_path: str = None
) -> str:
    """
    Add subtitles to a video, gradually displaying one or two words at a time.
    
    Args:
        video_path: Path to the video file
        text: Subtitle text to display
        start_time: Time in seconds when subtitles should start
        rectangle: ((x1, y1), (x2, y2)) - Top left and bottom right points of the rectangle
        duration: Duration in seconds for the entire text to be displayed
        font_size: Font size
        font_color: Font color
        output_path: Path for the output video. If None, will use original filename + "_subtitled"
    
    Returns:
        Path to the output video file
    """
    # Load the video
    video = VideoFileClip(video_path)
    
    # Calculate rectangle dimensions
    (x1, y1), (x2, y2) = rectangle
    rect_width = x2 - x1
    rect_height = y2 - y1
    
    # Split text into words
    words = text.split()
    
    # Group words into chunks of 1-2 words
    chunks = []
    i = 0
    while i < len(words):
        # If we have only one word left or the current word is long, use just one word
        if i == len(words) - 1 or len(words[i]) >= 10:
            chunks.append(words[i])
            i += 1
        # Otherwise, use two words
        else:
            chunks.append(f"{words[i]} {words[i+1]}")
            i += 2
    
    # Create a list of subtitle clips
    subtitle_clips = []
    
    # Calculate time per chunk
    time_per_chunk = duration / len(chunks)
    
    # Fixed position for all subtitles (centered in the rectangle)
    position_y = y1 + (rect_height // 2) - font_size
    
    # Create a clip for each chunk
    for i, chunk in enumerate(chunks):
        chunk_start_time = start_time + (i * time_per_chunk)
        
        # Create subtitle image with PIL
        text_img = create_text_frame(chunk, (rect_width, font_size * 2), 
                                    font_size=font_size, 
                                    font_color=font_color)
        
        # Convert to MoviePy clip with transparency
        txt_clip = (ImageClip(text_img, transparent=True)
                   .set_position((x1, position_y))
                   .set_start(chunk_start_time)
                   .set_duration(time_per_chunk))
                   
        subtitle_clips.append(txt_clip)
    
    # Overlay all subtitle clips on the video
    final_video = CompositeVideoClip([video] + subtitle_clips)
    
    # Set output path
    if output_path is None:
        filename, ext = os.path.splitext(video_path)
        output_path = f"{filename}_subtitled{ext}"
    
    # Write the result to a file
    final_video.write_videofile(output_path)
    
    return output_path

def add_centered_subtitles(
    video_path: str,
    text: str,
    y_position: int,
    start_time: float,
    duration: float,
    font_size: int = 30,
    font_color: str = "white",
    output_path: str = None
) -> str:
    """
    Add subtitles to a video, centered horizontally with 80% of video width.
    
    Args:
        video_path: Path to the video file
        text: Subtitle text to display
        y_position: Vertical position (y-coordinate) for the subtitles
        start_time: Time in seconds when subtitles should start
        duration: Duration in seconds for the entire text to be displayed
        font_size: Font size
        font_color: Font color
        output_path: Path for the output video. If None, will use original filename + "_subtitled"
    
    Returns:
        Path to the output video file
    """
    # Load the video to get dimensions
    video = VideoFileClip(video_path)
    video_width, video_height = video.size
    
    # Calculate the rectangle that's 80% of video width and centered
    rect_width = int(video_width * 0.8)
    x1 = (video_width - rect_width) // 2  # Center horizontally
    x2 = x1 + rect_width
    
    # Use the specified y_position and add enough height for text
    y1 = y_position
    y2 = y_position + font_size * 2
    
    # Create rectangle coordinates
    rectangle = ((x1, y1), (x2, y2))
    
    # Use the existing function with our calculated rectangle
    return add_subtitles_word_by_word(
        video_path=video_path,
        text=text,
        start_time=start_time,
        rectangle=rectangle,
        duration=duration,
        font_size=font_size,
        font_color=font_color,
        output_path=output_path
    )