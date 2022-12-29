from system import System

class KeyboardSystem(System):
    def __init__(self):
        self.chars = {
            'enter': 10,
            'esc': 27,
            'a': 97,
            'b': 98,
            'c': 99,
            'd': 100,
            'e': 101,
            'f': 102,
            'g': 103,
            'h': 104,
            'i': 105,
            'j': 106,
            'k': 107,
            'l': 108,
            'm': 109,
            'n': 110,
            'o': 111,
            'p': 112,
            'q': 113,
            'r': 114,
            's': 115,
            't': 116,
            'u': 117,
            'v': 118,
            'w': 119,
            'x': 120,
            'y': 121,
            'z': 122,
            '0': 48,
            '1': 49,
            '2': 50,
            '3': 51,
            '4': 52,
            '5': 53,
            '6': 54,
            '7': 55,
            '8': 56,
            '9': 57
        }

    def find_char(self, chr):
        for key, value in self.chars.items():
            if value == chr:
                return key
        return None

    def update(self):
        # get curses
        curses = self.filter_entities(['curses'])[0].get('curses')['value']
        # get key
        key = curses.screen.getch()
        # no keypress ( nodelay = True )
        if key == -1:
            return
        
        value = self.find_char(key)
        # char  not mapped
        if value == None:
            return

        if value == 'esc':
            exit()

        if value in ['w', 'a', 's', 'd', 'enter', 'esc']:
            System.push_event({
                'type': 'key_stroke',
                'value': value 
            })