# FloCap
FloCap is an OpenAI compatible API that utilizes the Florence-2 large language model for image captioning. This application provides an API endpoint that accepts image inputs and returns detailed captions or analyses based on the Florence-2 model's capabilities.

FloCap was primarily created for use with SillyTavern but should worl with any frontend/client capable of sending images to an OpenAI compatible API.

## The Florence-2 Model
Florence-2 is an advanced vision foundation model, from Microsoft, that uses a prompt-based approach to handle a wide range of vision and vision-language tasks. Florence-2 can interpret simple text prompts to perform tasks like captioning, object detection, and segmentation. It leverages our FLD-5B dataset, containing 5.4 billion annotations across 126 million images, to master multi-task learning. The model's sequence-to-sequence architecture enables it to excel in both zero-shot and fine-tuned settings, proving to be a competitive vision foundation model.

### Model usage notes
FloCap is currently only using the MORE_DETAILED_CAPTION mode of the model and does not require or use any prompt.

## Installation

### Windows

1. Ensure you have Python 3.10 or later installed on your system.

2. Clone this repository:
   ```
   git clone https://github.com/your-username/florence2-api-app.git
   cd florence2-api-app
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Set up the CUDA-enabled PyTorch (if you have an NVIDIA GPU):
   ```
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
   Note: Replace `cu118` with your CUDA version if different.

6. Run the application:
   ```
   python FlorenceAPI.py
   ```

### Linux/WSL

1. Ensure you have Python 3.10 or later installed on your system.

2. Clone this repository:
   ```
   git clone https://github.com/your-username/florence2-api-app.git
   cd florence2-api-app
   ```

3. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Set up the CUDA-enabled PyTorch (if you have an NVIDIA GPU):
   ```
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
   Note: Replace `cu118` with your CUDA version if different.

6. Run the application:
   ```
   python FlorenceAPI.py
   ```

### Docker

Docker installation instructions are coming soon. This section will be updated when Docker support is implemented.

## Usage

After starting the application, you can send POST requests to `http://localhost:5000/chat/completions` with JSON payloads containing image data and prompts. The API will respond with captions or analyses generated by the Florence-2 model.

Detailed API documentation and example requests will be provided in a separate document.

## Contributing

Contributions to the Florence 2 API App are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

[Specify your license here]