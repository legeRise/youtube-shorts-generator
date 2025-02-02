import os
from dotenv import load_dotenv

load_dotenv()

# API keys need to be configured in .env
llm_api_keys = {
        "openai": os.getenv('OPENAI_API_KEY'),
        "groq": os.getenv('GROQ_API_KEY'),
        "anthropic": os.getenv('ANTHROPIC_API_KEY')
    }

# optionally change providers
CHOSEN_LLM_PROVIDER = os.getenv('CHOSEN_LLM_PROVIDER','groq')  
CHOSEN_EMBEDDING_PROVIDER = os.getenv('CHOSEN_EMBEDDING_PROVIDER','ollama')  


FONT_BASE_DIR = 'fonts'
HF_TOKEN = os.getenv("HF_TOKEN", None)
IMAGE_GENERATION_SPACE_NAME="habib926653/stabilityai-stable-diffusion-3.5-large-turbo"


# LLM Models dictionary
selected_llm_model = {
        "openai": os.getenv('GPT_MODEL','gpt-4o-mini'),
        "groq": os.getenv('GROQ_MODEL','llama-3.3-70b-versatile'),
        "anthropic": os.getenv('ANTHROPIC_MODEL','claude-3-5-sonnet-latest'),
        "ollama": os.getenv('OLLAMA_MODEL','llama3.1')

    }


# Embedding Model Models dictionary
selected_embedding_model = {
        "openai": os.getenv('GPT_EMBEDDING_MODEL'),
        "groq": os.getenv('GROQ_EMBEDDING_MODEL'),
        "anthropic": os.getenv('ANTHROPIC_EMBEDDING_MODEL'),
        "ollama": os.getenv('OLLAMA_EMBEDDING_MODEL')

    }