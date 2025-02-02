import os
import uuid
import shutil
from image_generator import ImageGenerator
from moviepy.editor import ImageClip, concatenate_videoclips,AudioFileClip
from function_wrap_center import add_text_to_image
from gtts import gTTS
from structured_output import StructuredOutputExtractor
from pydantic import BaseModel, Field


class YoutubeShortGenerator:

    def __init__(self):
        self.video_title = None
        self.result = None
        self.media_dir = 'generated_media'
        self.generated_video_dir = None
        self.image_dir = None
        self.audio_clips_dir = None
        self.video_path = None

        os.makedirs(self.media_dir,exist_ok=True)

    def title_to_keywords(self, title):
        # Define your data extraction model here
        class TopN(BaseModel):
            title: str = Field(description="the title of the youtube video")
            title_image_prompt: str = Field(description="highly detailed and descriptive image prompt for the background image of Title")
            items: list[str] = Field(description="top n number of requested items")
            items_image_prompts: list[str] = Field(description="highly detailed and descriptive image prompts for each item ")

        # Assuming StructuredOutputExtractor is defined and functional
        extractor = StructuredOutputExtractor(response_schema=TopN)
        result = extractor.extract(title)
        self.result = result

        # create main directory for saving  video related content  i.e images, audio_clips
        video_title = self.result.title
        unique_id = uuid.uuid4().hex
        folder_path = f"{self.media_dir}/generated_{video_title}_{unique_id}"
        self.generated_video_dir = folder_path

        return self
    
    def generate_images(self):
        if not self.result:
            print("No data available. Call title_to_keywords first.")
            return self
        
        print(self.result,'inside generate_images()')
        
        generator = ImageGenerator()  # Your custom image generator
        folder_path = f"{self.generated_video_dir}/generated_images"  # Append unique ID
        os.makedirs(folder_path, exist_ok=True)  # Ensure directory is created
        self.image_dir = folder_path

        # Generate Title Image
        # generator.generate_image(self.result.title_image_prompt, path=f"{folder_path}/title.png")
        print("Title Prompt: ",self.result.title_image_prompt)

        # generate images using stable-diffusion-turbo
        generator.generate_image(self.result.title_image_prompt, path=f"{folder_path}/title.png")


        print("Generating Images...")
        image_prompts = self.result.items_image_prompts
        print("items image prompts: ", image_prompts)
        image_prompts = reversed(image_prompts)
        print("Image Prompts: ", image_prompts)  # Placeholder for actual image processing

        # Generate and save images
        for index, image_prompt in enumerate(image_prompts):
            
            # generate images using stable-diffusion-turbo
            generator.generate_image(image_prompt, f"{folder_path}/{index}.png" )  
            print(f"Image {index} saved.")

        return self  # Return self for further chaining if needed
    

    def overlay_text_to_images(self):
        if not self.result:
            print("No data available. Call title_to_keywords first.")
            return self
        
        title_text = self.result.title
        text_items = reversed(self.result.items)
        print("text_items ",text_items)

        # add text to title image
        add_text_to_image(text=title_text,image_path=f"{self.image_dir}/title.png", save_to=f"{self.image_dir}/title.png")
        
        # add text to other images
        for index, text in enumerate(text_items):
            image_path = f"{self.image_dir}/{index}.png"
            add_text_to_image(text=text,image_path=image_path,is_title=False, save_to=image_path)

        return self
        
        

    
    def generate_audio_clips(self):
        if not self.result:
            print("No data available. Call title_to_keywords first.")
            return self
        
        print("Generating Title Audio...")
        overlay_title = self.result.title
        print("Title: ", overlay_title)

        
        print("Generating Audio Clips...")
        overlay_text_items = reversed(self.result.items)
        print("Overlay Text: ", overlay_text_items)  # Placeholder for actual text processing

        folder_path = f"{self.generated_video_dir}/generated_audio_clips"  # Append unique ID
        self.audio_clips_dir = folder_path

        os.makedirs(folder_path, exist_ok=True)  # Ensure directory is created

        # Generate title Audio
        title_tts = gTTS(text=overlay_title)
        title_tts.save(f"{folder_path}/title.mp3")
        print(f"Title Audio clip title.mp3 saved.")

        # Generate and save audio clips
        for index, text_overlay in enumerate(overlay_text_items):
            tts = gTTS(text=text_overlay)  # Generate audio clip
            tts.save(f"{folder_path}/{index}.mp3")  # Save the audio as MP3
            print(f"Audio clip {index} saved.")

        return self  # Return self for further chaining if needed
        

    def make_video(self):
        # Ensure title is included and sorted properly
        audio_files = sorted(os.listdir(self.audio_clips_dir), key=lambda x: (x != "title.mp3", int(x.split(".")[0]) if x != "title.mp3" else -1))
        image_files = sorted(os.listdir(self.image_dir), key=lambda x: (x != "title.png", int(x.split(".")[0]) if x != "title.png" else -1))

        print("Sorted audio files:", audio_files)
        print("Sorted image files:", image_files)

        # Initialize audio clips
        audio_clips = [AudioFileClip(os.path.join(self.audio_clips_dir, audio)) for audio in audio_files]

        # Initialize image clips with matching durations
        image_clips = [ImageClip(os.path.join(self.image_dir, image)).set_duration(audio.duration) 
                    for image, audio in zip(image_files, audio_clips)]

        # Attach audio to images
        image_clips_with_audio = [image.set_audio(audio) for image, audio in zip(image_clips, audio_clips)]

        # Concatenate all video clips
        video_clip = concatenate_videoclips(image_clips_with_audio, method="compose")

        # Save the final video
        video_clip.write_videofile(
            os.path.join(self.generated_video_dir, 'final_video.mp4'), 
            codec='libx264', 
            fps=24
        )

        self.remove_directory(self.image_dir)
        self.remove_directory(self.audio_clips_dir)


        existing_videos = sorted(
            [os.path.join(self.media_dir, d) for d in os.listdir(self.media_dir) 
             if os.path.isdir(os.path.join(self.media_dir, d))],
            key=os.path.getctime  # Sort by creation time (oldest first)
        )

        if len(existing_videos) > 5:
            for old_video_dir in existing_videos[:-5]:  # Keep last 5, delete the rest
                if old_video_dir != self.generated_video_dir:  # Ensure we don't delete the current video
                    self.remove_directory(old_video_dir)

    @staticmethod
    def remove_directory(dir_path):
        """
        Remove the specified directory and all its contents.
        """
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            print(f"{dir_path} and its contents have been removed.")
        else:
            print(f"{dir_path} does not exist or is not a directory.")

            

    

if __name__ == '__main__':
    yt_short_generator = YoutubeShortGenerator()
    result = yt_short_generator.title_to_keywords("top 3 Marvel Superheroes").generate_images().overlay_text_to_images().generate_audio_clips().make_video()



