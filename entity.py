import uuid

class Entity:
    def __init__(self):
        self.id = uuid.uuid4()
        self._components = {}

    def append(self, component):
        self._components[component.name] = component.data

    def set(self, name, data):
        self._components[name] = data

    def get(self, name):
        return self._components[name]

    def remove(self, name):
        del self._components[name]
    
    # find entities with components
    def has(self, names):
        if type(names) is not list:
            names = [names]
        
        for name in names:
            if name not in self._components:
                return False
        return True

    def __str__(self):
        return f"{self.id} - {[key for key in self._components.keys()]}"