import arcade



class Background(arcade.Window):
    def __init__(self):
        super().__init__(1980, 1080, "background", fullscreen=True)


    def on_draw(self):
        cx = self.width 
        cy = self.height
        color = (240,198, 162, 80)






Background()
arcade.run()