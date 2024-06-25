import sys
import os
import torch
from flask import Flask, request, jsonify
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import io
import logging
import base64
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
from transformers.utils import TRANSFORMERS_CACHE
print(TRANSFORMERS_CACHE)

print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Working directory:", os.getcwd())
print("PYTHONPATH:", os.environ.get('PYTHONPATH', 'Not set'))

print("PyTorch version:", torch.__version__)
print("PyTorch installation location:", torch.__file__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda if torch.cuda.is_available() else "N/A")
if torch.cuda.is_available():
    print("CUDA device count:", torch.cuda.device_count())
    print("CUDA device name:", torch.cuda.get_device_name(0))


def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    if not str(filename).endswith("modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    imports.remove("flash_attn")
    return imports

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Enhanced GPU detection and information
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda if torch.cuda.is_available() else "N/A")
if torch.cuda.is_available():
    print("CUDA device count:", torch.cuda.device_count())
    print("CUDA device name:", torch.cuda.get_device_name(0))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load the model and processor
model_id = 'microsoft/Florence-2-large'
with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
    model = AutoModelForCausalLM.from_pretrained(model_id, attn_implementation="sdpa", trust_remote_code=True)
    model = model.to(device)
model.eval()  # Set the model to evaluation mode
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

print(f"Model device: {next(model.parameters()).device}")

def generate_caption(image):
    task_prompt = '<MORE_DETAILED_CAPTION>'
    inputs = processor(text=task_prompt, images=image, return_tensors="pt")
    # Move inputs to the same device as the model
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            early_stopping=False,
            do_sample=False,
            num_beams=3,
        )
    
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    parsed_answer = processor.post_process_generation(
        generated_text, 
        task=task_prompt, 
        image_size=(image.width, image.height)
    )
    
    return parsed_answer

@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    app.logger.info(f"Received request: {request.method} {request.url}")
    app.logger.debug(f"Request headers: {request.headers}")

    data = request.json
    app.logger.debug(f"Request data: {data}")

    if 'messages' not in data or not isinstance(data['messages'], list):
        app.logger.error("Invalid request format: 'messages' field is missing or not a list")
        return jsonify({"error": "Invalid request format"}), 400

    image = None
    user_prompt = "What's in this image?"

    for message in data['messages']:
        if message['role'] == 'user':
            for content in message['content']:
                if content['type'] == 'text':
                    user_prompt = content['text']
                elif content['type'] == 'image_url':
                    image_data = content['image_url']['url']
                    if image_data.startswith('data:image'):
                        try:
                            image_data = image_data.split(',')[1]
                            image_bytes = base64.b64decode(image_data)
                            image = Image.open(io.BytesIO(image_bytes))
                        except Exception as e:
                            app.logger.error(f"Error decoding base64 image: {str(e)}")
                            return jsonify({"error": f"Error processing image: {str(e)}"}), 400

    if image is None:
        app.logger.error("No valid image found in request")
        return jsonify({"error": "No valid image found in request"}), 400

    try:
        caption_result = generate_caption(image)
        app.logger.debug(f"Caption result: {caption_result}")
        app.logger.debug(f"type: {type(caption_result)}")
        if isinstance(caption_result, dict):
            caption = caption_result.get('<MORE_DETAILED_CAPTION>', 'No caption generated')
        else:
            caption = str(caption_result)
        
        # Combine the user's prompt with the generated caption
        full_response = f"User asked: {user_prompt}\n\nImage description: {caption}"
    except Exception as e:
        app.logger.error(f"Error generating caption: {str(e)}")
        return jsonify({"error": f"Error generating caption: {str(e)}"}), 500
    
    response = {
        "id": "chatcmpl-florence2",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "florence-2-large-caption",
        "usage": {
            "prompt_tokens": len(user_prompt.split()),
            "completion_tokens": len(caption.split()),
            "total_tokens": len(user_prompt.split()) + len(caption.split())
        },
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": full_response
                },
                "finish_reason": "stop",
                "index": 0
            }
        ]
    }
    
    app.logger.info("Successfully generated caption")
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)