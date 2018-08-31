'''Lets you use the geomagic touch as a mouse'''
from PhantomOmni import PhantomOmni
import pyautogui
from subprocess import call

arm = PhantomOmni(mode="mouse")
while True:
    try:
        pass
    except KeyboardInterrupt:
        arm.kill()
        exit()