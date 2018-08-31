'''Allows you to control the head of the rover using the Geomagic Touch'''
from Rover import Rover
from PhantomOmni import PhantomOmni
from time import sleep, time
from Tkinter import Tk, Canvas, Label
from threading import Thread
import cv2

x = PhantomOmni("position")
r = Rover()

#set up tkinter window with canvas
root = Tk()
root.title = "PhantomOmni+Rover:Head Following"
root.geometry("600x600")
c = Canvas(root, width=600, height=600)
c.pack()

lastShowTime = 0
showDelay = 0.1

counter = 0
locked = False


def capture_image():
    global counter
    #Gets image from stream and saves it
    img = r.get_image()
    cv2.imwrite("saved_images/{}.jpg".format(counter), img)
    print("Saved {}.jpg!".format(counter))
    counter += 1

def phantom_to_servos(coords):
    '''Maps arm coordinates to servo values'''
    servox = 150-((coords[0] + 200)/400*150)-75
    servoy = ((coords[1] + 100)/300*130)-50
    return (int(servox), int(servoy))

#easily create circle for convenience
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle

pointer = 0

t = time()
x_label = Label(root, text="X:")
x_label.place(x=10, y=10)
y_label = Label(root, text="Y:")
y_label.place(x=10, y=30)
z_label = Label(root, text="Z:")
z_label.place(x=10, y=50)

while True:
    
    #maps arm coordinates to servo values, and periodically move the rover's head there
    coords = x.coords
    servos = phantom_to_servos(coords)
    if time() - t > 0.5 and not locked:
        r.pan_servo(-servos[0])
        r.tilt_servo(servos[1])
        t = time()

    #display arm's coordinates in tkinter window
    x_label["text"] = "X: {}".format(coords[0])
    y_label["text"] = "Y: {}".format(coords[1])
    z_label["text"] = "Z: {}".format(coords[2])

    #visual representation of where the arm's pen point is
    c.delete(pointer)
    pointer = c.create_circle(coords[0]+300, 600-coords[1]-300, (coords[2]+120)/15, fill="black")

    #locks the head if button two is pressed
    if coords[4]:
		print("Toggled camera lock!")
		locked = not locked
		sleep(1)
    
    #saves an image from the rover if button one is pressed
    if coords[3]:
        capture_image()
        
    root.update_idletasks()
    root.update()