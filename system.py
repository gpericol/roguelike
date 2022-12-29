class System:
    _events = []
    entities = []

    def __init__(self):
        return

    @staticmethod
    def add_entity(entity):
        System.entities.append(entity)

    @staticmethod
    def remove_entity_by_id(id):
        System.entities = [entity for entity in System.entities if entity.id != id]

    @staticmethod
    def filter_entities(names):
        return [entity for entity in System.entities if entity.has(names)]

    # this method is used to get the first entity that has the component and return it
    @staticmethod
    def get_entity_component(name):
        entities = [entity for entity in System.entities if entity.has(name)]
        if len(entities) == 0:
            raise Exception("No entity with this component")
        return entities[0].get(name)


    def update(self):
        pass

    def __str__(self):
        return f"{System.entities}"

    @staticmethod
    def push_event(event):
        System._events.append(event)

    @staticmethod
    def remove_events(name):
        System._events = [event for event in System._events if event.get('type') != name]

    # clean all events
    @staticmethod
    def clean_events():
        System._events = []
