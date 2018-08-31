from Rover import Rover
from PhantomOmniold import PhantomOmni
from time import sleep, time
from utils import mapValues
# import cv2

arm = PhantomOmni("plane")
r = Rover()

claw_open = True
last_claw = True

jolt_delay = 100
last_jolt_time = 0

counter = 0

# def show_image():
# 	global counter
# 	img = r.get_image()
# 	cv2.imwrite("saved_images/{}.jpg".format(counter), img)
# 	print("Saved {}.jpg!".format(counter))
# 	counter += 1



while True:
    try:
        coords = arm.coords
        print(coords)
        # if coords[3]:
        #     show_image()

        x = mapValues(coords[0], -220, 220, -1000, 1000)
        y = mapValues(coords[2], -100, 100, -1000, 1000)   

        leftValue = -y + x
        rightValue = -y - x 
            
        motor1 = int(mapValues(leftValue, -2000, 2000, -255, 255))
        motor2 = int(mapValues(rightValue, -2000, 2000, -255, 255))
        

        if coords[4]:
            claw_open = True
            if claw_open is not last_claw:
                r.set_grip(90)
        else:
            claw_open = False
            if claw_open is not last_claw:
                r.set_grip(0)

        last_claw = claw_open

        if arm.ink():
            motor1 = 0
            motor2 = 0
            sleep(0.5)
            arm.jolt()
            sleep(0.5)

        
        if r.get_floor_data(0) < 100 or r.get_floor_data(1) < 100:
            if last_jolt_time + jolt_delay < time():
                arm.jolt()
                last_jolt_time = time()
 
        r.set_motors(motor1, motor2)
    except KeyboardInterrupt:
        r.stop()
        break
