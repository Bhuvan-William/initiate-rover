'''Where the magic happens'''
from Rover import Rover

x = Rover()
objects = x.get_objects()
#objects = {"RED":(0, 0, 0)}
print(objects)
#x.alert_relevant_cars(objects)

x.cleanClose()
