from system import System
from constants import *

class DungeonSystem(System):

    def update(self):
        # get state and verify that is a dungeon
        state = System.get_entity_component('state')['value']
        if state != 'dungeon':
            return

        # get the map
        dungeon = System.get_entity_component('dungeon')
        
        # get the player
        player = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'player'][0]
        map = dungeon['map'][player.get('position')['floor']]
        blood = dungeon['blood'][player.get('position')['floor']]

        #get the player position
        player_x = player.get('position')['x']
        player_y = player.get('position')['y']

        key = None
        # get event keystroke
        for event in System._events:
            if event['type'] == 'key_stroke':
                key = event['value']
                break
        
        if(key == 'esc'):
            exit()
        
        if key not in ['w', 's', 'a', 'd']:
            return

        if key == 'w':
            player_y -= 1
        elif key == 's':
            player_y += 1
        elif key == 'a':
            player_x -= 1
        elif key == 'd':
            player_x += 1

        fight = False
        # get enemies
        enemies = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'enemy' and e.get('position')['floor'] == player.get('position')['floor']]
        for enemy in enemies:
            # check if player_x and player_y are in the enemy position
            if enemy.get('position')['x'] == player_x and enemy.get('position')['y'] == player_y:
                fight = True
                enemy.get('race')['hp'] -= PLAYER_ATTACK
                blood[enemy.get('position')['y']][enemy.get('position')['x']] = True
                if enemy.get('race')['hp'] <= 0:
                    System.remove_entity_by_id(enemy.id)

        
        # check new position touch the wall
        if map[player_y][player_x] < WALL_FULL and not fight:
            player.get('position')['x'] = player_x
            player.get('position')['y'] = player_y

        if map[player_y][player_x] == CRATE:
            # check if the crate is closed
            crate = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'crate' and e.get('position')['x'] == player_x and e.get('position')['y'] == player_y and e.get('position')['floor'] == player.get('position')['floor']]
            if len(crate) > 0:
                crate = crate[0]
            if crate.get('state')['value'] == 'closed':
                System.push_event({
                    'type': 'noise_event',
                    'value': 'crate_open'
                })
                crate.get('state')['value'] = 'open'

        System.remove_events('key_stroke')
        