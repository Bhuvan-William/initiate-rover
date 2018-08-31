'''Records motions made by the arm to a file for later playback'''
from PhantomOmni import PhantomOmni
from time import sleep
from tqdm import tqdm
from Tkinter import Tk, Canvas, Label
import sys

filename = "/home/robot/Documents/save.txt"
if len(sys.argv) > 1:
    filename = sys.argv[1]



#sets up tkinter window with canvas
root = Tk()
root.title = "PhantomOmni+Rover:Head Following"
root.geometry("600x600")
c = Canvas(root, width=600, height=600)
c.pack()

#create circle method for convenience
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle

pointer = 0

#labels to show position of arm
x_label = Label(root, text="X:")
x_label.place(x=10, y=10)
y_label = Label(root, text="Y:")
y_label.place(x=10, y=30)
z_label = Label(root, text="Z:")
z_label.place(x=10, y=50)


arm = PhantomOmni("position")
sleep(3)
moves = []

print("Recording!")
while True:
    try:
        #get coordinates of arm and save them to an array
        coords = arm.coords
        moves.append(coords)

        #updates labels with where the arm is
        x_label["text"] = "X: {}".format(coords[0])
        y_label["text"] = "Y: {}".format(coords[1])
        z_label["text"] = "Z: {}".format(coords[2])
        
        #updates visual representation of arm's position
        c.delete(pointer)
        pointer = c.create_circle(coords[0]+300, 600-coords[1]-300, (coords[2]+120)/15, fill="black")

        root.update_idletasks()
        root.update()

        sleep(0.002)

    except KeyboardInterrupt:
        break

#opens save file to write all recorded points to
with open(filename, "w") as f:
    for move in tqdm(moves):
        formatted = []

        #formats with zero padding and polarity signs
        for x in move:
            if str(x)[0] != "-":
                x = "+"+str(x)
            x = str(x).ljust(8, "0")
            formatted.append(x)

        f.write("{}|{}|{}\n".format(formatted[0], formatted[1], formatted[2]))