import torch
from transformers import pipeline
import librosa
import io
import numpy as np
import logging

logger = logging.getLogger(__name__)

def transcribe_audio(audio_bytes):
    """Robust audio transcription with error handling"""
    try:
        # Convert bytes to numpy array using librosa
        audio_stream = io.BytesIO(audio_bytes)
        audio, sr = librosa.load(
            audio_stream,
            sr=16000,  # Force 16kHz sample rate
            mono=True,  # Convert to mono
            res_type="kaiser_fast"
        )
        
        # Initialize Whisper pipeline
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = pipeline(
            task="automatic-speech-recognition",
            model="openai/whisper-tiny",  # Use smaller model
            device=device,
            chunk_length_s=10,
            stride_length_s=4
        )

        # Run transcription
        result = pipe(audio.copy(), batch_size=1)
        return result["text"].strip()

    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        return "[AUDIO TRANSCRIPTION ERROR]"