'''Allows you to control the Geomagic Touch using the gyroscope+arduino nano module'''
import sys

sys.path.append('..')

from PhantomOmni import PhantomOmni
from Misc.Gyro import Gyro
from Misc.utils import mapValues

arm = PhantomOmni("gravity")
gyro = Gyro()

#arm coordinate limits used for mapping
LIMITS = ((-220, 220), (-115, 220), (-125, 100))
coords = [0, 0, 0]

def send_position(coords):
    '''Writes coordinates to a file in a way which the c script can read easily and move to'''
    with open("/home/robot/Documents/yeet.txt", "w") as f:
        formatted = []
        for x in coords:
            if str(x)[0] != "-":
                x = "+"+str(x)
            x = str(x).ljust(8, "0")
            formatted.append(x)

        f.write("{}|{}|{}\n".format(formatted[0], formatted[1], formatted[2]))

while True:
    try:
        #map values from the gyroscope to coordinates for the arm to move to
        values = gyro.getValues()
        if values:
            coords[0] = round(
                mapValues(-values[0], -35, 35, LIMITS[0][0], LIMITS[0][1]), 3
            )
            coords[1] = round(
                mapValues(-values[2], -35, 35, LIMITS[1][0], LIMITS[1][1]), 3
            )
            print(coords)
            send_position(coords)

    except KeyboardInterrupt:
        break

arm.kill()