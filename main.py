import os
import sys
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai

client = genai.Client(api_key=api_key)

from google.genai import types
from functions.get_files_info import get_files_info, get_file_content, write_file
from functions.run_python import run_python_file

system_prompt = """
You are a friendly and helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.")}))

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the content of a file in the specified directory and slices it to 10000 characters, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path for the file to read, relative to the working directory.")}))

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes the provided content to the file at the provided file path, constrained to the working directory. If no file is found at the provided file path, one is created",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path for the file to read, relative to the working directory."), 
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.")}))

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs the python file found at the provided file path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path for the python file to run, relative to the working directory.")}))

available_functions = types.Tool(function_declarations=[schema_get_files_info, schema_get_file_content, schema_write_file, schema_run_python_file])

def generate_response():
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else sys.exit('Usage: python main.py "prompt"')
    verbose_flag = True if len(sys.argv) > 2 and sys.argv[2] == "--verbose" else False
    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]
    counter = 1
    while counter <= 20:
        
        response = client.models.generate_content(
        model="gemini-2.0-flash-001", 
        contents=messages, 
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt))
        for candidate in response.candidates:
            messages.append(candidate.content)
        prompt_tokens = response.usage_metadata.prompt_token_count
        response_tokens = response.usage_metadata.candidates_token_count
        if response.function_calls and counter < 20:
            for function in response.function_calls:
                result = call_function(function, verbose_flag)
                messages.append(result)
                if result.parts[0].function_response.response:
                    if verbose_flag:
                        print(f"-> {(result.parts[0].function_response.response)["result"]}")
                else:
                    raise Exception(f"Error: no function results for {function}")
        else:
            print(response.text)
            break
        if verbose_flag:
            print(f"User prompt: {user_prompt}")
            print(f"Prompt tokens: {prompt_tokens}\nResponse tokens: {response_tokens}")

        counter += 1

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_name = function_call_part.name
    function_args = {"working_directory": "./calculator", **(function_call_part.args if function_call_part.args is not None else {})}
    function_result = ""
    match function_name:
        case "get_files_info":
            function_result = get_files_info(**function_args)
        case "get_file_content":
            function_result = get_file_content(**function_args)
        case "write_file":
            function_result = write_file(**function_args)
        case "run_python_file":
            function_result = run_python_file(**function_args)
        case _:
            return types.Content(role="tool", parts=[types.Part.from_function_response(name=function_name, response={"error": f"Unknown function: {function_name}"})])
    
    return types.Content(role="tool", parts=[types.Part.from_function_response(name=function_name, response={"result": function_result})])

def main():
    generate_response()

main()