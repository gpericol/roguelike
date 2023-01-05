from system import System
from constants import *
import random
from component import Component

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
                    System.push_event({
                        'type': 'death_event',
                        'value': {
                            'x': enemy.get('position')['x'],
                            'y': enemy.get('position')['y']
                        }
                    })
                    System.remove_entity_by_id(enemy.id)
                else:
                    component_bonk = Component('bonk')
                    component_bonk.data['value'] = random.randint(3, 8)
                    enemy.append(component_bonk)
                    System.push_event({
                        'type': 'bonk_event',
                        'value': component_bonk.data['value']
                    })

        stair = False
        # check if the player is in the stair up
        stair_up = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'stair_up' and e.get('position')['x'] == player_x and e.get('position')['y'] == player_y and e.get('position')['floor'] == player.get('position')['floor']]
        if len(stair_up) > 0:
            stair_up = stair_up[0]
        else:
            stair_up = None

        if stair_up is not None:
            player.get('position')['floor'] -= 1
            # get stair down
            stair_down = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'stair_down' and e.get('position')['floor'] == player.get('position')['floor']]
            player.get('position')['x'] = stair_down[0].get('position')['x']
            player.get('position')['y'] = stair_down[0].get('position')['y']
            stair = True
        
        # check if the player is in the stair down
        stair_down = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'stair_down' and e.get('position')['x'] == player_x and e.get('position')['y'] == player_y and e.get('position')['floor'] == player.get('position')['floor']]
        if len(stair_down) > 0:
            stair_down = stair_down[0]
        else:
            stair_down = None

        if stair_down is not None:
            # set new floor
            player.get('position')['floor'] += 1
            
            # get stair up
            stair_up = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'stair_up' and e.get('position')['floor'] == player.get('position')['floor']]
            
            # set player new position
            player.get('position')['x'] = stair_up[0].get('position')['x']
            player.get('position')['y'] = stair_up[0].get('position')['y']
            stair = True

        # add goal
        goal = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'goal' and e.get('position')['floor'] == player.get('position')['floor']]
        win = False
        if len(goal) > 0:
            goal = goal[0]
        else:
            goal = None
        
        if goal is not None:
            if goal.get('position')['x'] == player_x and goal.get('position')['y'] == player_y:
                System.push_event({
                    "type": "state_change",
                    "value": "win"
                })
                win = True
                

        # check new position touch the wall
        if map[player_y][player_x] < WALL_FULL and not fight and not stair and not win:
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
                    'value': {
                        'x': crate.get('position')['x'],
                        'y': crate.get('position')['y']
                    }
                })
    
                # make a random chioice with 0.5 probability
                if random.random() < 0.5:
                    # add +10 sanity
                    player.get('status')['sanity'] += 10
                    if player.get('status')['sanity'] > player.get('status')['max_sanity']:
                        player.get('status')['sanity'] = player.get('status')['max_sanity']
                    System.push_event({
                        'type': 'sanity_event',
                        'value': 10
                    })
                else:
                    # add + 10 health
                    player.get('status')['hp'] += 10
                    if player.get('status')['hp'] > player.get('status')['max_hp']:
                        player.get('status')['hp'] = player.get('status')['max_hp']
                    System.push_event({
                        'type': 'health_event',
                        'value': 10
                    })

                crate.get('state')['value'] = 'open'

        System.remove_events('key_stroke')
        