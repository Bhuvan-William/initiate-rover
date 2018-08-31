from PhantomOmni import PhantomOmni
from time import sleep
from tqdm import tqdm
import sys

filename = "/home/robot/Documents/save.txt"
if len(sys.argv) > 1:
    filename = sys.argv[1]

arm = PhantomOmni("gravity")
x = 0

#opens the save file to read coords from
with open(filename, "r") as f:
    #writes every coordinate set to a file which the c script reads from and moves to,
    #giving a longer wait time for the first move as it will be the largest jump
    for line in f.read().split("\n"):
        with open("/home/robot/Documents/yeet.txt", "w") as f:
            f.write(line)
        if x == 0:
            sleep(3)
        else:
            sleep(0.003)
        x += 1
            
arm.kill()