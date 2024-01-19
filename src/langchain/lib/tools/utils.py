import pkgutil
import importlib
import inspect
from langchain.tools import BaseTool


import pkgutil
import importlib
import inspect
import os
from langchain.tools import BaseTool
import importlib.util
from typing import List


def get_custom_tools() -> List[BaseTool]:
    tools: List[BaseTool] = []
    root_package = str(__package__)
    spec = importlib.util.find_spec(root_package)

    if spec and spec.origin:
        package_dir = os.path.dirname(spec.origin)
        for _, module_name, _ in pkgutil.walk_packages(path=[package_dir], prefix=root_package + '.'):
            module = importlib.import_module(module_name)
            for _, cls in inspect.getmembers(module):
                if inspect.isclass(cls) and issubclass(cls, BaseTool) and cls is not BaseTool:
                    obj = cls()
                    if hasattr(obj, 'should_use') and not obj.should_use:
                        print(f'Not using tool: {cls.__name__}')
                        continue
                    tools.append(cls)

    return tools
