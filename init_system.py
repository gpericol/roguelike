from system import System
from entity import Entity
from component import Component
from dungeon import Dungeon


class InitSystem(System):

    def _prepare_new_world(self):
        # remove entity dungeon
        entity_dungeon = System.filter_entities(['dungeon'])
        if len(entity_dungeon) > 0:
            System.remove_entity_by_id(entity_dungeon[0].id)
        
        #remove entity player
        entity_player = System.filter_entities(['role'])
        if len(entity_player) > 0:
            System.remove_entity_by_id(entity_player[0].id)


        # create dungeon entity
        entity_dungeon = Entity()
        dungeon_height = 200
        dungeon_width = 200
        dungeon_generator = Dungeon(dungeon_width, dungeon_height, 50, 20, 10, 3)
        
        component_dungeon = Component('dungeon')
        component_dungeon.data['floors_number'] = dungeon_generator.floors_num

        for floor in dungeon_generator.floors:
            component_dungeon.data['map'].append(floor.get_map())
            component_dungeon.data['visited'].append(floor.get_visited())

        component_visibility = Component('visibility')
        component_visibility.data['fov'] = 10
        component_visibility.data['visible'] = [[False for x in range(dungeon_width)] for y in range(dungeon_height)]

        entity_dungeon.append(component_dungeon)
        entity_dungeon.append(component_visibility)
        System.add_entity(entity_dungeon)

        # create player entity
        entity_player = Entity()
        component_role = Component('role')
        component_role.data['value'] = 'player'

        component_position = Component('position')
        first_room_center = dungeon_generator.floors[0].get_stair_up()
        component_position.data['x'] = first_room_center[0]
        component_position.data['y'] = first_room_center[1]
        component_position.data['floor'] = 0

        entity_player.append(component_role)
        entity_player.append(component_position)
        System.add_entity(entity_player)

    def update(self):
        # get state
        state = self.get_entity_component('state')['value']
        if state != 'init':
            return

        # get event key_press
        key_press = None
        for event in self._events:
            if event['type'] == 'key_stroke':
                key_press = event
                break
                
        # no keypress
        if key_press is None:
            return

        key = key_press['value']
        if key == 'esc':
            exit()

        elif key == 'enter':
            self._prepare_new_world()
            self.get_entity_component('state')['value'] = 'dungeon'
        
        System.remove_events('key_stroke')