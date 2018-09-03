from PhantomOmni import PhantomOmni
from time import sleep

text = raw_input("What do you want to write?")
arm = PhantomOmni("gravity")

STARTX = -81
RECORDX = -11
mod = STARTX - RECORDX

def coords_to_write(move):
    a = []
    for x in move:
        if str(x)[0] != "-":
            x = "+"+str(x)
        x = str(x).ljust(8, "0")
        a.append(x)
    
    return "{}|{}|{}\n".format(a[0], a[1], a[2])

def write_to_coords(txt):
    txt = txt.replace("\n", "").split("|")
    
    return [float(x) for x in txt]

try:
    for n, char in enumerate(text):
        file = "letters/{}.txt".format(char)
        with open(file, "r") as f:
            coords = f.read().split("\n")[:-1]
        
        
        
        
        x = 0
        print("HNGGGGGGGG")
        for line in coords:
            numbers = write_to_coords(line)
            
            numbers[0] += mod
            print(coords_to_write(numbers))
            
            with open("/home/robot/Documents/yeet.txt", "w") as f:
                f.write(coords_to_write(numbers))
            if x == 0:
                sleep(1)
            else:
                sleep(0.003)
            
            x += 1
        mod += 30
except KeyboardInterrupt:
    arm.kill()
arm.kill()