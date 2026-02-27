import os
import logging
from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip, ColorClip

logging.basicConfig(level=logging.INFO)

def generate_viral_video(audio_path: str, transcript_data: list, output_path: str = "data/viral/clip.mp4"):
    """
    Takes a highly-dense knowledge audio clip and generates a vertical (9:16) video
    with Hermozi-style kinetic typography popping onto the screen word-by-word.
    
    transcript_data expects a list of words with timestamps:
    [{"word": "Let's", "start": 0.0, "end": 0.2}, ...]
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        logging.info(f"Loading audio for viral export: {audio_path}")
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # Create a deep dark background (TikTok vertical format: 1080x1920)
        bg_clip = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=duration)
        
        # Build TextClips for each word
        text_clips = []
        for word_info in transcript_data:
            start_t = word_info['start']
            end_t = word_info['end']
            word_dur = end_t - start_t
            
            # Simple bold, center-screen text. 
            # In a full-scale app, we'd use custom fonts, yellow highlights, and scale animations
            try:
                txt_clip = TextClip(
                    word_info['word'].upper(), 
                    fontsize=120, 
                    color='white', 
                    bg_color='transparent',
                    font='Arial-Bold'
                )
                txt_clip = txt_clip.set_position('center')
                                   .set_start(start_t)
                                   .set_duration(word_dur)
                                   .crossfadein(0.05)
                text_clips.append(txt_clip)
            except Exception as inner_e:
                logging.warning(f"Failed to create TextClip for word '{word_info['word']}': {inner_e}")
                
        # Composite the video
        logging.info(f"Compositing {len(text_clips)} kinetic text elements...")
        video = CompositeVideoClip([bg_clip] + text_clips)
        video = video.set_audio(audio)
        
        # Write output (H.264, AAC for social media compatibility)
        video.write_videofile(
            output_path, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac", 
            threads=4, 
            preset="fast"
        )
        
        logging.info(f"Viral snippet successfully generated at: {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"Error generating viral video: {e}")
        return None

if __name__ == "__main__":
    print("Viral Video Generation module loaded.")
