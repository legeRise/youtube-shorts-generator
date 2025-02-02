import streamlit as st
import os
import re
from youtube_short_generator import YoutubeShortGenerator

def main():
    st.markdown(
    "<h1 style='text-align: center;'>YT Shorts Generator</h1>",
    unsafe_allow_html=True
    )
    st.markdown("<p style='text-align: center;'>Leave a Like if it works for you! ❤️</p>", unsafe_allow_html=True)
    
    # User Input
    video_title = st.text_input("Enter Video Title:", "Top 3 Marvel Superheroes")
    
    if st.button("Generate Video"):
        if video_title.strip():
            # Validate that the title starts with "Top 3" or "Top 5" (case-insensitive)
            pattern = r"^top\s*(3|5)\b"
            if not re.match(pattern, video_title.strip(), re.IGNORECASE):
                st.warning("Please start the title with 'Top 3' or 'Top 5'.")
                return
            
            st.info("Starting video generation process...")
            
            try:
                # Initialize Generator
                yt_generator = YoutubeShortGenerator()
                
                with st.spinner("Analyzing title and extracting keywords..."):
                    yt_generator.title_to_keywords(video_title)
                    st.info("Keywords extracted successfully!")
                
                with st.spinner("Generating images..."):
                    yt_generator.generate_images()
                    st.info("Images generated successfully!")
                
                with st.spinner("Overlaying text on images..."):
                    yt_generator.overlay_text_to_images()
                    st.info("Text overlay completed!")
                
                with st.spinner("Generating audio clips..."):
                    yt_generator.generate_audio_clips()
                    st.info("Audio clips generated successfully!")
                
                with st.spinner("Combining images and audio into video..."):
                    yt_generator.make_video()
                    st.info("Video is being finalized!")
                
                # Get the generated video path
                video_path = os.path.join(yt_generator.generated_video_dir, 'final_video.mp4')
                
                if os.path.exists(video_path):
                    st.success("Video generated successfully!")
                    
                    # Provide a download link
                    with open(video_path, "rb") as file:
                        st.download_button(
                            label="Download Video",
                            data=file,
                            file_name="youtube_short.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Error: Video file not found.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a valid title.")

if __name__ == "__main__":
    main()
