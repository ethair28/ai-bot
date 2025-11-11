import os
# FIX: Use relative import (from .config) since config.py is a sibling file 
# inside the 'functions' package.
from .config import MAX_READ_LENGTH

# Use the imported constant
MAX_FILE_CHARS = MAX_READ_LENGTH

def get_file_content(working_directory, file_path):
    """
    Reads the content of a specific file, enforcing security checks and truncation.

    Args:
        working_directory (str): The permitted root directory for file access.
        file_path (str): The relative or absolute path to the file to read.

    Returns:
        str: The content of the file, or an error message if reading fails.
    """
    try:
        # 1. Combine working_directory and file_path to get the intended full path
        # This ensures 'lorem.txt' is correctly found inside the 'calculator' directory.
        intended_full_path = os.path.join(working_directory, file_path)

        # 2. Normalize paths to handle relative paths and symlinks securely
        # realpath resolves symbolic links and normalizes the path.
        abs_working_dir = os.path.realpath(working_directory)
        # Use the combined path for the absolute file path resolution
        abs_file_path = os.path.realpath(intended_full_path) 

        # 3. Security Check: Ensure file_path is within working_directory
        # If the file path is outside the working directory, the common path will be shorter.
        if not os.path.commonpath([abs_working_dir, abs_file_path]) == abs_working_dir:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # 4. Check if it is a regular file
        if not os.path.isfile(abs_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # 5. Read the file content
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 6. Truncation check
        if len(content) > MAX_FILE_CHARS:
            truncated_content = content[:MAX_FILE_CHARS]
            message = f'[...File "{file_path}" truncated at {MAX_FILE_CHARS} characters]'
            return truncated_content + message
        
        return content

    except Exception as e:
        # 7. Catch any other errors (e.g., permission issues, encoding errors)
        return f"Error: {e.__class__.__name__}: {e}"