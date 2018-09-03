'''Contain the Rover class - allowing one to control the rover,
as well as access its sensory data'''

import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')

import logging
logging.basicConfig(format="%(relativeCreated)d | %(message)s", filename="../logs/run.log", level=logging.DEBUG)

import socket
import time
import io
from time import sleep
import urllib
import json
import math
import cv2
import numpy as np
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Rover(object):
    '''Rover class - sends commands to the rover to move it,
    or to get data from it, like from the distance sensors or
    camera. Also contains some image recognition code for working
    with images gotten from the rover'''

    OBJECT_SIZES = {"RED":4, "BLUE":5}

    def __init__(self):
        logging.info("Initiating rover")
        self.debug = True
        # Network variables for wifi
        #self.ai_addr = ('10.123.1.2', 10000)
        #self.rover_addr = ('10.123.1.43', 10000)
        #self.graph_addr = ('10.123.1.2', 10001)
        self.ai_addr = ('172.16.80.145', 10000)
        self.rover_addr = ('172.16.80.185', 10000)
        self.graph_addr = ('172.16.80.145', 10001)
        self.recipients = {
            ('172.16.80.130', 10004) : "Laptop_1"
        }

        self.coords = [0, 0]

        logging.info("About to construct socket with robot")
        t = time.time()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.ai_addr)
        logging.warning("Bound rover socket: took %ss", time.time()-t)

        self.top_speed = 110
        self.led_toggle = 0

        self.pan_angle = 0
        self.title_angle = 0
        self.right_pan_limit = 75
        self.left_pan_limit = -self.right_pan_limit
        self.top_tilt_limit = 80
        self.bottom_tilt_limit = -50
        self.angle_step = 5
        self.pan_servo(0)
        self.tilt_servo(0)

        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

        self.dims = (640, 480)
        self.center_tolerances = [self.dims[1]/2-200, self.dims[0]/2+200,
                                  self.dims[1]/2+200, self.dims[0]/2-200]
        self.edge_tolerances = [self.dims[0]/2 - 500, self.dims[0]/2 + 500]
        self.found_face = False
        
        logging.info("Reading thresholds.json")
        t = time.time()
        with open("../thresholds.json", "r") as file_obj:
            self.thresholds = json.load(file_obj)
        logging.warning("Read thresholds in %ss", time.time()-t)
        
    def listenFromSockets(self):
        t = time.time()
        data = self.sock.recvfrom(1024)
        logging.warning("Received information from %s after %ss", str(data[1]), time.time()-t)
        return data
    
    def getCoords(self):
        logging.warning("GETTING COORDS")
        t = time.time()
        for sock, name in self.recipients.items():
            self.sock.sendto("?coords", sock)
            logging.info("Asking %s aka %s for its location", str(sock), name)
        logging.warning("Asked all recipients for locations in %ss", time.time()-t)

    def alert_relevant_cars(self, objects):
        logging.warning("ALERTING RELEVANT CARS")
        self.getCoords()
        while True:
            logging.warning("Waiting for co-ordinates")
            t = time.time()
            data = self.listenFromSockets()
            logging.warning("Received co-ordinated in %ss", time.time()-t)
            if data[1] in self.recipients.keys():
                coords = [int(x) for x in data[0].split(":")[1].split(",")]
                logging.info("Co-ordinates received are %s", str(coords))

                for color, obj in objects.items():
                    if abs(coords[0] - obj[0]) + abs(coords[1] - obj[1]) < 40:
                        t = time.time()
                        logging.warning("Sending START command to %s about %s object", str(data[1]), color)
                        self.sock.sendto("!start:{}:{},{}:{}:".format(color, obj[0], obj[1], obj[2]), data[1])
                        logging.warning("SENT in %ss", time.time()-t)
                        
                self.send_photos()
                break
        return
    


    def alert_relevant_cars2(self, objects):
        logging.warning("ALERTING RELEVANT CARS")
        self.getCoords()
        while True:
            logging.warning("Waiting for co-ordinates")
            t = time.time()
            data = self.listenFromSockets()
            logging.warning("Received co-ordinated in %ss", time.time()-t)
            if data[1] in self.recipients.keys():
                coords = [int(x) for x in data[0].split(":")[1].split(",")]
                logging.info("Co-ordinates received are %s", str(coords))

                for color, obj in objects.items():
                    if abs(coords[0] - obj[0]) + abs(coords[1] - obj[1]) < 100:
                        t = time.time()
                        logging.warning("Sending START command to %s about %s object", str(data[1]), color)
                        self.sock.sendto("!start:{}:{},{}:{}:".format(color, obj[0], obj[1], obj[2]), data[1])
                        logging.warning("SENT in %ss", time.time()-t)
                break
        return 
    
    def send_photos(self):
        '''Talks to recipients and manages their requests for pictures of previously
        specified objects'''
        logging.warning("MANAGING PHOTO REQUESTS")
        while True:
            logging.warning("Waiting for image requests")
            t = time.time()
            data = self.listenFromSockets()
            logging.warning("Received image request after %ss", time.time()-t)
            splitData = data[0].split(":")
            if data[1] in self.recipients.keys():
                if splitData[0] == "!photo" and splitData[1] == "1":
                    logging.info("Moving camera to face object")
                    self.pan_servo(splitData[2])
                    sleep(1)
                    logging.info("About to send command to take photo of object from stream")
                    self.sock.sendto("!takePhoto", data[1])
                    logging.warning("Sent command to take photo to %s", str(data[1]))
                    logging.info("Listening for photo process end acknowledgement")
                    data = self.listenFromSockets()
                    if data[0] == "!returnServo":
                        logging.warning("Photo request complete.")
                        self.pan_servo(0)
                
    def cleanClose(self):
        '''Closes active sockets(s)'''
        self.sock.close()

    def set_motors(self, left, right):
        '''Set the motors on the rover'''
        motor_params = ["Motor"]
        motor_params.append(str(left))
        motor_params.append(str(right))
        motor_params = ','.join(str(e) for e in motor_params)
        self.sock.sendto(motor_params, self.rover_addr)
        self.sock.sendto(motor_params, self.graph_addr)

    def forwards(self, speed=None):
        '''Set the rover to moving forward'''
        if speed is None:
            speed = self.top_speed
        self.set_motors(speed, speed)

    def backwards(self, speed=None):
        '''Set the rover to moving backwards'''
        if speed is None:
            speed = self.top_speed
        self.set_motors(-1 * speed, -1 * speed)

    def left(self, speed=None):
        '''Set the robot to turning left'''
        if speed is None:
            speed = self.top_speed
        self.set_motors(-1 * speed, speed)

    def right(self, speed=None):
        '''Set the robot to turning right'''
        if speed is None:
            speed = self.top_speed
        self.set_motors(speed, -1 * speed)

    def edge_left(self):
        '''Turn the robot leftwards slightly'''
        self.left(75)
        sleep(0.5)
        self.stop()

    def edge_right(self):
        '''Turn the robot rightwards slightly'''
        self.right(75)
        sleep(0.5)
        self.stop()

    def stop(self):
        '''Stop all movement from the robot'''
        self.set_motors(0, 0)

    def get_image(self):
        '''Get an image from the PiCamera on the rover from the UV4L web stream'''
        '''
        t = time.time()
        logging.info("About to capture image from stream")
        stream = urllib.urlopen('http://{}:8080/stream/video.mjpeg'.format(self.rover_addr[0]))
        returned_bytes = ''
        while True:
            returned_bytes += stream.read(1024)
            start = returned_bytes.find('\xff\xd8')
            end = returned_bytes.find('\xff\xd9')
            if start != -1 and end != -1:
                jpg = returned_bytes[start:end+2]
                returned_bytes = returned_bytes[end+2:]
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                logging.warning("Captured image in %ss", time.time()-t)
        '''
        x = time.time()
        stream=urllib.urlopen('http://{}:8080/stream/video.mjpeg'.format(self.rover_addr[0]))
        bytes=''
        
        while True:
            
            
            bytes+=stream.read(1024)
            a = bytes.find('\xff\xd8')
            b = bytes.find('\xff\xd9')
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2]
                bytes= bytes[b+2:]
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                print(time.time()-x)
                return i
        '''
        self.sock.sendto("Picture", self.rover_addr)
        part_count = self.sock.recvfrom(4096)
        print(part_count)
        part_count = part_count[0]
        self.sock.sendto("", self.rover_addr)
        data = ""
        
        for i in range(int(part_count.split(":")[1])):
            data += self.sock.recvfrom(4096)[0]
            self.sock.sendto("", self.rover_addr)
            print(i)
        #print(data)
        img = Image.open(io.BytesIO(data)).convert("RGB")
        open_cv_image = np.array(img) 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        return open_cv_image
        '''

    def detect_face(self, img):
        '''Return information about the most prevalent face in the image (if any)
            Returns the original image with a rectangle around the face, and a tuple
            of the coordinates of the face in the image, and its width and height'''
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        try:
            x_coord, y_coord, width, height = faces[0]
            cv2.rectangle(img, (x_coord, y_coord), (x_coord+width, y_coord+height), (255, 0, 0), 2)
            roi_gray = gray[y_coord:y_coord+height, x_coord:x_coord+width]
            roi_color = img[y_coord:y_coord+height, x_coord:x_coord+width]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            for (eye_x, eye_y, eye_width, eye_height) in eyes:
                cv2.rectangle(roi_color, (eye_x, eye_y),
                              (eye_x+eye_width, eye_y+eye_height),
                              (0, 255, 0), 2
                             )
            self.found_face = True
            return img, (x_coord, y_coord, width, height)
        except cv2.error:
            self.found_face = False
            return img, 1

    def follow_face(self):
        '''Draws a rectangle around all faces in a captured image
        (not sure why we still keep this)'''
        while True:
            img = self.get_image()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x_coord, y_coord, width, height) in faces:
                cv2.rectangle(img, (x_coord, y_coord),
                              (x_coord+width, y_coord+height),
                              (255, 0, 0), 2
                             )
                #roi_gray = gray[y:y+h, x_coord:x_coord+w]
                #roi_color = img[y:y+h, x_coord:x_coord+w]

    def follow(self, img):
        '''From an image, calculates and carries out what steps should be taken
        (adjust servo pan and tilt, or rotating the entire robot)
        in order to follow the face in the image'''
        if not self.found_face:
            return

        x_coord, y_coord, width, height = img
        center = (x_coord+width/2, y_coord+height/2)

        if center[0] > self.edge_tolerances[1]:
            self.edge_right()
        elif center[0] < self.edge_tolerances[0]:
            self.edge_left()
        elif center[0] > self.center_tolerances[1] and self.pan_angle <= self.right_pan_limit:
            self.pan_servo(self.pan_angle + self.angle_step)
        elif center[0] < self.center_tolerances[3] and self.pan_angle >= self.left_pan_limit:
            self.pan_servo(self.pan_angle - self.angle_step)

        if center[1] > self.center_tolerances[2] and self.title_angle >= self.bottom_tilt_limit:
            self.tilt_servo(self.title_angle - self.angle_step)
        elif center[1] > self.center_tolerances[0] and self.title_angle <= self.top_tilt_limit:
            self.tilt_servo(self.title_angle + self.angle_step)

        if width*height > 70000:
            self.backwards()
            sleep(0.75)
            self.stop()
        elif width*height < 60000:
            self.forwards()
            sleep(0.75)
            self.stop()

    def set_pixel(self, led_id, hue, brightness):
        '''Set one of the leds on the rover with a hue and brightness'''
        pixel_params = ["Pixel"]
        pixel_params.append(str(led_id))
        pixel_params.append(str(hue))
        pixel_params.append(str(brightness))
        pixel_params = ','.join(str(e) for e in pixel_params)
        self.sock.sendto(pixel_params, self.rover_addr)

    def pan_servo(self, angle):
        '''Pans the servo (left and right) holding the camera and ultrasonic sensor'''
        self.pan_angle = angle
        servo_params = ["ServoPan"]
        servo_params.append(angle)
        servo_params = ','.join(str(e) for e in servo_params)
        self.sock.sendto(servo_params, self.rover_addr)

    def set_grip(self, angle):
        '''Sets the servo controlling the gripper on the front of the rover'''
        servo_params = ["ServoGrip"]
        servo_params.append(angle)
        servo_params = ','.join(str(e) for e in servo_params)
        self.sock.sendto(servo_params, self.rover_addr)

    def tilt_servo(self, angle):
        '''Tilts the servo (up and down) holding the camera and ultrasonic sensor'''
        self.title_angle = angle
        servo_params = ["ServoTilt"]
        servo_params.append(angle)
        servo_params = ','.join(str(e) for e in servo_params)
        self.sock.sendto(servo_params, self.rover_addr)

    def set_leds(self, hue=0, brightness=0):
        '''Sets all leds on the rover with a hue and brightness'''
        for i in range(14):

            self.set_pixel(i, hue, brightness)

            self.set_pixel(i+14, hue, brightness)

            sleep(0.05)

    def toggle_led(self):
        '''Toggles the 5th LED. We don't need this'''
        self.set_pixel(5, 50, self.led_toggle)
        self.led_toggle = 1-self.led_toggle

    def get_sensor_data(self):
        '''Gets all sensory data from the rover (other than images)'''
        self.sock.sendto("Sensors", self.rover_addr)
        data, _ = self.sock.recvfrom(4096)
        return [float(info) for info in data.split(",")]

    def get_floor_data(self, sensor):
        '''Gets the floor sensors data'''
        values = self.get_sensor_data()
        return (values[sensor*2] + values[sensor*2+1])/2

    def get_distance_data(self):
        '''Gets the distance sensor data'''
        values = self.get_sensor_data()
        return values[6]

    def get_object_distance(self, real, perceived):
        '''Returns the distance of an object, given a real measurement of the object
        and a perceived measurement. This is done as the ratio of the size of the object
        in real life to the perceived size is the same as the ratio of the distance it is
        from the camera to the camera's focal length. This is not too acurate, but good enough'''
        return ((real * 3600) / perceived)/(1920/self.dims[0])

    def get_colors(self, img, debug=False):
        '''Returns all significant objects of colors specified in
        thresholds.json as an array of tuples (color, contour)'''

        logging.info("GETTING COLORS")
        t = time.time()
        if isinstance(img, str):
            img = cv2.imread(img)
        else:
            img = np.array(img)
        logging.info("Read image in %ss", time.time()-t)

        t = time.time()
        
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        logging.warning("Converted image to hsv in %ss", time.time()-t)
        colors = []

        for color, threshs in self.thresholds.items():
            t = time.time()
            masks = []
            for thresh in threshs:
                lower = np.array(thresh[0])
                upper = np.array(thresh[1])
                masks.append(cv2.inRange(img_hsv, lower, upper))
            mask = sum(masks)
            

            logging.warning("Created masks for %s in %ss", color, time.time()-t)

            t = time.time()
            
            kernel_open = np.ones((5, 5))
            kernel_close = np.ones((20, 20))
            mask_open = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
            mask_close = cv2.morphologyEx(mask_open, cv2.MORPH_CLOSE, kernel_close)

            

            logging.warning("Simplified masks heavily in %ss", time.time()-t)
            t = time.time()

            _, contours, _ = cv2.findContours(mask_close.copy(),
                                              cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE
                                             )
            
            
            
            logging.warning("Found contours in %ss", time.time()-t)

            if contours == []:
                continue
            else:
                
                contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(contour) < (self.dims[0]/10)**2:
                    continue
                
                logging.info("Found largest contour")
                t = time.time()
                
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.04*perimeter, True)
                logging.warning("Simplified contour heavily in %ss", time.time()-t)
                colors.append((color, contour))

            if debug:
                cv2.drawContours(img, [approx], -1, (0, 255, 0), 5)
            
        if debug:
            cv2.namedWindow(color)
            cv2.moveWindow(color, 40, 30)
            cv2.imshow(color, img)
            cv2.waitKey(1000)

        return colors

    def get_objects(self):
        '''Scans the landscape, taking note of any object of specified colors
        (see thresholds.json). It returns a list of how far away
        on the x and y axis each object is'''

        logging.warning("GETTING OBJECTS")
        
        self.set_leds(0, 0)
        self.pan_servo(0)
        self.tilt_servo(20)
        sleep(1)
        logging.info("Prepared for scanning")

        objects = {}

        for theta in range(self.left_pan_limit, self.right_pan_limit, 7):
            t = time.time()
            self.pan_servo(theta)
            sleep(0.05)
            logging.info("Panned servo 2 degrees in %ss", time.time()-t)

            img = self.get_image()
            cv2.imwrite("t.jpg", img)
            
            colors = self.get_colors(img, self.debug)
            if colors == []:
                
                continue
            
            for color, contour in colors:
                if 250 < cv2.minAreaRect(contour)[0][0] < 430:
                    if color == "RED":
                        self.set_leds(hue=0, brightness=100)
                    elif color == "BLUE":
                        self.set_leds(hue=180, brightness=100)
                    t = time.time()
                    object_size = Rover.OBJECT_SIZES[color]
                    perceived_width = cv2.minAreaRect(contour)[1][0]
                    hypotenuse = self.get_object_distance(object_size, perceived_width)
                    opposite = int(math.sin(math.radians(theta))*hypotenuse)
                    adjacent = int(math.cos(math.radians(theta))*hypotenuse)
                    print("{} obj sighted".format(color))
                    logging.info("Calculated distance and co-ordinates of %s object in %ss", color, time.time()-t)
                    objects[color] = (self.coords[0]+opposite, self.coords[1]+adjacent, theta)
                
                    
        self.pan_servo(0)
        self.set_leds(hue=0, brightness=0)
        return objects
