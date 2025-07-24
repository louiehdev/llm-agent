import os

def get_files_info(working_directory, directory=None):
    try:
        wdir_abs_path = os.path.abspath(working_directory)
        dir_abs_path = os.path.abspath(os.path.join(wdir_abs_path, directory)) if directory else wdir_abs_path
        if os.path.commonpath([wdir_abs_path, dir_abs_path]) != wdir_abs_path or not os.path.exists(dir_abs_path):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(dir_abs_path):
            return f'Error: "{directory}" is not a directory'
        files_info = []
        for file in os.listdir(dir_abs_path):
            file_path = os.path.join(dir_abs_path, file)
            file_info = f"- {file}: file_size={os.path.getsize(file_path)} bytes, is_dir={os.path.isdir(file_path)}\n"
            files_info.append(file_info)
        return "".join(files_info)
    except Exception as e:
        return f'Error: {str(e)}'
    
def get_file_content(working_directory, file_path):
    try:
        wdir_abs_path = os.path.abspath(working_directory)
        file_abs_path = os.path.abspath(os.path.join(wdir_abs_path, file_path))
        if os.path.commonpath([wdir_abs_path, file_abs_path]) != wdir_abs_path or not os.path.exists(file_abs_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(file_abs_path):
            return f'Error: "{file_path}" is not a file'
        
        with open(file_abs_path, 'r') as f:
            content = f.read(10000)
            is_large = len(f.read()) > 10000
        if is_large:
            return content + '[...File "{file_path}" truncated at 10000 characters]'
        else:
            return content

    except Exception as e:
        return f'Error: {str(e)}'

def write_file(working_directory, file_path, content):
    try:
        wdir_abs_path = os.path.abspath(working_directory)
        file_abs_path = os.path.abspath(os.path.join(wdir_abs_path, file_path))
        if os.path.commonpath([wdir_abs_path, file_abs_path]) != wdir_abs_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        if not os.path.exists(file_abs_path):
            os.makedirs(os.path.dirname(file_abs_path), exist_ok=True)
        
        with open(file_abs_path, 'w') as f:
            f.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f'Error: {str(e)}'