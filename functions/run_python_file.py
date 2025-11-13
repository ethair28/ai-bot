import os
import subprocess


def run_python_file(working_directory, file_path, args=None):
    """
    Execute a Python file within a restricted working directory.

    Args:
        working_directory (str): Base directory that bounds execution.
        file_path (str): Relative or absolute path to the Python file.
        args (list, optional): Additional CLI args passed to the script.

    Returns:
        str: Formatted stdout/stderr output or an error description.
    """
    args = args or []

    try:
        intended_full_path = os.path.join(working_directory, file_path)
        abs_working_dir = os.path.realpath(working_directory)
        abs_file_path = os.path.realpath(intended_full_path)

        if os.path.commonpath([abs_working_dir, abs_file_path]) != abs_working_dir:
            return (
                f'Error: Cannot execute "{file_path}" as it is outside the permitted '
                "working directory"
            )

        if not os.path.isfile(abs_file_path):
            return f'Error: File "{file_path}" not found.'

        if not abs_file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        command = ["python", abs_file_path, *args]
        completed_process = subprocess.run(
            command,
            cwd=abs_working_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = completed_process.stdout.strip()
        stderr = completed_process.stderr.strip()

        if not stdout and not stderr:
            return "No output produced."

        output_lines = [
            f"STDOUT: {stdout}" if stdout else "STDOUT:",
            f"STDERR: {stderr}" if stderr else "STDERR:",
        ]

        if completed_process.returncode != 0:
            output_lines.append(f"Process exited with code {completed_process.returncode}")

        return "\n".join(output_lines)

    except Exception as e:
        return f"Error: executing Python file: {e}"
