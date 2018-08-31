import threading
import subprocess
import Queue

class PhantomOmni():
    def __init__(self, plane=False):
        self.plane = plane
        self.dataThread = threading.Thread(target=self.getData)
        self.dataThread.setDaemon(True)

        self.dataThread.start()
        self.q = Queue.Queue()

    def run_commands(self, command):
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        return proc_stdout

    def getData(self):
        if self.plane:
            proc = subprocess.Popen(["cd /home/robot/Downloads/openhaptics_3.4-0-developer-edition-amd64/opt/OpenHaptics/Developer/3.4-0/examples/HD/console/FrictionlessPlane/;./FrictionlessPlane"], stdout=subprocess.PIPE, shell=True)
        else:
            proc = subprocess.Popen(["cd /home/robot/Downloads/openhaptics_3.4-0-developer-edition-amd64/opt/OpenHaptics/Developer/3.4-0/examples/HD/console/forcespls/;./FrictionlessPlane"], stdout=subprocess.PIPE, shell=True)
        #pipe = proc.stdout

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
                data = self.q.get(block=False)
            except Queue.Empty:
                if data != 0:
                    break

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