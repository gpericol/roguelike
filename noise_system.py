from system import System
from screen_system import ScreenSystem
import random
import time
from constants import *

class NoiseSystem(ScreenSystem):
    def update(self):
        # get noise_event from system
        noise_event = None
        for event in self._events:
            if event['type'] == 'noise_event':
                noise_event = event
                break
        if noise_event is None:
            return
        
        for i in range(8,10):
            System.push_event({
                'type': 'noise',
                'value': {
                    'color': COLOR_WHITE,
                    'symbol': random.choice(['-', '*', '+']),
                    'radius': i
                }
            })
            super().update()
            time.sleep(0.1)

        # remove noise_event from system
        self.remove_events('noise_event')
        super().update()


