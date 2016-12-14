from gpiozero import Button


class Switch(Button):
    def __init__(self, pin, parent, **kwargs):
        super().__init__(pin, **kwargs)
        self.parent = parent
