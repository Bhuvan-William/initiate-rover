'''Where the magic happens but differently'''
from Rover import Rover

x = Rover()
objects = x.get_objects()
x.alert_relevant_cars2(objects)

x.cleanClose()