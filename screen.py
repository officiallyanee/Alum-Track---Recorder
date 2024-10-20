from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

def merge_audio_video(video_path, audio_path, output_path):
    # Load the video file
    video = VideoFileClip("C:/Users/ashri/OneDrive/Desktop/New folder/output_video.mp4")
    
    # Load the audio file
    audio = AudioFileClip("C:/Users/ashri/OneDrive/Desktop/New folder/output.wav")
    
    # Set the audio of the video to the loaded audio file
    final_video = video.set_audio("C:/Users/ashri/OneDrive/Desktop/New folder/final_video.mp4")
    
    # Write the result to a file
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    
    # Close the clips
    video.close()
    audio.close()
    final_video.close()

# Usage
video_file = "C:/Users/ashri/OneDrive/Desktop/New folder/output_video.mp4"  # Path to your video file
audio_file = "C:/Users/ashri/OneDrive/Desktop/New folder/output.wav"  # Path to your audio file
output_file = "C:/Users/ashri/OneDrive/Desktop/New folder/final_video.mp4"  # Path for the output file

merge_audio_video(video_file, audio_file, output_file)