import tkinter as tk
from tkinter import Canvas, messagebox
from constants import (
    PIANO_ROLL_HEIGHT_PERCENT,
    PIANO_ROLL_WIDTH_PERCENT,
    CANVAS_GRID_X,
    CANVAS_GRID_Y,
    NOTE_THICKNESS,
    MIN_ZOOM,
    MAX_ZOOM,
    SOLFEGE,
)
import time


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
        self.timestamp = None
        self.timestamp_x = 0
        self.zoomLevel = 1
        self.note_id = []
        self.connected_line_id = []
        self.consonances_id = []
        self.last_shape = None
        self.notes_outlined = True

        super(PianoRoll, self).__init__(
            parent,
            width=self.width,
            height=self.height,
            bg='#34444e',
            highlightthickness=1,
            highlightbackground='black'
        )

        self.draw()
        self.grid(row=self.gridX, column=self.gridY)


    def draw(self):
        self.draw_notes('rectangle')

        self.timestamp = self.create_rectangle(
            self.timestamp_x, 0, 5, self.get_note_height(0)+NOTE_THICKNESS, fill='red', tags='timestamp'
        )


    def draw_notes(self, shape):
        app = self.parent.parent
        shape_method = None
        if shape == 'rectangle':
            shape_method = self.create_rectangle
        elif shape == 'oval':
            shape_method = self.create_oval
        elif shape == 'line':
            shape_method = self.create_line

        self.reset_zoom_level()
        self.last_shape = shape

        if app.tracks and shape_method:
            self.note_id = []
            for i, track in enumerate(app.tracks):
                self.note_id.append([])
                self.delete(f'track_{i}')
                for note in track.notes:
                    note_y = self.get_note_height(note[0])
                    note_start = note[1]
                    note_end = note[2]

                    if shape == 'rectangle' or shape == 'oval':
                        self.note_id[-1].append(
                            shape_method(
                                note_start, note_y,
                                note_end, note_y + NOTE_THICKNESS,
                                fill=track.color,
                                activefill='lightgray',
                                tags=f'track_{i}',
                        ))
                    elif shape == 'line':
                        self.note_id[-1].append(
                            shape_method(
                                note_start, note_y + NOTE_THICKNESS/2,
                                note_end, note_y + NOTE_THICKNESS/2,
                                fill=track.color,
                                activefill='lightgray',
                                tags=f'track_{i}',
                        ))
            if self.timestamp:
                self.tag_raise(self.timestamp)


    def change_opacity(self, bitmap_name):
        app = self.parent.parent
        if not app.tracks:
            return

        for i in range(len(self.note_id)):
            for note in self.note_id[i]:
                if bitmap_name == '':
                    self.itemconfigure(note, width=1, outline='black')
                else:
                    self.itemconfigure(note, width=0)
                self.itemconfigure(note, stipple=bitmap_name)


    def outline(self):
        self.notes_outlined = not self.notes_outlined
        for i in range(len(self.note_id)):
            for note in self.note_id[i]:
                self.itemconfigure(note, width=int(self.notes_outlined), outline='black')


    def show_consonances(self):
        app = self.parent.parent
        if not app.tracks:
            return
        self.reset_zoom_level()

        if len(self.consonances_id) > 0:
            self.delete('consonances')
            self.consonances_id = []
        else:
            song_name = app.root.filename.split('/')[-1].split('.')[0].replace('_', ' ').title()
            messagebox.showinfo(
                title='Additional consonances information',
                message=(
                    f'{song_name} has a percent of {app.consonant_percent:.2f} consonances\n'
                    f'Tip: you can always get see this under `View/Song info`'
                )
            )

            self.consonances_id = []
            tile_width = app.consonances[1][0] - app.consonances[0][0]
            tile_height = self.get_note_height(0)+NOTE_THICKNESS
            for t, val in app.consonances:
                color = ''
                if val == 'consonant':
                    color = 'green'
                elif val == 'dissonant':
                    color = 'red'

                self.consonances_id.append(
                    self.create_rectangle(
                        t, 0, t+tile_width, tile_height,
                        fill=color,
                        stipple='gray25',
                        outline='',
                        tags='consonances'
                ))
                self.tag_lower(self.consonances_id[-1])


    def connect_notes(self):
        app = self.parent.parent
        if not app.tracks:
            return

        self.reset_zoom_level()
        if len(self.connected_line_id) > 0:
            for i, track in enumerate(app.tracks):
                self.delete(f'line_track_{i}')
            self.connected_line_id = []
        else:
            self.connected_line_id = []
            for j, track in enumerate(app.tracks):
                self.connected_line_id.append([])
                for i in range(len(track.notes)-1):
                    note_y_1 = self.get_note_height(track.notes[i][0])
                    note_start_1 = track.notes[i][1]
                    note_end_1 = track.notes[i][2]
                    note_y_2 = self.get_note_height(track.notes[i+1][0])
                    note_start_2 = track.notes[i+1][1]
                    note_end_2 = track.notes[i+1][2]
                    self.connected_line_id[-1].append(
                        self.create_line(
                            (note_end_1+note_start_1)/2, note_y_1 + NOTE_THICKNESS/2,
                            (note_end_2+note_start_2)/2, note_y_2 + NOTE_THICKNESS/2,
                            fill=track.color,
                            activefill='black',
                            tags=f'line_track_{j}',
                    ))
                    if not app.trackSidebar.buttons[j].selected.get():
                        self.itemconfigure(self.connected_line_id[-1][-1], state='hidden')


    def reset_zoom_level(self):
        app = self.parent.parent
        if self.zoomLevel != 1:
            factor = 1 / self.zoomLevel
            self.zoomLevel = 1
            self.scale('all', 0, 0, factor, 1)

            x1, _, x2, _ = self.bbox('all')
            _, _, _, y2 = self.sidebar.bbox('all')
            self.configure(scrollregion=[x1, 0, x2, y2])
            app.timestamp_speed *= factor
            self.timestamp_x *= factor


    def init_tooltips(self, notation=None):
        app = self.parent.parent
        if not app.tracks or not app.tooltips_active:
            return

        for i, track in enumerate(app.tracks):
            for j in range(len(track.notes)):
                note_start = track.notes[j][1]
                note_end = track.notes[j][2]
                length = (note_end - note_start) * app.tick_to_track
                pitch = self.numeric_to_string_note(track.notes[j][0])
                if notation == 'classic':
                    pitch = SOLFEGE[list(pitch)[0]]
                    if self.numeric_to_string_note(track.notes[j][0]).find('#') > 0:
                        pitch += '#'

                message = f'{pitch} plays {length:.2f} s'
                app.tooltip.tagbind(self, self.note_id[i][j],  message)


    def enable_tooltips(self):
        app = self.parent.parent
        app.tooltips_active = not app.tooltips_active
        if app.tooltips_active:
            self.init_tooltips()
        else:
            for i, track in enumerate(app.tracks):
                for j in range(len(track.notes)):
                    app.tooltip.tagunbind(self, self.note_id[i][j])


    def play_song(self):
        start_time = time.time()
        app = self.parent.parent
        if self.parent.parent.musicPlayer.is_playing and app.seconds_elapsed < app.length_in_seconds:
            for i, note_index in enumerate(app.note_index_to_play):
                # Add new notes that are being played
                while note_index < len(app.tracks[i].notes):
                    note, start, end = app.tracks[i].notes[note_index]
                    start *= app.tick_to_track
                    end *= app.tick_to_track
                    if start <= app.seconds_elapsed and app.seconds_elapsed < end:
                        app.current_notes[i].append([note, start, end, note_index])
                        sidebar_note = self.sidebar.notes[note]
                        self.sidebar.itemconfig(sidebar_note.id, fill=sidebar_note.activefill)
                        self.sidebar.activeNotes[note] += 1
                        self.itemconfig(self.note_id[i][note_index], fill='lightgray')
                        note_index += 1
                    else:
                        break
                app.note_index_to_play[i] = note_index

                # Remove notes that finished playing
                for elem in app.current_notes[i]:
                    note, start, end, note_index = elem
                    if end < app.seconds_elapsed:
                        self.sidebar.activeNotes[note] -= 1
                        if self.sidebar.activeNotes[note] == 0:
                            sidebar_note = self.sidebar.notes[note]
                            self.sidebar.itemconfig(sidebar_note.id, fill=sidebar_note.color)
                        self.itemconfig(self.note_id[i][note_index], fill=app.tracks[i].color)
                        app.current_notes[i].remove(elem)

            stop_time = time.time()
            method_time = stop_time - start_time

            self.parent.after(int(1000 / app.fps) - app.fps*int(method_time*1000), self.play_song)
            self.timestamp_x += app.timestamp_speed * (1 + method_time*app.fps)
            self.move(self.timestamp, app.timestamp_speed * (1 + method_time*app.fps), 0)
            app.seconds_elapsed += 1 / app.fps + method_time


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

        self.scroll_x = tk.Scrollbar(
            parent,
            orient='horizontal',
            command=self._horizontal_scroll,
            repeatdelay=0,
            repeatinterval=0,
            takefocus=False,
        )
        self.scroll_x.grid(row=self.gridX-1, column=self.gridY, sticky='ew', columnspan=2)

        self.scroll_y = tk.Scrollbar(
            parent,
            orient='vertical',
            command=self._vertical_scroll,
            repeatdelay=0,
            repeatinterval=0,
            takefocus=False,
        )
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

        # Zoom only if a song is already selected
        if app.root.filename:
            x = 0
            y = self.canvasy(event.y)
            factor = 1.001 ** event.delta

            if self.zoomLevel * factor > MIN_ZOOM and self.zoomLevel * factor < MAX_ZOOM:
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


    def _horizontal_scroll(self, *args):
        self.xview(*args)
