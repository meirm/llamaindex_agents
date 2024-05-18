def add(x: float, y: float) -> float:
    """Adds two floats together."""
    return x + y

def subtract(x: float, y: float) -> float:
    """Subtracts two floats together."""
    return x - y

def multiply(x: float, y: float) -> float:
    """Multiplies two floats together."""
    return x * y

def divide(x: float, y: float) -> float:
    """Divides two floats together."""
    if y == 0:
        raise ValueError("Cannot divide by zero!")
    return x / y

def human_input(query:str) -> str: 
    """Prompts the user for input."""
    return input(query)

import sys
import io

class CodeExecutor:
    def __init__(self):
        pass
    
    def execute_code(self, code):
        try:
            # Redirect stdout to capture print outputs
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            
            # Compile and execute the code
            exec(code)
            
            # Get the output
            output = new_stdout.getvalue()
            print("Output:", output)
            # Restore stdout
            sys.stdout = old_stdout
            
            return output
        except Exception as e:
            return str(e)

# Sample usage
# code_executor = CodeExecutor()
# sample_code = """
# def fibonacci(n):
#     if n <= 1:
#         return n
#     else:
#         return fibonacci(n-1) + fibonacci(n-2)

# result = fibonacci(12)
# print(result)
# """
# output = code_executor.execute_code(sample_code)
# print("Output:", output)

def repl(code:str) -> str:
    """Execute python code and returns the stdout. Code needs to print the output."""
    code_executor = CodeExecutor()
    output = code_executor.execute_code(code)
    print("Output:", output)
    print("Code:", code)
    return output