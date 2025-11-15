import os
from typing import Any, Callable, Dict, List

from xai_sdk.chat import tool

from .get_file_content import get_file_content
from .get_files_info import get_files_info
from .run_python_file import run_python_file
from .write_file import write_file

REPO_ROOT = os.path.realpath(os.getcwd())
ToolExecutor = Callable[[Dict[str, Any]], str]


def _resolve_working_directory(raw_directory: str | None) -> str:
    """
    Normalize the requested working directory so it stays inside the repository.
    """
    directory = raw_directory or "."
    candidate = os.path.realpath(directory if os.path.isabs(directory) else os.path.join(REPO_ROOT, directory))

    if os.path.commonpath([REPO_ROOT, candidate]) != REPO_ROOT:
        raise ValueError("working_directory must remain inside the repository root.")

    return candidate


def _execute_get_file_content(args: Dict[str, Any]) -> str:
    file_path = args.get("file_path")
    if not file_path:
        return 'Error: "file_path" is required.'

    try:
        working_directory = _resolve_working_directory(args.get("working_directory"))
    except ValueError as exc:
        return f"Error: {exc}"

    return get_file_content(working_directory, file_path)


def _execute_get_files_info(args: Dict[str, Any]) -> str:
    try:
        working_directory = _resolve_working_directory(args.get("working_directory"))
    except ValueError as exc:
        return f"Error: {exc}"

    directory = args.get("directory", ".")
    return get_files_info(working_directory, directory)


def _execute_write_file(args: Dict[str, Any]) -> str:
    file_path = args.get("file_path")
    content = args.get("content")
    if not file_path or content is None:
        return 'Error: Both "file_path" and "content" are required.'

    try:
        working_directory = _resolve_working_directory(args.get("working_directory"))
    except ValueError as exc:
        return f"Error: {exc}"

    return write_file(working_directory, file_path, content)


def _execute_run_python_file(args: Dict[str, Any]) -> str:
    file_path = args.get("file_path")
    if not file_path:
        return 'Error: "file_path" is required.'

    tool_args_raw = args.get("args", [])
    if tool_args_raw is None:
        tool_args_raw = []
    if not isinstance(tool_args_raw, list):
        return 'Error: "args" must be a list of strings.'

    tool_args: List[str] = []
    for value in tool_args_raw:
        if not isinstance(value, str):
            return 'Error: All entries in "args" must be strings.'
        tool_args.append(value)

    try:
        working_directory = _resolve_working_directory(args.get("working_directory"))
    except ValueError as exc:
        return f"Error: {exc}"

    return run_python_file(working_directory, file_path, tool_args)


TOOL_DEFINITIONS = [
    tool(
        name="get_file_content",
        description="Read the contents of a text file within the repository workspace.",
        parameters={
            "type": "object",
            "properties": {
                "working_directory": {
                    "type": "string",
                    "description": "Relative path from the repository root indicating which subdirectory to treat as the working directory.",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read, relative to the working directory.",
                },
            },
            "required": ["working_directory", "file_path"],
        },
    ),
    tool(
        name="get_files_info",
        description="List files (name, size, directory flag) within a directory of the repository.",
        parameters={
            "type": "object",
            "properties": {
                "working_directory": {
                    "type": "string",
                    "description": "Relative path from the repository root indicating which subdirectory to treat as the working directory.",
                },
                "directory": {
                    "type": "string",
                    "description": "Optional subdirectory to inspect relative to the working directory. Defaults to the working directory root.",
                    "default": ".",
                },
            },
            "required": ["working_directory"],
        },
    ),
    tool(
        name="write_file",
        description="Create or overwrite a file inside the repository with the provided text content.",
        parameters={
            "type": "object",
            "properties": {
                "working_directory": {
                    "type": "string",
                    "description": "Relative path from the repository root indicating which subdirectory to treat as the working directory.",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to create or overwrite within the working directory.",
                },
                "content": {
                    "type": "string",
                    "description": "Full textual content to write into the file.",
                },
            },
            "required": ["working_directory", "file_path", "content"],
        },
    ),
    tool(
        name="run_python_file",
        description="Execute a Python script located inside the repository.",
        parameters={
            "type": "object",
            "properties": {
                "working_directory": {
                    "type": "string",
                    "description": "Relative path from the repository root indicating which subdirectory to treat as the working directory.",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to execute, relative to the working directory.",
                },
                "args": {
                    "type": "array",
                    "description": "Optional command line arguments to pass to the script.",
                    "items": {"type": "string"},
                    "default": [],
                },
            },
            "required": ["working_directory", "file_path"],
        },
    ),
]

TOOL_EXECUTORS: Dict[str, ToolExecutor] = {
    "get_file_content": _execute_get_file_content,
    "get_files_info": _execute_get_files_info,
    "write_file": _execute_write_file,
    "run_python_file": _execute_run_python_file,
}
