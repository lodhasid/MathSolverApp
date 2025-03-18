# Math Problem Solver

This application helps solve math problems using image recognition and OpenAI's GPT-4 Vision API. Simply upload a picture of your math problem, and the app will provide a detailed solution with step-by-step explanations.

## Setup Instructions

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the app in your web browser (it should open automatically when you run the command above)
2. Click on "Choose an image of your math problem" to upload your image
3. Once your image is uploaded, click "Solve Problem"
4. Wait for the solution to be generated
5. Review the detailed solution and explanation

## Requirements

- Python 3.7+
- OpenAI API key with access to GPT-4 Vision API
- Supported image formats: PNG, JPG, JPEG

## Note

Make sure your image is clear and the math problem is easily readable for the best results. 