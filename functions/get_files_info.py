import os


def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        # Reject absolute `directory` values to force relative usage.
        if os.path.isabs(directory):
            return "Error: `directory` must be a relative path within the working_directory"

        # Resolve real absolute paths (this follows symlinks and normalizes `..` etc.)
        working_directory = os.path.realpath(working_directory)
        target_dir = os.path.realpath(os.path.join(working_directory, directory))

        # Ensure containment
        if os.path.commonpath([working_directory, target_dir]) != working_directory:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Ensure the target exists
        if not os.path.exists(target_dir):
            return f'Error: "{directory}" is not a directory'

        # Collect file information
        entries = []
        for name in sorted(os.listdir(target_dir)):
            abspath = os.path.join(target_dir, name)
            try:
                st = os.stat(abspath)
            except OSError:
                continue

            relpath = os.path.relpath(abspath, working_directory)
            entries.append({
                "name": name,
                "relpath": relpath,
                "abspath": abspath,
                "is_dir": os.path.isdir(abspath),
                "size": st.st_size,
                "mtime": st.st_mtime,
            })

        # Format output
        lines = []
        for e in entries:
            lines.append(f"- {e['name']}: file_size={e['size']} bytes, is_dir={e['is_dir']}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error: {str(e)}"
