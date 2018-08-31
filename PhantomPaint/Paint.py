'''A demo using the Geomagic Touch where you can paint on a canvas. Mechanics are extremely simple; there is only a
paintbrush/pencil and an eraser. The harder you push with the brush, the thicker the line'''

from PhantomOmni import PhantomOmni
import Tkinter as tk
import os 
import psutil

FILEPATH = os.path.dirname(os.path.realpath(__file__))

PENCIL, ERASER = list(range(2))
TOOLS = [PENCIL, ERASER]

USING_PHANTOM = True

class Paint():
    def __init__(self):
        #set up tkinter window
        self.root = tk.Tk()
        self.root.geometry("1800x1000")
        self.root.resizable(width=False, height=False)
        self.root.title("PhantomPaint")
        self.root.configure(background="light gray")

        #used to store references to tkinter photoimages so they aren't deleted by garbage collection
        self._references = []
        self.show_toolbar()
        self.create_canvas()
        if USING_PHANTOM:
            self.setup_phantom()
        self.old_mouse = None
        
    def show_toolbar(self):
        '''Creates the buttons for the tools as well as initializing some base options'''
        self.toolbar = tk.Frame(self.root, bg="light gray", width=150, height=500, bd=5, relief=tk.RIDGE)
        self.toolbar.place(x=10, y=10)
        self.tools = []
        for tool in TOOLS:
            self._references.append(tk.PhotoImage(file=FILEPATH+"/tools/{}.png".format(str(tool))))
            b = tk.Button(self.toolbar, text=str(tool), image=self._references[-1], relief=tk.RAISED, command=lambda tool=tool:self.set_selected_tool(tool))
            b.pack(fill=None, expand=False)
            self.tools.append(b)
        self.set_selected_tool(0)
        self.tool_size = 10
        self.selected_color = "black"
        self.steps = []

    def create_canvas(self):
        '''Creates the canvas and creates button bindings'''
        self.c = tk.Canvas(self.root, width=1600, height=980, bg="white", cursor="pencil")
        self.c.place(x=170, y=10)
        self.c.bind("<Button-1>", self.mouse_down)
        self.c.bind("<B1-Motion>", self.mouse_down_move)
        self.c.bind("<ButtonRelease-1>", self.mouse_up)
        self.root.bind_all("<Control-z>", self.undo)
    
    def set_selected_tool(self, tool):
        '''Updates the selected tool and button visuals'''
        [b.configure(relief=tk.RAISED) for b in self.tools]
        self.tools[tool].configure(relief=tk.SUNKEN)
        self.selected_tool = tool

    def setup_phantom(self):
        self.phantom = PhantomOmni(mode="mouse")
    
    def mouse_down(self, event):
        '''Callback called when mouse goes down - uses the tool where it was placed, once'''
        self.curr_step = []
        if self.selected_tool == PENCIL or self.selected_tool == ERASER:
            color = self.selected_color
            if self.selected_tool == ERASER:
                color = "white"
            if 170 < event.x < 1770 and 10 < event.y < 990:
                if USING_PHANTOM:
                    coords = self.phantom.coords
                    if coords[2] < 45:
                        extra = 45 - (int(coords[2]))
                    else:
                        extra = 0
                    self.curr_step.append(self.c.create_oval(event.x-(self.tool_size+extra)/2, 
                    event.y-(self.tool_size+extra)/2, 
                    event.x+(self.tool_size+extra)/2, 
                    event.y+(self.tool_size+extra)/2,
                    fill=color,
                    width=0))
                    self.old_mouse = [event.x, event.y]
                else:
                    self.curr_step.append(self.c.create_rectangle(event.x-self.tool_size/2, 
                    event.y-self.tool_size/2, 
                    event.x+self.tool_size/2, 
                    event.y+self.tool_size/2,
                    fill=color,
                    width=0))
        self.old_mouse = [event.x, event.y]
    
    def mouse_down_move(self, event):
        '''Callback called when the mouse moves while down (i.e called a lot)'''
        if self.old_mouse is None:
            self.mouse_down(event)
        if self.selected_tool == PENCIL or self.selected_tool == ERASER:
            if 0 < event.x < 1770 and 10 < event.y < 990:
                color = self.selected_color
                if self.selected_tool == ERASER:
                    color = "white"
                if USING_PHANTOM:
                    coords = self.phantom.coords
                    if coords[2] < 45:
                        extra = 45 - (int((coords[2])))
                    else:
                        extra = 0
                    
                    #creates a line between the last place this callback was run and where the mouse is now
                    #the line has rounded ends to appear as smooth as possible
                    self.curr_step.append(self.c.create_line(
                        self.old_mouse[0], 
                        self.old_mouse[1], 
                        event.x, 
                        event.y,
                        fill=color,
                        width=self.tool_size+extra, 
                        capstyle=tk.ROUND, 
                        smooth=tk.TRUE
                    ))
                    self.old_mouse = [event.x, event.y]
                else:
                    self.curr_step.append(self.c.create_line(
                        self.old_mouse[0], 
                        self.old_mouse[1], 
                        event.x, 
                        event.y,
                        fill=color,
                        width=self.tool_size, 
                        capstyle=tk.ROUND, 
                        smooth=tk.TRUE
                    ))
                    self.old_mouse = [event.x, event.y]

    def mouse_up(self, event):
        '''Callback run when mouse goes up'''
        self.steps.append(self.curr_step)

    def undo(self, event):
        '''Callback run when ctrl-z is pressed - undoes last brush stroke'''
        if self.steps == []:
            return
        for line in self.steps[-1]:
            self.c.delete(line)
        self.steps.pop(-1)
        
try:
    x = Paint()
    x.root.mainloop()
except Exception as e:
    pass
x.phantom.kill()