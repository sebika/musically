import tkinter as tk
from tkinter import Canvas
from constants import (
    PIANO_ROLL_HEIGHT_PERCENT,
    PIANO_ROLL_WIDTH_PERCENT,
    CANVAS_GRID_X,
    CANVAS_GRID_Y,
    NOTE_THICKNESS,
    COLOR_PALETTE,
    MIN_ZOOM,
    MAX_ZOOM
)
from random import randint, choice


class PianoRoll(Canvas):
    def __init__(self, parent, sidebar):
        parent.update()
        self.sidebar = sidebar
        self.width = PIANO_ROLL_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = PIANO_ROLL_HEIGHT_PERCENT / 100 * parent.winfo_height()
        self.gridX = CANVAS_GRID_X
        self.gridY = CANVAS_GRID_Y
        self.zoomLevel = 1

        super(PianoRoll, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            bg=COLOR_PALETTE['mint_cream'],
            highlightthickness=0
        )

        self.draw()
        self.grid(row=self.gridX, column=self.gridY)


    def draw(self):
        for i in range(20):
            y = randint(0, 10)*100
            self.create_rectangle(100*i, y, 100+100*i, y + NOTE_THICKNESS, fill=choice(['red', 'blue', 'pink', 'orange', 'yellow']), tags='note')


    def configure_scrollbars(self, parent):
        self.bind('<Control-MouseWheel>', self._do_zoom)
        self.bind("<MouseWheel>", self._on_mousewheel)

        # self.bind('<ButtonPress-1>', lambda event: self.scan_mark(event.x, event.y))
        # self.bind('<B1-Motion>', lambda event: self.scan_dragto(event.x, event.y, gain=1))

        self.scroll_x = tk.Scrollbar(parent, orient='horizontal', command=self.xview)
        self.scroll_x.grid(row=self.gridX-1, column=self.gridY, sticky='ew', columnspan=2)

        self.scroll_y = tk.Scrollbar(parent, orient='vertical', command=self._vertical_scroll)
        self.scroll_y.grid(row=self.gridX, column=self.gridY+1, sticky='ns')

        self.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        _, _, _, y2 = self.sidebar.bbox('all')
        self.sidebar.configure(scrollregion=self.sidebar.bbox('all'))

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

        if self.zoomLevel * factor > MIN_ZOOM and self.zoomLevel * factor < MAX_ZOOM:
            self.zoomLevel *= factor
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
