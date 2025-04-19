from llama_cpp import Llama
import base64
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable for LLM instance
_llm_instance = None

def initialize_model():
    """Initialize the LLM model once"""
    global _llm_instance
    
    if _llm_instance is None:
        try:
            model_path = "models/lava/ggml-model-q5_k.gguf"
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model not found at {model_path}")
            
            logger.info("Initializing LLaVA model...")
            _llm_instance = Llama(
                model_path=model_path,
                logits_all=True,
                n_ctx=2048,  # Increased context window
                n_threads=4,  # Use multiple threads
                verbose=False
            )
            logger.info("Model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise

def convert_bytes_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 encoded data URL"""
    try:
        encoded_string = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        logger.error(f"Failed to convert image to base64: {str(e)}")
        raise

def handle_image(image_bytes: bytes, user_message: str) -> str:
    """
    Process an image and generate a description based on user message
    """
    try:
        # Initialize model if not already done
        initialize_model()
        
        # Convert image to base64
        image_base64 = convert_bytes_to_base64(image_bytes)
        
        # Create the chat completion with proper message format
        messages = [
            {
                "role": "system",
                "content": "You are an assistant who provides detailed and accurate image descriptions."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": image_base64}}
                ]
            }
        ]
        
        logger.debug("Sending request to model...")
        output = _llm_instance.create_chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=512
        )
        
        logger.info("Image processing completed successfully")
        return output["choices"][0]["message"]["content"]
        
    except Exception as e:
        logger.error(f"Error in handle_image: {str(e)}")
        return f"Error processing image: {str(e)}"

def convert_image_to_base64(image_path: str) -> str:
    """Convert an image file to base64 encoded data URL"""
    try:
        with open(image_path, "rb") as image_file:
            return convert_bytes_to_base64(image_file.read())
    except Exception as e:
        logger.error(f"Failed to convert image file to base64: {str(e)}")
        raise

if __name__ == "__main__":
    # Test the handler
    try:
        image_path = "test_image.jpg"
        test_bytes = open(image_path, "rb").read()
        result = handle_image(test_bytes, "Describe this image in detail")
        print("\nGenerated description:")
        print(result)
    except Exception as e:
        print(f"Error in main execution: {str(e)}")