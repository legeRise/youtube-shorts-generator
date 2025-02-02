import pollinations
import constants
from PIL import Image
from gradio_client import Client


class ImageGenerator:
    def __init__(self, model=pollinations.Image.flux(), seed="random", width=720, height=1280, enhance=False, nologo=True, private=True, safe=False, referrer="pollinations.py"):
        # Initialize the image model with provided parameters
        self.image_model = pollinations.Image(
            model=model,
            seed=seed,
            width=width,
            height=height,
            enhance=False,
            nologo=nologo,
            private=private,
            safe=safe,
            referrer=referrer
        )
    
    def generate_image_with_pollinations_ai(self, prompt):
        # Generate image using the provided prompt
        try:
            image = self.image_model(prompt=prompt)
            return image  # Return the generated image object
        except Exception as e:
            print(f"Error generating image: {e}")
            return None  # Return None if there's an error
        

    def generate_image(self, prompt, path='test_image.png'):
        try:
            # Initialize the Gradio Client with Hugging Face token
            client = Client(constants.IMAGE_GENERATION_SPACE_NAME, hf_token=constants.HF_TOKEN)

            # Make the API request
            result = client.predict(
                param_0=prompt,  # Text prompt for image generation
                api_name="/predict"
            )

            image = Image.open(result)
            image.save(path)

            # Return the result (which includes the URL or file path)
            return result

        except Exception as e:
            print(f"Error during image generation: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == '__main__':
    image_generator = ImageGenerator()  # You can pass custom params here if needed
    result = image_generator.generate_image("A cat with flowers around it.",path='wow9.png')
    
    print(result)
