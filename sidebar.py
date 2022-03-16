from cgitb import text
from tkinter import CENTER, BooleanVar, Button, Canvas, Checkbutton, Frame, PhotoImage, Radiobutton, StringVar, IntVar
from constants import (
    CANVAS_GRID_X,
    CANVAS_GRID_Y,
    NOTE_THICKNESS,
    ROOT_INITIAL_HEIGHT,
    SIDEBAR_PIANO_HEIGHT_PERCENT,
    SIDEBAR_PIANO_WIDTH_PERCENT,
    COLOR_PALETTE,
    ROOT_INITIAL_WIDTH,
    SIDEBAR_PIANO_WIDTH_PERCENT,
    MUSIC_PLAYER_WIDTH_PERCENT,
    MUSIC_PLAYER_HEIGHT_PERCENT,
    TRACKS_SIDEBAR_WIDTH_PERCENT,
    TRACKS_SIDEBAR_HEIGHT_PERCENT
)
from note import SidebarNote

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
            G_sharp = SidebarNote(0, offset + h*3, self.width*0.75, offset + h*4, COLOR_PALETTE['black_coral'], f'G#{i}', self)
            F_sharp = SidebarNote(0, offset + h*5, self.width*0.75, offset + h*6, COLOR_PALETTE['black_coral'], f'F#{i}', self)
            D_sharp = SidebarNote(0, offset + h*8, self.width*0.75, offset + h*9, COLOR_PALETTE['black_coral'], f'D#{i}', self)
            C_sharp = SidebarNote(0, offset + h*10, self.width*0.75, offset + h*11, COLOR_PALETTE['black_coral'], f'C#{i}', self)

            self.notes += [B, A_sharp, A, G_sharp, G, F_sharp, F, E, D_sharp, D, C_sharp, C]

            offset += 12*h

        # Here I want to keep the notes in this order: C0, C#0, D0, ..., A10, A#10
        self.notes.reverse()

        self.note_to_int = {}
        for i, note in enumerate(self.notes):
            self.note_to_int[note.pitch] = i


    def updateSize(self, event, parent):
        parent.update()
        self.width = SIDEBAR_PIANO_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = SIDEBAR_PIANO_HEIGHT_PERCENT / 100 * parent.winfo_height()

        # Here are the real widths of the notes
        for note in self.notes:
            note.width = self.width - 2
            if note.pitch.find('#') != -1:
                note.width *= 0.65

            self.coords(note.id, note.x-1, note.y, note.width, note.height)
            if note.textId:
                self.coords(note.textId, (note.x + note.width) - 11, (note.y + note.height) // 2)

        self.configure(scrollregion=self.bbox('all'))

        self.config(width=self.width, height=self.height)


class MusicPlayer(Frame):
    def __init__(self, parent):
        parent.update()
        self.width = ROOT_INITIAL_WIDTH * MUSIC_PLAYER_WIDTH_PERCENT / 100
        self.height = ROOT_INITIAL_HEIGHT * MUSIC_PLAYER_HEIGHT_PERCENT / 100

        super(MusicPlayer, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            background='white',
        )

        self.backward_image = PhotoImage(file='resources/images/backward.png').subsample(5)
        self.backward_button = Button(self, image=self.backward_image, borderwidth=0)
        self.backward_button.place(relx=0.45, rely=0.5, anchor=CENTER)

        self.play_image = PhotoImage(file='resources/images/play.png').subsample(5)
        self.play_button = Button(self, image=self.play_image, borderwidth=0)
        self.play_button.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.forward_image = PhotoImage(file='resources/images/forward.png').subsample(5)
        self.forward_button = Button(self, image=self.forward_image, borderwidth=0)
        self.forward_button.place(relx=0.55, rely=0.5, anchor=CENTER)

        self.stop_image = PhotoImage(file='resources/images/stop.png').subsample(5)
        self.stop_button = Button(self, image=self.stop_image, borderwidth=0)
        self.stop_button.place(relx=0.975, rely=0.5, anchor=CENTER)

        self.grid(row=0, column=1, columnspan=3, sticky='w')

    def updateSize(self, event, parent):
        parent.update()
        self.width = MUSIC_PLAYER_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = MUSIC_PLAYER_HEIGHT_PERCENT / 100 * parent.winfo_height()

        self.config(width=self.width, height=self.height)


class TrackSidebar(Frame):
    def __init__(self, parent):
        parent.update()
        self.width = ROOT_INITIAL_WIDTH * TRACKS_SIDEBAR_WIDTH_PERCENT / 100
        self.height = ROOT_INITIAL_HEIGHT * TRACKS_SIDEBAR_HEIGHT_PERCENT / 100

        super(TrackSidebar, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            background='lightgray',
        )


        self.selected = BooleanVar(value=False)

        self.cb = Button(
            self,
            text="Mute ON",
            bg='green',
            activebackground='green',
            command=self.change
        )
        self.cb.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.grid(row=1, column=0, rowspan=2, stick='S')

    def change(self):
        self.selected.set(not self.selected.get())
        if self.selected.get():
            self.cb['text'] = 'Mute OFF'
            self.cb['bg'] = 'red'
            self.cb['activebackground'] = 'red'
            #cb['highlightbackground'] = 'red'
        else:
            self.cb['text'] = 'Mute ON'
            self.cb['bg'] = 'green'
            self.cb['activebackground'] = 'green'
            #cb['highlightbackground'] = 'green'

    def updateSize(self, event, parent):
        parent.update()
        self.width = TRACKS_SIDEBAR_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = TRACKS_SIDEBAR_HEIGHT_PERCENT / 100 * parent.winfo_height()

        self.config(width=self.width, height=self.height)
