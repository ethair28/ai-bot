import json
import os
import sys

from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import system, tool_result, user  # We use system()/user() to build chat messages

from functions.tool_registry import TOOL_DEFINITIONS, TOOL_EXECUTORS

# Describe the coding agent role and remind the model about the available tools.
SYSTEM_PROMPT = """
You are Grok code, a careful coding agent operating inside this git repository.
- Always inspect existing files before making changes.
- Use the available tools (get_file_content, get_files_info, write_file, run_python_file) whenever they help you gather context or execute code.
- Keep answers focused, actionable, and grounded in the repository's actual state.
""".strip()


def _handle_tool_call(tool_call):
    """
    Execute a requested tool call and return a tuple of (result_text, log_summary).
    """
    tool_name = tool_call.function.name
    executor = TOOL_EXECUTORS.get(tool_name)
    if executor is None:
        return f'Error: Unknown tool "{tool_name}".', f'TOOL_CALL {tool_name} FAILED: unknown tool'

    arguments_raw = tool_call.function.arguments or "{}"
    try:
        arguments = json.loads(arguments_raw) if arguments_raw else {}
    except json.JSONDecodeError as exc:
        return (
            f'Error: Could not parse arguments for tool "{tool_name}": {exc}',
            f'TOOL_CALL {tool_name} FAILED: invalid arguments {arguments_raw!r}',
        )

    try:
        result = executor(arguments)
        summary = f"TOOL_CALL {tool_name} ARGS {arguments!r}"
        return result, summary
    except Exception as exc:
        return f'Error: Tool "{tool_name}" failed: {exc}', f"TOOL_CALL {tool_name} FAILED: {exc}"

# Load environment variables
load_dotenv()

# Retrieve the API Key from the environment variable (e.g., from your .env file)
api_key = os.environ.get("BOOT_DEV_GROK_API_KEY")

try:
    # --- Check for CLI argument before proceeding ---
    if len(sys.argv) < 2:
        # Print the usage message to stderr (good practice for CLI errors)
        sys.stderr.write("Error: Missing CLI argument.\n")
        # FIX: Ensure usage message includes the optional --verbose flag
        sys.stderr.write("Usage: python grok_code_agent.py \"Your prompt here\" [--verbose]\n")
        # Exit immediately with a non-zero status code (1) to indicate an error
        sys.exit(1)

    # --- Check for --verbose flag ---
    # The flag will be the third argument (index 2) if it exists.
    is_verbose = (len(sys.argv) == 3 and sys.argv[2] == "--verbose")

    # Store the argument for clarity, now that we know it exists
    user_query = sys.argv[1]

    # 1. Check for API key presence and initialize the Client
    if not api_key:
        # Keep this as a ValueError as it's a configuration error
        raise ValueError("Configuration Error: API Key not found. Please set BOOT_DEV_GROK_API_KEY in your .env file.")
        
    client = Client(
        api_key=api_key
    )

    # --- UPDATED FUNCTIONALITY ---
    # Create the list of messages (equivalent to the types.Content list)
    messages = [
        system(SYSTEM_PROMPT),
        user(user_query)
    ]

    # 2. Create a chat instance and pass the initial messages directly
    # This is the Grok SDK equivalent of passing 'contents=messages' to generate_content
    chat = client.chat.create(
        model="grok-code-fast-1",
        messages=messages,
        tools=TOOL_DEFINITIONS,
    )
    # The separate chat.append() step is now removed.
    
    tool_call_logs: list[str] = []
    # 4. Get the response, allowing for iterative tool usage.
    while True:
        response = chat.sample()

        if not response.tool_calls:
            break

        chat.append(response)
        for tool_call in response.tool_calls:
            tool_response_text, log_summary = _handle_tool_call(tool_call)
            tool_call_logs.append(log_summary)
            chat.append(tool_result(tool_response_text))
    
    # Extract token usage from the response metadata
    prompt_tokens = response.usage.prompt_tokens
    response_tokens = response.usage.completion_tokens
    
    # 5. Print the Grok response (Behavior controlled by is_verbose)
    if is_verbose:
        # Full verbose output
        print(f"User prompt: {user_query}")
        print("Grok Technical Response:")
        if tool_call_logs:
            print("Tool calls executed:")
            for entry in tool_call_logs:
                print(f"- {entry}")
        print(response.content)

        print("\n--- Verbose Response Object (Debugging Info) ---")
        # Print the entire response object for detailed inspection
        print(response)
        print("------------------------------------------------")

        print("\n--- Token Usage ---")
        # 6. Print the token counts in the requested format
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")
        print("-------------------")
    else:
        # Raw output only (non-verbose mode)
        if tool_call_logs:
            print("Tool calls executed:")
            for entry in tool_call_logs:
                print(f"- {entry}")
        print(response.content)

except ValueError as ve:
    # Handles the specific case where the key is missing
    print(f"Error: {ve}")
except Exception as e:
    # Catches general API or network errors
    print(f"An unexpected error occurred during API interaction: {e}")
