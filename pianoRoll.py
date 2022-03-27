import tkinter as tk
from tkinter import Canvas
from turtle import width
from constants import (
    PIANO_ROLL_HEIGHT_PERCENT,
    PIANO_ROLL_WIDTH_PERCENT,
    CANVAS_GRID_X,
    CANVAS_GRID_Y,
    NOTE_THICKNESS,
    COLOR_PALETTE,
    MIN_ZOOM,
    MAX_ZOOM,
    TRACKS_PATELLTE
)


class PianoRoll(Canvas):
    def __init__(self, parent, sidebar, tracks=None):
        parent.update()
        self.parent = parent
        self.sidebar = sidebar
        self.tracks = tracks
        self.width = PIANO_ROLL_WIDTH_PERCENT / 100 * parent.winfo_width()
        self.height = PIANO_ROLL_HEIGHT_PERCENT / 100 * parent.winfo_height()
        self.gridX = CANVAS_GRID_X
        self.gridY = CANVAS_GRID_Y
        self.timestamp_x = 0
        self.zoomLevel = 1

        super(PianoRoll, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            bg='#34444e',
            highlightthickness=1,
            highlightbackground='black'
        )

        self.draw(self.tracks)
        self.grid(row=self.gridX, column=self.gridY)


    def draw(self, tracks=None):
        if tracks:
            for i, track in enumerate(tracks):
                for note in track.notes:
                    note_y = self.get_note_height(note[0])
                    note_start = note[1]
                    note_end = note[2]

                    self.create_rectangle(
                        note_start, note_y,
                        note_end, note_y + NOTE_THICKNESS,
                        fill=track.color,
                        activefill='lightgray',
                        tags=f'track_{i}',
                    )
        self.timestamp = self.create_rectangle(
            self.timestamp_x, 0, 5, self.get_note_height(0)+NOTE_THICKNESS, fill='red', tags='timestamp'
        )


    def play_song(self):
        app = self.parent.parent
        if self.parent.parent.musicPlayer.is_playing and app.seconds_elapsed < app.length_in_seconds:
            for i, note_index in enumerate(app.note_index_to_play):
                # Add new notes that are being played
                while note_index < len(app.tracks[i].notes):
                    note, start, end = app.tracks[i].notes[note_index]
                    start *= app.tick_to_track
                    end *= app.tick_to_track
                    if start <= app.seconds_elapsed and app.seconds_elapsed < end:
                        app.current_notes[i].append([note, start, end])
                        sidebar_note = self.sidebar.notes[note]
                        self.sidebar.itemconfig(sidebar_note.id, fill=sidebar_note.activefill)
                        self.sidebar.activeNotes[note] += 1
                        # print(f'Track {i}, note: {note_index} -> {note} {start} {end} | {app.seconds_elapsed}')
                        note_index += 1
                    else:
                        break
                app.note_index_to_play[i] = note_index

                # Remove notes that finished playing
                for elem in app.current_notes[i]:
                    note, start, end = elem
                    if end < app.seconds_elapsed:
                        self.sidebar.activeNotes[note] -= 1
                        if self.sidebar.activeNotes[note] == 0:
                            sidebar_note = self.sidebar.notes[note]
                            self.sidebar.itemconfig(sidebar_note.id, fill=sidebar_note.color)

                        app.current_notes[i].remove(elem)
                        # print(f'Track {i}: {len(app.current_notes[i])}')


            self.timestamp_x += app.timestamp_speed
            self.move(self.timestamp, app.timestamp_speed, 0)
            app.seconds_elapsed += 1 / app.fps
            self.parent.after(int(1000 / app.fps), self.play_song)


    def stop_song(self):
        x1, y1, x2, y2 = self.coords(self.timestamp)
        self.timestamp_x = 0
        self.coords(self.timestamp, 0, 0, x2-x1, y2-y1)


    def configure_scrollbars(self, parent):
        self.bind('<Control-MouseWheel>', self._do_zoom)
        self.bind('<MouseWheel>', self._on_mousewheel)

        # self.bind('<ButtonPress-1>', lambda event: (
        #     self.scan_mark(event.x, event.y),
        #     self.sidebar.scan_mark(event.x, event.y),
        # ))
        # self.bind('<B1-Motion>', lambda event: (
        #     self.scan_dragto(event.x, event.y, gain=1),
        #     self.sidebar.scan_dragto(event.x, event.y, gain=1),
        # ))

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


    def get_note_height(self, note):
        height = self.sidebar.notes[note].y
        pitch = self.numeric_to_string_note(note)

        if pitch[0] in list('CDFGA') and pitch[1] != '#':
            height += NOTE_THICKNESS // 2

        return height


    def numeric_to_string_note(self, note):
        return self.sidebar.notes[note].pitch


    def string_to_numeric_note(self, note):
        return self.sidebar.note_to_int[note]


    def _do_zoom(self, event):
        app = self.parent.parent
        x = 0
        y = self.canvasy(event.y)
        factor = 1.001 ** event.delta

        if self.zoomLevel * factor > MIN_ZOOM or self.zoomLevel * factor > MAX_ZOOM:
            self.zoomLevel *= factor
            self.scale('all', x, y, factor, 1)

            x1, _, x2, _ = self.bbox('all')
            _, _, _, y2 = self.sidebar.bbox('all')
            self.configure(scrollregion=[x1, 0, x2, y2])
            app.timestamp_speed *= factor
            self.timestamp_x *= factor


    def _on_mousewheel(self, event):
        self.yview_scroll(int(-1*(event.delta/120)), 'units')
        self.sidebar.yview_scroll(int(-1*(event.delta/120)), 'units')


    def _vertical_scroll(self, *args):
        self.yview(*args)
        self.sidebar.yview(*args)
