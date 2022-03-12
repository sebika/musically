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
    SIDEBAR_PIANO_WIDTH_PERCENT,
    COLOR_PALETTE,
    MIN_ZOOM,
    MAX_ZOOM
)
from random import randint, choice
from note import SidebarNote


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

        print(self.zoomLevel)
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



class PianoNoteSidebar(Canvas):
    def __init__(self, parent):
        parent.update()
        self.width = SIDEBAR_PIANO_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = SIDEBAR_PIANO_HEIGHT_PERCENT / 100 * parent.winfo_height()
        self.gridX = CANVAS_GRID_X - 1
        self.gridY = CANVAS_GRID_Y - 1
        self.notes = []

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
        h = NOTE_THICKNESS
        offset = 0

        for i in range(10, -1, -1):
            # Tones
            B = SidebarNote(0, offset, self.width, offset + h*1.5, COLOR_PALETTE['mint_cream'], f'B{i}', self)
            A = SidebarNote(0, offset + h*1.5, self.width, offset + h*3.5, COLOR_PALETTE['mint_cream'], f'A{i}', self)
            G = SidebarNote(0, offset + h*3.5, self.width, offset + h*5.5, COLOR_PALETTE['mint_cream'], f'G{i}', self)
            F = SidebarNote(0, offset + h*5.5, self.width, offset + h*7, COLOR_PALETTE['mint_cream'], f'F{i}', self)
            E = SidebarNote(0, offset + h*7, self.width, offset + h*8.5, COLOR_PALETTE['mint_cream'], f'E{i}', self)
            D = SidebarNote(0, offset + h*8.5, self.width, offset + h*10.5, COLOR_PALETTE['mint_cream'], f'D{i}', self)
            C = SidebarNote(0, offset + h*10.5, self.width, offset + h*12, COLOR_PALETTE['aero_blue'], f'C{i}', self, True)

            # Semitones
            A_sharp = SidebarNote(0, offset + h, self.width*0.75, offset + h*2, COLOR_PALETTE['black_coral'], f'A#{i}', self)
            G_sharp = SidebarNote(0, offset + h*3, self.width*0.75, offset + h*4, COLOR_PALETTE['black_coral'], f'A#{i}', self)
            F_sharp = SidebarNote(0, offset + h*5, self.width*0.75, offset + h*6, COLOR_PALETTE['black_coral'], f'A#{i}', self)
            D_sharp = SidebarNote(0, offset + h*8, self.width*0.75, offset + h*9, COLOR_PALETTE['black_coral'], f'A#{i}', self)
            C_sharp = SidebarNote(0, offset + h*10, self.width*0.75, offset + h*11, COLOR_PALETTE['black_coral'], f'A#{i}', self)

            self.notes += [B, A_sharp, A, G_sharp, G, F_sharp, F, E, D_sharp, D, C_sharp, C]

            offset += 12*h

        # Here I want to keep the notes in this order: C0, C#0, D0, ..., A10, A#10
        self.notes.reverse()


    def updateSize(self, event, parent):
        parent.update()
        self.width = SIDEBAR_PIANO_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = SIDEBAR_PIANO_HEIGHT_PERCENT / 100 * parent.winfo_height()

        # Here are the real widths of the notes
        for note in self.notes:
            note.width = self.width - 2
            if note.pitch.find('#') != -1:
                note.width *= 0.65

            self.coords(note.id, note.x, note.y, note.width, note.height)
            if note.textId:
                self.coords(note.textId, (note.x + note.width) - 11, (note.y + note.height) // 2)

        self.configure(scrollregion=self.bbox('all'))

        self.config(width=self.width, height=self.height)
