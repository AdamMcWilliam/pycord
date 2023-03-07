from p5 import * 
def setup():
    createCanvas(400, 400); 

def draw():
    background(200); ellipse(200, 200, 100, 100); 
    save("result.png")