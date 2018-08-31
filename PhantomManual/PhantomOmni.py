import threading
import subprocess
import Queue
from time import time

class PhantomOmni():
    def __init__(self, mode="plane"):
        self.mode = mode
        self.dataThread = threading.Thread(target=self.getData)
        self.dataThread.setDaemon(True)

        self.dataThread.start()
        self.q = Queue.Queue()

    def run_commands(self, command):
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        return proc_stdout

    def getData(self):
        if self.mode == "plane":
            proc = subprocess.Popen(["cd /home/robot/Downloads/openhaptics_3.4-0-developer-edition-amd64/opt/OpenHaptics/Developer/3.4-0/examples/HD/console/FrictionlessPlane/;./FrictionlessPlane"], stdout=subprocess.PIPE, shell=True)
        elif self.mode == "forces":
            proc = subprocess.Popen(["cd /home/robot/Downloads/openhaptics_3.4-0-developer-edition-amd64/opt/OpenHaptics/Developer/3.4-0/examples/HD/console/forcespls/;./FrictionlessPlane"], stdout=subprocess.PIPE, shell=True)
        elif self.mode == "mouse":
            proc = subprocess.Popen(["cd /home/robot/Downloads/openhaptics_3.4-0-developer-edition-amd64/opt/OpenHaptics/Developer/3.4-0/examples/HD/console/mouse/;./FrictionlessPlane"], stdout=subprocess.PIPE, shell=True)


        for stdout_line in iter(proc.stdout.readline, ""):
            self.q.put(stdout_line, block=False)

    def send_command(self, command):
        with open("/home/robot/Documents/yeet.txt", "w") as f:
            f.write(command)

    @property
    def coords(self):
        data = 0
        while True:
            try:
                t = time()
                data = self.q.get(block=False)
                x = time()-t
            except Queue.Empty:
                if data != 0:
                    break
                else:
                    pass
                    #print("caught up to queue")
        '''
        while True:
            try:
                with open("/home/robot/Documents/yeet.txt", "r") as f:
                    data = f.read()
                print(data)
                parts = data.replace("\n", "").split(":")
                x = float(parts[0][1:])
                y = float(parts[1][1:])
                z = float(parts[2][1:])
                b1 = int(parts[3])
                b2 = int(parts[4])
                return (x, y, z, b1, b2)
            except ValueError:
                pass
        '''
        parts = data.replace("\n", "").split(":")
        x = float(parts[0][1:])
        y = float(parts[1][1:])
        z = float(parts[2][1:])
        b1 = int(parts[3])
        b2 = int(parts[4])
        return (x, y, z, b1, b2)

    @property
    def x(self):
        coords = self.coords
        return coords[0]
    
    @property
    def y(self):
        coords = self.coords
        return coords[1]
    
    @property
    def z(self):
        coords = self.coords
        return coords[2]
    
    def ink(self):
        coords = self.coords
        if -1 < coords[0] < 1 and -66.5 < coords[1] < -64.5 and -88.5 < coords[2] < -87.5:
            return True
        return False

    def jolt(self):
        self.send_command("J")