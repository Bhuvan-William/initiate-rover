
class Rover:
    def __init__(self, id):
        print("rover started")
        self.id = id
        self.reset()
    
    def updateData(self, left, right, duration):
        self.left = left
        self.right = right
        self.duration = duration
        
    def isMoving(self):
        if self.left != 0 and self.right != 0:
            return True
        return False
    
    def reset(self):
        self.left = 0
        self.right = 0
        self.duration = 0
        self.claw = 2
        self.lightPreset = 0
        self.lights = (0, 0)
    
    def setLights(self, hue, brightness):
        self.lights = (hue, brightness)

    def postData(self, reset=True):
        res = {
            "roverid": self.id,
            "left": self.left,
            "right": self.right,
            "duration": self.duration,
            "claw": self.claw,
            "lightPreset" : self.lightPreset,
            "lights" : self.lights
        }
        if reset:
            self.reset()

        return res