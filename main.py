from textwrap import fill
import tkinter as tk
import tkinter
from tkinter import messagebox

from mido import MidiFile
import pygame

from tkinter import *

width = 300
height = 300

def do_zoom(event):
    global width, height

    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    factor = 1.0005 ** event.delta

    if width * factor >= 299 and width * factor < 500:
        canvas.scale(ALL, x, y, factor, factor)
        canvas.configure(scrollregion=canvas.bbox("all"))

        width = width * factor
        height = height * factor
        print(width, height)
    else:
        print('cant scale anymore')


def update_l1(event):
    l1.config(text=f'W:{parent.winfo_width()} H:{parent.winfo_height()}')

parent = tk.Tk()
parent.bind('<Configure>', update_l1)
parent.geometry("500x500")

canvas_x = 1
canvas_y = 1

canvas = tk.Canvas(parent, width=width, height=height, bg='white')
canvas.bind("<MouseWheel>", do_zoom)
canvas.bind('<ButtonPress-1>', lambda event: canvas.scan_mark(event.x, event.y))
canvas.bind("<B1-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1))

canvas.create_oval(10, 10, 20, 20, fill="red")
canvas.create_oval(400, 400, 420, 420, fill="blue")
canvas.create_rectangle(600, 10, 640, 50)
canvas.grid(row=canvas_x+1, column=canvas_y)

scroll_x = tk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
scroll_x.grid(row=canvas_x, column=canvas_y, sticky="ew", columnspan=2)

scroll_y = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
scroll_y.grid(row=canvas_x+1, column=canvas_y+1, sticky="ns")

canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
canvas.configure(scrollregion=canvas.bbox("all"))

l1 = tk.Label(parent, text=f'aaaaaaaaaa')
l1.grid(row=0, column=0, columnspan=2)

l2 = tk.Label(parent, text='bbbb')
l2.grid(row=1, column=0, rowspan=2)

def helloCallBack():
    song = 'resources\VampireKillerCV1.mid'
    pygame.mixer.init()
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0)
    pygame.mixer.stop()

b = tk.Button(parent, text ="Hello", command = helloCallBack)
b.grid(row=2, column=3)


while True:
    parent.update()
