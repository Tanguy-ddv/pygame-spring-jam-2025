class Entity:
    def __init__(self, entity_manager, entity_id):
        self.entity_manager = entity_manager
        self.entity_id = entity_id

        self.components = {}

    def add_component(self, component):
        component_type = type(component)

        self.components[component_type] = component
        self.entity_manager.register_component(self.entity_id, component_type)

    def get_id(self):
        return self.entity_id
    
    def get_component(self, component_type):
        return self.components[component_type]