from Tkinter import *
import time

size = 32
gui_scale = 512/size

root = Tk()
root.title("Transpose")
root.resizable(0, 0)

frame = Frame(root, bd=5, relief=SUNKEN)
frame.pack()

canvas = Canvas(frame, width=gui_scale*size*2 + gui_scale, height=gui_scale*size, bd=0, highlightthickness=0)
canvas.pack()
root.update() # fix geometry
canvas.create_rectangle(0, 0, gui_scale*size*2 + gui_scale, gui_scale*size, fill="white")

for i in range(0, size):
    for j in range(0, size):
        canvas.create_rectangle(i*gui_scale, j*gui_scale, (i+1)*gui_scale, (j+1)*gui_scale)

for i in range(size + 1, 2*size + 1):
    for j in range(0, size):
        canvas.create_rectangle(i*gui_scale, j*gui_scale, (i+1)*gui_scale, (j+1)*gui_scale)

def update(d_i, d_j,op):
    if (op == "read"):
        canvas.create_rectangle(d_i*gui_scale, d_j*gui_scale, (d_i+1)*gui_scale, (d_j+1)*gui_scale, fill="green")
    else:
        canvas.create_rectangle((d_i+size+1)*gui_scale, d_j*gui_scale, (d_i+2+size)*gui_scale, (d_j+1)*gui_scale, fill="red")
    root.update_idletasks() # redraw
    root.update() # process events 

i = 0
j = 0

blocksize2 = 1
blocksize = 1

while j < size:
    i = 0
    while i < size:
        for jj in range(j, j+blocksize):
            for ii in range(i, i+blocksize):
                update(jj, ii, "read")
                update(ii, size - 1 - jj, "write")
                time.sleep(0.01)
        i = i + blocksize
    j = j + blocksize
'''
while i < size:
    j = 0
    while j < size:
        for ii in range(i, i+blocksize):
            for jj in range(j, j+blocksize2):
                update(jj, ii, "read")
                update(ii, size - 1 - jj, "write")
        j = j + blocksize2
    i = i + blocksize
'''

time.sleep(10)
