import yaml
import importlib

class Tool:
    def __init__(self, config):
        self.name = config['name']
        self.module = config['module']
        self.function = config['function']
        self.instance = self.load_tool()

    def load_tool(self):
        module = importlib.import_module(self.module)
        tool_func = getattr(module, self.function)
        return tool_func

def load_tools_config(file_path):
    with open(file_path, 'r') as file:
        tools_config = yaml.safe_load(file)
    return tools_config