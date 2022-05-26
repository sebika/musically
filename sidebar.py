from tkinter import CENTER, BooleanVar, Button, Canvas, PhotoImage, messagebox
from tkinter.colorchooser import askcolor
from constants import (
    CANVAS_GRID_X,
    CANVAS_GRID_Y,
    NOTE_THICKNESS,
    PLAYING_FILE_EXTENSION,
    ROOT_INITIAL_HEIGHT,
    SIDEBAR_PIANO_HEIGHT_PERCENT,
    SIDEBAR_PIANO_WIDTH_PERCENT,
    COLOR_PALETTE,
    ROOT_INITIAL_WIDTH,
    SIDEBAR_PIANO_WIDTH_PERCENT,
    MUSIC_PLAYER_WIDTH_PERCENT,
    MUSIC_PLAYER_HEIGHT_PERCENT,
    SOLFEGE,
    TRACKS_SIDEBAR_HEIGHT_PERCENT,
    TRACKS_SIDEBAR_WIDTH_PERCENT,
)
import pygame

class PianoNoteSidebar(Canvas):
    def __init__(self, parent):
        parent.update()
        self.width = SIDEBAR_PIANO_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = SIDEBAR_PIANO_HEIGHT_PERCENT / 100 * parent.winfo_height()
        self.gridX = CANVAS_GRID_X - 1
        self.gridY = CANVAS_GRID_Y - 1
        self.notes = []
        self.activeNotes = []

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
            A_sharp = SidebarNote(0, offset + h, self.width*0.75, offset + h*2, COLOR_PALETTE['space_cadet'], f'A#{i}', self)
            G_sharp = SidebarNote(0, offset + h*3, self.width*0.75, offset + h*4, COLOR_PALETTE['space_cadet'], f'G#{i}', self)
            F_sharp = SidebarNote(0, offset + h*5, self.width*0.75, offset + h*6, COLOR_PALETTE['space_cadet'], f'F#{i}', self)
            D_sharp = SidebarNote(0, offset + h*8, self.width*0.75, offset + h*9, COLOR_PALETTE['space_cadet'], f'D#{i}', self)
            C_sharp = SidebarNote(0, offset + h*10, self.width*0.75, offset + h*11, COLOR_PALETTE['space_cadet'], f'C#{i}', self)

            self.notes += [B, A_sharp, A, G_sharp, G, F_sharp, F, E, D_sharp, D, C_sharp, C]
            self.activeNotes += [0] * 12

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


class SidebarNote():
    def __init__(self, x, y, width, height, color, pitch, canvas, addNoteText=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.pitch = pitch
        self.classic_pitch = SOLFEGE[list(self.pitch)[0]]
        self.id = canvas.create_rectangle(x, y, width, height, fill=color)
        self.textId = None

        if addNoteText:
            self.textId = canvas.create_text(0, 0, text=self.pitch)


        self.activefill = COLOR_PALETTE['blue_gray']
        canvas.itemconfig(self.id, activefill=self.activefill)


class MusicPlayer(Canvas):
    def __init__(self, parent):
        parent.update()
        self.width = ROOT_INITIAL_WIDTH * MUSIC_PLAYER_WIDTH_PERCENT / 100
        self.height = ROOT_INITIAL_HEIGHT * MUSIC_PLAYER_HEIGHT_PERCENT / 100
        self.parent = parent

        super(MusicPlayer, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            background=COLOR_PALETTE['black_coral'],
            highlightthickness=0
        )

        self.play_image = PhotoImage(file='resources/images/play.png').subsample(5)
        self.pause_image = PhotoImage(file='resources/images/pause.png').subsample(5)
        self.is_playing = None
        self.play_button = Button(
            self, image=self.play_image, borderwidth=0, highlightthickness=0,
            command=lambda: self.play_song(None)
        )
        self.play_button.place(relx=0.1, rely=0.5, anchor=CENTER)


        self.stop_image = PhotoImage(file='resources/images/stop.png').subsample(5)
        self.stop_button = Button(
            self, image=self.stop_image, borderwidth=0, highlightthickness=0,
            command=lambda: self.stop_song(None)
        )
        self.stop_button.place(relx=0.150, rely=0.5, anchor=CENTER)

        self.volume_on = PhotoImage(file='resources/images/volume_on.png').subsample(5)
        self.volume_off = PhotoImage(file='resources/images/volume_off.png').subsample(5)
        self.is_volume_on = True
        self.volume_button = Button(
            self, image=self.volume_on, borderwidth=0, highlightthickness=0,
            command=lambda: self.mute_unmute(None)
        )
        self.volume_button.place(relx=0.2, rely=0.5, anchor=CENTER)

        self.grid(row=0, column=1, columnspan=3, sticky='w')


    def mute_unmute(self, event):
        app = self.parent.parent
        if app.root.filename:
            self.is_volume_on = not self.is_volume_on
            if self.is_volume_on:
                self.volume_button.configure(image=self.volume_on)
                pygame.mixer.music.set_volume(1)
            else:
                self.volume_button.configure(image=self.volume_off)
                pygame.mixer.music.set_volume(0)
        else:
            messagebox.showerror(
                title='Music player error',
                message='You need to Open a midi file before trying to mute a song'
            )


    def play_song(self, event):
        app = self.parent.parent
        if app.root.filename:
            if self.is_playing == None:
                self.is_playing = True
                self.play_button.configure(image=self.pause_image)
                song_name = app.root.filename.split('.')[0] + PLAYING_FILE_EXTENSION

                pygame.mixer.music.load(song_name)
                pygame.mixer.music.play()
                app.canvas.play_song()
            else:
                self.is_playing = not self.is_playing

                if self.is_playing:
                    self.play_button.configure(image=self.pause_image)
                    pygame.mixer.music.unpause()
                    app.canvas.play_song()
                else:
                    self.play_button.configure(image=self.play_image)
                    pygame.mixer.music.pause()
        else:
            messagebox.showerror(
                title='Music player error',
                message='You need to Open a midi file before trying to play it'
            )


    def stop_song(self, event):
        app = self.parent.parent
        if app.root.filename:
            self.is_playing = None
            self.play_button.configure(image=self.play_image)
            pygame.mixer.music.stop()
            app.seconds_elapsed = 0
            app.init_current_playing_notes()
            app.init_sidebar_notes()
            app.init_canvas_notes()
            app.canvas.stop_song()
        else:
            messagebox.showerror(
                title='Music player error',
                message='You need to Open a midi file before trying to stop a song'
            )


    def updateSize(self, event, parent):
        parent.update()
        self.width = MUSIC_PLAYER_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = MUSIC_PLAYER_HEIGHT_PERCENT / 100 * parent.winfo_height()

        self.config(width=self.width, height=self.height)


class TrackSidebar(Canvas):
    def __init__(self, parent):
        parent.update()
        self.parent = parent
        self.width = ROOT_INITIAL_WIDTH * TRACKS_SIDEBAR_WIDTH_PERCENT / 100
        self.height = ROOT_INITIAL_HEIGHT * TRACKS_SIDEBAR_HEIGHT_PERCENT / 100
        self.color_picker_image = PhotoImage(file='resources/images/color_picker.png').subsample(9)

        super(TrackSidebar, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            background=COLOR_PALETTE['black_coral'],
            highlightthickness=0,
        )
        self.buttons = []
        self.color_picker_buttons = []
        self.grid(row=1, column=0, rowspan=2, stick='S')

    def draw(self, track_names):
        if self.parent.parent.root.filename:
            for button in self.buttons:
                button.destroy()
            self.buttons = []
            for button in self.color_picker_buttons:
                button.destroy()
            self.color_picker_buttons = []
            offset = 0
            for i, track_name in enumerate(track_names):
                self.buttons.append(TrackSidebarButton(self, track_name, offset, i))
                self.color_picker_buttons.append(ColorPickerTrackSidebarButton(
                    self, self.color_picker_image, offset, i
                ))
                offset += self.height // 6


    def updateSize(self, event, parent):
        parent.update()
        self.width = TRACKS_SIDEBAR_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = TRACKS_SIDEBAR_HEIGHT_PERCENT / 100 * parent.winfo_height()

        self.config(width=self.width, height=self.height)


class ColorPickerTrackSidebarButton(Button):
    def __init__(self, parent, image, offset, id):
        self.id = id
        self.parent = parent
        super(ColorPickerTrackSidebarButton, self).__init__(
            parent,
            image=image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.change_track_color(id)
        )
        self.place(relx=0.5, y=offset+60, anchor=CENTER)


    def change_track_color(self, track_index):
        app = self.parent.parent.parent
        hex_color = askcolor(title='Pick a color')[1]
        if hex_color:
            app.tracks[track_index].color = hex_color
            track_notes = list(app.canvas.find_withtag(f'track_{self.id}'))
            connected_track_notes = list(app.canvas.find_withtag(f'line_track_{track_index}'))

            if len(app.canvas.connected_line_id) > 0:
                for line in connected_track_notes:
                    app.canvas.itemconfigure(line, fill=hex_color)

            for note in track_notes:
                app.canvas.itemconfigure(note, fill=hex_color)

            self.parent.buttons[track_index].on_color = hex_color
            self.parent.buttons[track_index].update_color()


class TrackSidebarButton(Button):
    def __init__(self, parent, text, offset, id):
        self.parent = parent
        self.id = id
        self.selected = BooleanVar(value=True)
        self.on_color = COLOR_PALETTE['bitter_lime']

        self.canvas_id = super(TrackSidebarButton, self).__init__(
            parent,
            text=text,
            bg=self.on_color,
            activebackground =self.on_color,
            width=int(parent.width//15),
            height=int(parent.width//30),
            wraplength=45,
            command=self.change,
        )

        self.place(relx=0.5, y=30+offset, anchor=CENTER)
        self.y = 30+offset


    def update_color(self):
        tracks = self.parent.parent.parent.tracks
        if tracks and self.id < len(tracks):
            self.on_color = tracks[self.id].color
        self.off_color = 'lightgray'

        if self.selected.get():
            self.configure(bg=self.on_color, activebackground=self.on_color)
        else:
            self.configure(bg=self.off_color, activebackground=self.off_color)


    def change(self):
        canvas = self.parent.parent.parent.canvas
        track_notes = list(canvas.find_withtag(f'track_{self.id}'))
        connected_track_notes = list(canvas.find_withtag(f'line_track_{self.id}'))
        self.selected.set(not self.selected.get())
        if self.selected.get():
            self.configure(bg=self.on_color, activebackground=self.on_color)
            for line in connected_track_notes:
                canvas.itemconfigure(line, state='normal')
                canvas.tag_raise(line)
            for note in track_notes:
                canvas.itemconfigure(note, state='normal')
                canvas.tag_raise(note)
            canvas.tag_raise(canvas.timestamp)
        else:
            self.configure(bg=self.off_color, activebackground=self.off_color)
            for note in track_notes:
                canvas.itemconfigure(note, state='hidden')
            for line in connected_track_notes:
                canvas.itemconfigure(line, state='hidden')

class Track():
    def __init__(self, name, notes, color):
        self.name = name
        self.notes = notes
        self.color = color
