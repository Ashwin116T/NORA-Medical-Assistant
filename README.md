# N.O.R.A.- AI-Powered Medical Information Assistant with Multimodal Input Support
This is a locally hosted, multimodal medical assistant chatbot designed for hospitals and healthcare environments.

## System Requirements
- OS: Ubuntu 22.04 or similar Linux distribution
- RAM: 16 GB minimum
- GPU: NVIDIA RTX 4050 Ti (6 GB VRAM) or higher recommended
- Python: 3.10+

## Installation Instructions

###  Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> Note: You may need to install system packages like `ffmpeg`, `librosa`, or others used in audio/image processing.

### Configure `config.yaml`
Modify the `config.yaml` file to match your local model setup. Example:
```yaml
ollama:
  model_name: "llama3:latest"
  base_url: "http://localhost:11434"
```

Ensure Ollama is installed and the model is pulled:
```bash
ollama run llama3
```

### LLaVA Model Setup (for Image + Text Input)
To enable image-based multimodal functionality:

1. Download a compatible `.gguf` model file from Hugging Face, such as:  
   https://huggingface.co/llava-hf/llava-llama-2-7b-chat-gguf

2. Create a folder inside your project:
```bash
mkdir -p models/lava
```

3. Move the downloaded `.gguf` file into the folder and rename:
```bash
mv <downloaded_model>.gguf models/lava/ggml-model-q5_k.gguf
```

> Note: If you use a different filename or location, update `image_handler.py` accordingly.

### Run the Application
```bash
streamlit run app.py
```

The app will launch on `http://localhost:8501`.

## Project Structure Overview

- `app.py`: Main Streamlit app frontend
- `llm_chains.py`: Chains logic using LangChain (chat + RAG support)
- `audio_handler.py`: Converts audio to text using Whisper
- `image_handler.py`: Handles image input and generates descriptions
- `pdf_handler.py`: Parses and chunks PDF content for embedding
- `utils.py`: Timestamp and chat history utilities
- `config.yaml`: Configuration settings
- `prompt_templates.py`: System-level prompt format for N.O.R.A.


## Notes
- This version is a prototype and was run on a personal machine.
- All models and vector stores are hosted locally (no cloud usage).
