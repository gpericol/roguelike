from system import System
from screen_system import ScreenSystem
import time
from constants import *
import random

class AnimationSystem(ScreenSystem):
    def update(self):
        # get events from system
        damage_event = None
        bonk_event = None
        death_event = None
        noise_event = None
        for event in self._events:
            if event['type'] == 'damage_event':
                damage_event = event
            if event['type'] == 'bonk_event':
                bonk_event = event
            if event['type'] == 'death_event':
                death_event = event
            if event['type'] == 'noise_event':
                noise_event = event

        if damage_event is None and bonk_event is None and death_event is None and noise_event is None:
            return
        
        for i in range(1,5):
            if bonk_event is not None:
                System.push_event({
                    'type': 'bonk',
                    'value': {
                        'count': i,
                        'value': bonk_event['value']
                    }
                })
            if damage_event is not None:
                System.push_event({
                    'type': 'damage',
                    'value': {
                        'count': i,
                        'value': str(damage_event['value'])
                    }
                })

            if death_event is not None:
                System.push_event({
                    'type': 'death',
                    'value': {
                        'position': death_event['value'],
                        'color':random.choice([COLOR_BROWN, COLOR_GREEN, COLOR_RED, COLOR_WHITE, COLOR_LIGHT_RED, COLOR_LIGHT_BROWN])
                    }
                })

            if noise_event is not None:
                System.push_event({
                    'type': 'noise',
                    'value': {
                        'color': COLOR_WHITE,
                        'symbol': random.choice(['-', '*', '+']),
                        'radius': i + 3
                    }
                })
            super().update()
            time.sleep(0.1)

        # remove noise_event from system
        self.remove_events('damage_event')
        self.remove_events('bonk_event')
        self.remove_events('death_event')
        self.remove_events('noise_event')
        super().update()