import os
import subprocess

def run_python_file(working_directory, file_path):
    try:
        wdir_abs_path = os.path.abspath(working_directory)
        file_abs_path = os.path.abspath(os.path.join(wdir_abs_path, file_path))
        if os.path.commonpath([wdir_abs_path, file_abs_path]) != wdir_abs_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.exists(file_abs_path):
            return f'Error: File "{file_path}" not found'
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'
        
        result = subprocess.run(["python3", file_abs_path], capture_output=True, text=True, timeout=30)

        if result:
            return f"STDOUT: {result.stdout}\n STDERR: {result.stderr}" if result.returncode == 0 else f"STDOUT: {result.stdout}\n STDERR: {result.stderr}\n Process exited with code {result.returncode}"
        else:
            return "No output produced"

    except Exception as e:
        return f"Error: executing Python file: {e}"