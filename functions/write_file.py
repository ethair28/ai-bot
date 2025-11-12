import os

def write_file(working_directory, file_path, content):
    """
    Writes content to a specific file, enforcing security checks.
    Creates the file if it does not exist, and overwrites existing content.

    Args:
        working_directory (str): The permitted root directory for file access.
        file_path (str): The relative or absolute path to the file to write.
        content (str): The string content to write to the file.

    Returns:
        str: A success message, or an error message if writing fails.
    """
    try:
        # 1. Combine working_directory and file_path to get the intended full path
        intended_full_path = os.path.join(working_directory, file_path)

        # 2. Normalize paths to handle relative paths and symlinks securely
        abs_working_dir = os.path.realpath(working_directory)
        abs_file_path = os.path.realpath(intended_full_path) 

        # 3. Security Check: Ensure file_path is within working_directory
        # If the file path is outside the working directory, the common path will be shorter.
        if not os.path.commonpath([abs_working_dir, abs_file_path]) == abs_working_dir:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # 4. Write the file content (using 'w' to overwrite/create, and 'utf-8')
        with open(abs_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 5. Success message
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        # 6. Catch any other errors (e.g., permission issues, directory creation issues)
        return f"Error: {e.__class__.__name__}: {e}"