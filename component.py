import json
import copy

FILE = 'components.json'

class Component:

    _components = None

    def __init__(self, name):
        if Component._components is None:
            with open(FILE, 'r') as f:
                Component._components = json.load(f)
        
        if Component._components.get(name) is None:
            raise ValueError('Component not found')

        self.name = name
        self.data = copy.deepcopy(Component._components[name])

    def __str__(self) -> str:
        return f"{self.data}"