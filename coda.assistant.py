import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv  # Used to load environment variables from .env file
from rich.console import Console  # For rich text output (colors, formatting)
from rich.markdown import Markdown  # To render Markdown from the AI
import textwrap  # To format the system prompt nicely
from typing import Optional, Dict, Any, List # For type hinting

# --- Constants & Configuration ---

# Load environment variables from .env file if it exists
load_dotenv()

# --- Core Configuration ---
# Allow overriding the model via environment variable, default to gemini-1.5-pro-latest
DEFAULT_MODEL_NAME = "gemini-1.5-pro-latest"
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", DEFAULT_MODEL_NAME)

# --- Generation Configuration ---
# Allow overriding key generation parameters via environment variables
# Provide sensible defaults if environment variables are not set or invalid
try:
    TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", 0.7))
except ValueError:
    TEMPERATURE = 0.7

try:
    # Use None for top_p/top_k if not specified or invalid, letting the API use its default
    TOP_P_ENV = os.getenv("GEMINI_TOP_P")
    TOP_P = float(TOP_P_ENV) if TOP_P_ENV else None
except ValueError:
    TOP_P = None

try:
    TOP_K_ENV = os.getenv("GEMINI_TOP_K")
    TOP_K = int(TOP_K_ENV) if TOP_K_ENV else None
except ValueError:
    TOP_K = None

try:
    MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", 8192))
except ValueError:
    MAX_OUTPUT_TOKENS = 8192

GENERATION_CONFIG = {
    "temperature": TEMPERATURE,
    "top_p": TOP_P,
    "top_k": TOP_K,
    "max_output_tokens": MAX_OUTPUT_TOKENS,
    "response_mime_type": "text/plain", # Ensures plain text for easier history handling
}
# Filter out None values from GENERATION_CONFIG as the API expects numbers or omitted keys
GENERATION_CONFIG = {k: v for k, v in GENERATION_CONFIG.items() if v is not None}


# --- Safety Settings ---
# These can also be made configurable via environment variables if needed
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# --- System Prompt ---
# Define the AI's role, personality, and instructions
SYSTEM_PROMPT = textwrap.dedent("""
You are Coda, an advanced AI Code Assistant powered by Google's Gemini model.
Your purpose is to help users with their programming tasks. Be highly knowledgeable, accurate, and helpful.

Instructions:
1.  **Understand the Goal:** Carefully analyze the user's request, code snippets, and questions. Ask clarifying questions if the request is ambiguous.
2.  **Provide Explanations:** Don't just give code. Explain *why* the code works, the logic behind it, and potential alternatives or trade-offs.
3.  **Format Code Clearly:** Use Markdown code blocks with appropriate language identifiers (e.g., ```python ... ```) for all code snippets.
4.  **Be Language Agnostic (but prioritize Python if unspecified):** Assist with various programming languages, but assume Python if not specified.
5.  **Debug Assistance:** Help users debug their code. Ask for the code, the error message, and what they expect to happen.
6.  **Best Practices:** Suggest improvements regarding code style, efficiency, security, and maintainability where appropriate.
7.  **Stay On Topic:** Focus on programming, software development, algorithms, data structures, and related technical topics. Politely decline unrelated requests.
8.  **Maintain Context:** Remember previous parts of the conversation to provide relevant follow-up assistance (handled by the chat object).
9.  **Be Concise but Thorough:** Provide enough detail to be helpful without being excessively verbose.
10. **Safety First:** Adhere strictly to safety guidelines. Do not generate harmful, unethical, or inappropriate content.
""")

# --- Initialization ---
console = Console() # Create a console object for rich output

def configure_api() -> None:
    """
    Loads the Google API key from environment variables or .env file
    and configures the genai library. Exits if the key is not found.
    """
    api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        console.print("[bold red]Error: GOOGLE_API_KEY not found.[/]")
        console.print(
            "Please set the GOOGLE_API_KEY environment variable or "
            "create a .env file with the key."
        )
        sys.exit(1) # Exit if key is not found

    try:
        genai.configure(api_key=api_key)
        console.print("[green]API Key configured successfully.[/]")
    except Exception as e:
        console.print(f"[bold red]Error configuring Generative AI SDK: {e}[/]")
        sys.exit(1)

def initialize_model() -> genai.ChatSession:
    """
    Initializes the Generative Model with configured settings and starts a chat session.
    Exits if initialization fails.

    Returns:
        genai.ChatSession: The initialized chat session object.
    """
    console.print(f"[cyan]Initializing model: {MODEL_NAME}...[/]")
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            safety_settings=SAFETY_SETTINGS,
            generation_config=GENERATION_CONFIG,
            system_instruction=SYSTEM_PROMPT
        )
        # Start chat with empty history
        chat = model.start_chat(history=[])
        console.print("[green]Model initialized and chat session started.[/]")
        return chat
    except Exception as e:
        console.print(f"[bold red]Error initializing model '{MODEL_NAME}': {e}[/]")
        console.print("[yellow]Possible reasons: Invalid model name, API key issue, network problem.[/]")
        sys.exit(1)

def get_multiline_input() -> str:
    """
    Prompts the user for potentially multi-line input.
    Input ends when the user enters 'EOF' or 'eof' on a new line.

    Returns:
        str: The complete user input.
    """
    lines: List[str] = []
    console.print("[bold yellow]You (end input with 'EOF' on a new line):[/]")
    while True:
        try:
            line = input("> ")
            if line.strip().upper() == "EOF":
                break
            lines.append(line)
        except EOFError: # Handle Ctrl+D
            break
    return "\n".join(lines)

# --- Main Interaction Loop ---
def run_assistant(chat: genai.ChatSession) -> None:
    """
    Handles the main interaction loop with the user.

    Args:
        chat (genai.ChatSession): The active chat session with the model.
    """
    console.print("\n[bold cyan]Welcome to Coda - Your AI Code Assistant![/]")
    console.print(f"Model: [bold]{MODEL_NAME}[/]")
    console.print(f"Config: [dim]{GENERATION_CONFIG}[/dim]")
    console.print("Type 'quit' or 'exit' to end the session.")
    console.print("-" * 50)

    while True:
        try:
            # Get user input (potentially multi-line)
            user_input = get_multiline_input()

            # Check for exit commands after getting input
            if user_input.strip().lower() in ["quit", "exit"]:
                console.print("[bold cyan]\nAssistant shutting down. Goodbye![/]")
                break

            # Skip empty input after stripping whitespace
            if not user_input.strip():
                continue

            # Send message to the model (streaming)
            console.print("\n[bold blue]Coda:[/]")
            full_response = ""
            try:
                # Use stream=True for interactive feedback
                response_stream = chat.send_message(user_input, stream=True)

                # Display a thinking status while waiting for the first chunk
                with console.status("[cyan]Thinking...", spinner="dots"):
                    for chunk in response_stream:
                        # Basic check for blocked content based on safety
                        # More robust check would inspect chunk.prompt_feedback potentially
                        if not chunk.parts:
                             console.print("[bold yellow]Warning: Received empty chunk, potentially due to safety filters or stop reason.[/]")
                             # You could add logic here to check chat.history[-1].finish_reason if needed
                             continue

                        if chunk.text:
                            # Print text directly for immediate feedback.
                            # Note: Markdown rendering during streaming can be tricky
                            # if formatting spans multiple chunks (like code blocks).
                            # Printing raw text is often the most reliable for CLIs.
                            print(chunk.text, end="", flush=True)
                            full_response += chunk.text

                print() # Add a newline after the stream finishes

                # Optional: Render the *complete* response as Markdown *after* streaming.
                # This ensures proper block formatting but loses the streaming "feel".
                # Uncomment the lines below if you prefer this approach:
                # console.print("\n--- Rendered Markdown ---")
                # console.print(Markdown(full_response))
                # console.print("--- End Rendered Markdown ---")


            # Handle specific API errors during generation/streaming
            except genai.types.StopCandidateException as e:
                 console.print(f"\n[bold yellow]Warning:[/bold yellow] Response stopped: {e}")
                 console.print("[dim]This might be due to safety settings, length limits, or stop sequences.[/dim]")
            except genai.types.BlockedPromptException as e:
                 console.print(f"\n[bold red]Error:[/bold red] Your prompt was blocked by safety settings: {e}")
                 # You might want to inspect chat.history for debugging
                 # if chat.history:
                 #     console.print("[dim]Last user message:", chat.history[-2].parts[0].text, "[/dim]")
            except google.api_core.exceptions.GoogleAPIError as e:
                console.print(f"\n[bold red]API Error occurred: {e}[/]")
                console.print("[yellow]There might be an issue with the connection or the Google Cloud service.[/yellow]")
                # Depending on the error, you might want to break or retry
            except Exception as e:
                console.print(f"\n[bold red]An error occurred while getting the response: {type(e).__name__}: {e}[/]")
                # Add more specific error handling if needed

        # Handle interruption (Ctrl+C)
        except KeyboardInterrupt:
            console.print("\n[bold cyan]\nAssistant shutting down (Interrupted). Goodbye![/]")
            break
        # Catch any other unexpected errors in the loop
        except Exception as e:
            console.print(f"\n[bold red]An unexpected error occurred in the main loop: {type(e).__name__}: {e}[/]")
            break # Exit on unknown errors to prevent unexpected states

# --- Entry Point ---
def main() -> None:
    """Main function to set up and run the assistant."""
    configure_api()
    chat_session = initialize_model()
    run_assistant(chat_session)

if __name__ == "__main__":
    main()