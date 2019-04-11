import tkinter as tkr
import trajectory_lib as lib
import numpy as np
from matplotlib import pyplot as plt


class Cursor(tkr.Tk):
    
    def __init__(self, width = 1200, height = 800, y_at_zero = 0):
        
        tkr.Tk.__init__(self)
        fr = tkr.Frame(self)
        fr.pack()
        self.canvas = tkr.Canvas(fr, height = height, width = width, bg = 'black')
        self.canvas.pack()
        self.radius = 50
        self.id = self.draw_circle("red")
        
        self.scale = height - 200
        self.origin = (width/2, 4/5*height)
        xo, yo = self.origin
        self.canvas.move(self.id, xo, yo - self.scale*y_at_zero)
        
    def draw_circle(self, color):
        r =  self.radius
        return self.canvas.create_oval(-r, -r, +r, +r, fill = color)
    
    def update(self, dy):
        #move the object
        self.canvas.move(self.id, 0, - self.scale*dy)
        self.canvas.update()


x1 = lib.Segment(5).generate(0.25)
x2 = lib.Ramp(50).generate(0.25, 2)
x = np.append(x1, x2)
y = lib.Frequency_trajectory_to_Chirp(x, A = 0.5)

#tb1 = lib.Trapezium_Block(slope = [0.75, 1.25, 2.5, 5])
#y = tb1.bind(t_pause = (2.5,5), t_plateau = (1,2.5))

dy = np.diff(y)
plt.plot(y)

c = Cursor(y_at_zero = 0.5)

for dy_k in dy:    
    c.update(dy_k)
    c.after(int(1000/60.0))
    
#tk.mainloop()