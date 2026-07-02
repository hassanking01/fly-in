import arcade



class Background(arcade.Window):
    def __init__(self):
        super().__init__(1980, 1080, "background", fullscreen=True)


    def on_draw(self):
        cx = self.width 
        cy = self.height
        color = (240,198, 162, 80)
        for i in range(4, self.width, 22):
            arcade.draw_line(0, i, cx, i, color)

        for i in range(0, self.width , 80):
            arcade.draw_line(0, i, cx, i, color, line_width=5)
            arcade.draw_line(i,0,i,cy, color , line_width=5)





Background()
arcade.run()