from system import System
from entity import Entity
from component import Component
from dungeon import Dungeon

class StateSystem(System):

    def create_stairs(self, position, floor_number, role):
        entity_stair = Entity()
        component_role = Component('role')
        component_role.data['value'] = role
        component_position = Component('position')
        component_position.data['x'] = position[0]
        component_position.data['y'] = position[1]
        component_position.data['floor'] = floor_number
        entity_stair.append(component_role)
        entity_stair.append(component_position)
        System.add_entity(entity_stair)

    def load_dungeon(self):
        # create dungeon entity
        entity_dungeon = Entity()
        dungeon_height = 100
        dungeon_width = 100
        dungeon_generator = Dungeon(dungeon_width, dungeon_height, 40, 20, 10, 3)
        
        component_dungeon = Component('dungeon')
        component_dungeon.data['floors_number'] = dungeon_generator.floors_num

        for floor in dungeon_generator.floors:
            component_dungeon.data['map'].append(floor.get_map())
            component_dungeon.data['visited'].append(floor.get_visited())
            component_dungeon.data['blood'].append(floor.get_blood())
            component_dungeon.data['rooms_center'].append(floor.get_rooms_center())
            component_dungeon.data['paths'].append(floor.get_paths())

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

        component_status = Component('status')

        entity_player.append(component_role)
        entity_player.append(component_position)
        entity_player.append(component_status)

        System.add_entity(entity_player)

        # create enemies
        for floor in dungeon_generator.floors:
            for enemy in floor.get_enemies():
                entity_enemy = Entity()
                component_role = Component('role')
                component_role.data['value'] = 'enemy'

                component_position = Component('position')
                component_position.data['x'] = enemy[0]
                component_position.data['y'] = enemy[1]
                component_position.data['floor'] = floor.floor_number

                component_race = Component('race')

                races = {
                    0: ('Z', 'Zombie', 10, 10, 5),
                    1: ('G', 'Ghoul', 20, 10, 5),
                    2: ('V', 'Vampire', 20, 20, 5),
                }
                symbol, value, hp, attack, fov = races[enemy[2]]
                component_race.data['symbol'] = symbol
                component_race.data['value'] = value
                component_race.data['hp'] = hp
                component_race.data['attack'] = attack
                component_race.data['fov'] = fov

                component_direction = Component('direction')
                component_direction.data['x'] = None
                component_direction.data['y'] = None

                entity_enemy.append(component_role)
                entity_enemy.append(component_position)
                entity_enemy.append(component_direction)
                entity_enemy.append(component_race)
                System.add_entity(entity_enemy)

        # create crates
        for floor in dungeon_generator.floors:
            for crate in floor.get_crates():
                entity_crate = Entity()
                component_role = Component('role')
                component_role.data['value'] = 'crate'

                component_position = Component('position')
                component_position.data['x'] = crate[0]
                component_position.data['y'] = crate[1]
                component_position.data['floor'] = floor.floor_number

                component_state = Component('state')
                component_state.data['value'] = 'closed'

                entity_crate.append(component_role)
                entity_crate.append(component_position)
                entity_crate.append(component_state)
                
                System.add_entity(entity_crate)

        # create stairs
        for floor in dungeon_generator.floors:
            # first floor no stair up
            if floor.floor_number != 0:
                self.create_stairs(floor.get_stair_up(), floor.floor_number, 'stair_up')
            # goal
            if floor.floor_number == dungeon_generator.floors_num - 1:
                self.create_stairs(floor.get_stair_down(), floor.floor_number, 'goal')
            # stair down
            else: 
                self.create_stairs(floor.get_stair_down(), floor.floor_number, 'stair_down')



    def unload_dungeon(self):
        #remove entity player and enemies and crates
        entity_roles = System.filter_entities(['role'])
        for e in entity_roles:
            System.remove_entity_by_id(e.id)

        # remove entity dungeon
        entity_dungeon = System.filter_entities(['dungeon'])
        for e in entity_dungeon:
            System.remove_entity_by_id(e.id)

        
    """
        event: state_change
        {
            "type": "state_change",
            "value": "state"
        }

        states:
            - init
            - dungeon
            - gameover
    """

    # states: init --> dungeon --> gameover --> init

    def update(self):

        new_state = None
        # find event with type state_change
        for event in self._events:
            if event.get('type') == 'state_change':
                new_state = event["value"]
                break

        if new_state is None:
            return
        
        if new_state == 'gameover':
            self.unload_dungeon()
            System.get_entity_component('state')['value'] = "gameover"

        if new_state == 'win':
            self.unload_dungeon()
            System.get_entity_component('state')['value'] = "win"

        if new_state == 'dungeon':
            self.load_dungeon()
            System.get_entity_component('state')['value'] = "dungeon"

        if new_state == 'init':
            self.unload_dungeon()
            System.get_entity_component('state')['value'] = "init"

        # remove change state event
        System.remove_events('state_change')