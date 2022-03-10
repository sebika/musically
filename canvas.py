import tkinter as tk
from tkinter import Canvas
from constants import (
    CANVAS_INITIAL_HEIGHT_PERCENT,
    CANVAS_INITIAL_WIDTH_PERCENT,
    CANVAS_GRID_X,
    CANVAS_GRID_Y,
)
from random import randint, choice


class MusicallyCanvas(Canvas):
    def __init__(self, parent):
        parent.update()
        self.width = CANVAS_INITIAL_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = CANVAS_INITIAL_HEIGHT_PERCENT / 100 * parent.winfo_height()
        self.gridX = CANVAS_GRID_X
        self.gridY = CANVAS_GRID_Y

        super(MusicallyCanvas, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            bg='white',
            highlightthickness=0
        )

        self.bind('<MouseWheel>', self.do_zoom)
        self.bind('<ButtonPress-1>', lambda event: self.scan_mark(event.x, event.y))
        self.bind('<B1-Motion>', lambda event: self.scan_dragto(event.x, event.y, gain=1))

        scroll_x = tk.Scrollbar(parent, orient='horizontal', command=self.xview)
        scroll_x.grid(row=self.gridX-1, column=self.gridY, sticky='ew', columnspan=2)

        scroll_y = tk.Scrollbar(parent, orient='vertical', command=self.yview)
        scroll_y.grid(row=self.gridX, column=self.gridY+1, sticky='ns')

        self.draw()

        self.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        x1, y1, x2, y2 = self.bbox('all')
        self.configure(scrollregion=[0, 0, x2, y2])
        self.grid(row=self.gridX, column=self.gridY)


    def draw(self):
        for i in range(20):
            y = randint(0, 4)*100
            self.create_rectangle(100+100*i, y, 200+100*i, y + 20, fill=choice(['red', 'blue', 'pink', 'orange', 'yellow']))


    def do_zoom(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        factor = 1.0005 ** event.delta

        self.scale('all', x, y, factor, factor)
        self.configure(scrollregion=self.bbox('all'))
        self.width = self.width * factor
        self.height = self.height * factor
        print(self.width, self.height)


    def updateSize(self, event, parent):
        parent.update()
        self.width = CANVAS_INITIAL_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = CANVAS_INITIAL_HEIGHT_PERCENT / 100 * parent.winfo_height()

        self.config(width=self.width, height=self.height)
