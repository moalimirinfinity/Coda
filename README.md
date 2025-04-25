# Coda - AI Code Assistant

Coda is a command-line AI code assistant powered by Google's Gemini models (defaults to `gemini-1.5-pro-latest`). It provides an interactive chat interface to help you with programming questions, code generation, debugging, explanations, and more.

## Features

* **Interactive Chat:** Converse with the AI, ask follow-up questions, and maintain context throughout the session.
* **Powered by Gemini:** Leverages Google's advanced AI models (configurable, defaults to `gemini-1.5-pro-latest`).
* **Rich Terminal Output:** Uses the `rich` library for colored and formatted text/code in your terminal for better readability.
* **Environment Variable Configuration:** Easily configure the model name, temperature, token limits, and other generation parameters via environment variables or a `.env` file.
* **Multi-line Input Support:** Paste or type multi-line code snippets or questions easily by signaling the end of your input.
* **Customizable System Prompt:** The AI's persona ("Coda") and instructions are defined in the script but can be modified if needed.
* **Secure API Key Handling:** Uses python-dotenv for easy and secure management of your Google API key via a `.env` file or environment variables.
* **Streaming Responses:** See the AI's response appear token by token for a more interactive feel.

## Prerequisites

* Python 3.8 or higher (recommended for type hinting support)
* `pip` (Python package installer)

## Setup

1.  **Clone the repository (or download the script):**
    ```bash
    # If you have a git repository
    git clone <your-repo-url>
    cd <your-repo-directory>
    # Or just save the Python script (e.g., coda_assistant.py) in a directory
    ```

2.  **Install dependencies:**
    Navigate to the script's directory in your terminal and run:
    ```bash
    pip install google-generativeai python-dotenv rich
    ```

3.  **Set up Google API Key:**
    You need a Google AI API key to use this script.
    * Obtain your key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    * **Recommended Method:** Create a file named `.env` in the *same directory* as the script. Add your API key to this file:
        ```dotenv
        # .env file content
        GOOGLE_API_KEY='YOUR_API_KEY_HERE'
        ```
    * **Alternative Method:** Set the `GOOGLE_API_KEY` environment variable directly in your operating system.

## Usage

1.  **Navigate to the script's directory** in your terminal.
2.  **Run the assistant:**
    ```bash
    python coda_assistant.py
    ```
3.  **Interact with Coda:**
    * You will be greeted by Coda and see the model and configuration being used.
    * At the `You (end input with 'EOF' on a new line):` prompt, type your question or paste your code.
    * **For multi-line input:** Simply press Enter to go to the next line. When you are finished with your input, type `EOF` (case-insensitive) on a new line by itself and press Enter.
    * Coda will process your input and stream its response.
    * Type `quit` or `exit` (and press Enter) to end the session. You can also use `Ctrl+C`.

## Configuration (via Environment Variables / .env file)

The assistant's behavior can be customized using environment variables. You can set these in your system or add them to the `.env` file alongside your `GOOGLE_API_KEY`.

* **`GOOGLE_API_KEY`** (Required): Your API key for Google AI Studio.
* **`GEMINI_MODEL_NAME`**: The specific Gemini model to use.
    * Default: `gemini-1.5-pro-latest`
    * Example: `gemini-1.5-flash-latest`
* **`GEMINI_TEMPERATURE`**: Controls randomness. Lower values (e.g., `0.2`) are more deterministic, higher values (e.g., `0.9`) are more creative.
    * Default: `0.7`
    * Example: `0.5`
* **`GEMINI_MAX_TOKENS`**: The maximum number of tokens to generate in the response.
    * Default: `8192`
    * Example: `4096`
* **`GEMINI_TOP_P`**: Nucleus sampling parameter. If set, the model considers only tokens with cumulative probability mass up to this value. (Use values between 0.0 and 1.0). *Omit or leave blank to use API default.*
    * Default: (API default)
    * Example: `0.95`
* **`GEMINI_TOP_K`**: Top-k sampling parameter. If set, the model considers only the `k` most likely tokens at each step. *Omit or leave blank to use API default.*
    * Default: (API default)
    * Example: `40`

**Example `.env` file with custom configuration:**

```dotenv
GOOGLE_API_KEY='YOUR_API_KEY_HERE'
GEMINI_MODEL_NAME='gemini-1.5-flash-latest'
GEMINI_TEMPERATURE='0.6'
GEMINI_MAX_TOKENS='4000'
GEMINI_TOP_P='0.9'