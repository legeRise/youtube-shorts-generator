import constants
from PIL import Image
from gradio_client import Client


class ImageGenerator:     

    def generate_image(self, prompt, path='test_image.png'):
        try:
            # Initialize the Gradio Client with Hugging Face token
            client = Client(constants.IMAGE_GENERATION_SPACE_NAME, hf_token=constants.HF_TOKEN)

            # Make the API request
            result = client.predict(
    		prompt="Hello!!",
    		width=720,
    		height=1280,
    		api_name="/generate_image")

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
