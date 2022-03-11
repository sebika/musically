from cgitb import text
import tkinter as tk
from tkinter import Canvas, Label
from constants import (
    PIANO_ROLL_HEIGHT_PERCENT,
    PIANO_ROLL_WIDTH_PERCENT,
    CANVAS_GRID_X,
    CANVAS_GRID_Y,
    NOTE_THICKNESS,
    SIDEBAR_PIANO_HEIGHT_PERCENT,
    SIDEBAR_PIANO_WIDTH_PERCENT
)
from random import randint, choice


class PianoRoll(Canvas):
    def __init__(self, parent):
        parent.update()
        self.width = PIANO_ROLL_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = PIANO_ROLL_HEIGHT_PERCENT / 100 * parent.winfo_height()
        self.gridX = CANVAS_GRID_X
        self.gridY = CANVAS_GRID_Y

        super(PianoRoll, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            bg='white',
            highlightthickness=0
        )

        self.draw()
        self.grid(row=self.gridX, column=self.gridY)


    def draw(self):
        for i in range(20):
            y = randint(0, 10)*100
            self.create_rectangle(100*i, y, 100+100*i, y + NOTE_THICKNESS, fill=choice(['red', 'blue', 'pink', 'orange', 'yellow']), tags='note')


    def configure_scrollbars(self, parent, sidebar):
        self.sidebar = sidebar
        self.bind('<Control-MouseWheel>', self._do_zoom)
        self.bind("<MouseWheel>", self._on_mousewheel)

        # self.bind('<ButtonPress-1>', lambda event: self.scan_mark(event.x, event.y))
        # self.bind('<B1-Motion>', lambda event: self.scan_dragto(event.x, event.y, gain=1))

        self.scroll_x = tk.Scrollbar(parent, orient='horizontal', command=self.xview)
        self.scroll_x.grid(row=self.gridX-1, column=self.gridY, sticky='ew', columnspan=2)

        self.scroll_y = tk.Scrollbar(parent, orient='vertical', command=self._vertical_scroll)
        self.scroll_y.grid(row=self.gridX, column=self.gridY+1, sticky='ns')

        self.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        _, _, _, y2 = sidebar.bbox('all')
        sidebar.configure(scrollregion=sidebar.bbox('all'))

        _, _, x2, _ = self.bbox('all')
        self.configure(scrollregion=[0, 0, x2, y2])


    def updateSize(self, event, parent):
        parent.update()
        self.width = PIANO_ROLL_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = PIANO_ROLL_HEIGHT_PERCENT / 100 * parent.winfo_height()

        self.config(width=self.width, height=self.height)

    def _do_zoom(self, event,):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        factor = 1.001 ** event.delta

        self.scale('all', x, y, factor, 1)

        x1, y1, x2, _ = self.bbox('all')
        _, _, _, y2 = self.sidebar.bbox('all')
        self.configure(scrollregion=[x1, y1, x2, y2])

    def _on_mousewheel(self, event):
        self.yview_scroll(int(-1*(event.delta/120)), 'units')
        self.sidebar.yview_scroll(int(-1*(event.delta/120)), 'units')


    def _vertical_scroll(self, *args):
        self.yview(*args)
        self.sidebar.yview(*args)



class PianoNoteSidebar(Canvas):
    def __init__(self, parent):
        parent.update()
        self.width = SIDEBAR_PIANO_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = SIDEBAR_PIANO_HEIGHT_PERCENT / 100 * parent.winfo_height()
        self.gridX = CANVAS_GRID_X - 1
        self.gridY = CANVAS_GRID_Y - 1
        self.items = []

        super(PianoNoteSidebar, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            bg='white',
            highlightthickness=0
        )

        self.draw()
        self.grid(row=self.gridX, column=self.gridY, rowspan=2, sticky='s')


    def draw(self):
        col = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']

        for i in range(80):
            # Label(self, text=str(i)).place(x=10, y=i*NOTE_THICKNESS*1.5+5)
            self.items.append(self.create_rectangle(0, i*NOTE_THICKNESS*1.5, self.width, (i+1)*NOTE_THICKNESS*1.5, fill=col[i%7]))


    def updateSize(self, event, parent):
        parent.update()
        self.width = SIDEBAR_PIANO_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = SIDEBAR_PIANO_HEIGHT_PERCENT / 100 * parent.winfo_height()

        for item in self.items:
            x0, y0, x1, y1 = self.coords(item)
            self.coords(item, x0, y0, self.width-1, y1)

        self.config(width=self.width, height=self.height)
