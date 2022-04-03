import tkinter as tk
from common import Track
from constants import (
    ROOT_INITIAL_HEIGHT,
    ROOT_INITIAL_WIDTH,
    COLOR_PALETTE,
    TRACKS_PATELLTE
)
from pianoRoll import PianoRoll
from sidebar import PianoNoteSidebar, MusicPlayer, TrackSidebar
from mido import MidiFile, Message, tick2second, MetaMessage
from tkinter import filedialog
import pygame
import Pmw


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.parent = self
        self.tracks = None
        self.root.filename = None
        self.length_in_seconds = None
        self.seconds_elapsed = None
        self.tooltip = Pmw.Balloon()

        self.sidebar = PianoNoteSidebar(self.root)
        self.canvas = PianoRoll(self.root, self.sidebar)
        self.canvas.configure_scrollbars(self.root)
        self.musicPlayer = MusicPlayer(self.root)
        self.trackSidebar = TrackSidebar(self.root)

        self.root.update()

        self.init_mixer()
        self.init_window()
        self.init_menu()

        self.root.bind('<Configure>', self.updateSize)
        self.root.bind('<space>', self.musicPlayer.play_song)
        self.root.bind('r', self.musicPlayer.stop_song)
        self.root.configure(bg=COLOR_PALETTE['black_coral'])


    def init_mixer(self):
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
        pygame.mixer.init()


    def init_window(self):
        self.screenWidth = self.root.winfo_screenwidth()
        self.screenHeight = self.root.winfo_screenheight()
        pixelsRight = (self.screenWidth - ROOT_INITIAL_WIDTH) // 2
        pixelsDown = (self.screenHeight - ROOT_INITIAL_HEIGHT) // 2
        self.root.geometry(
            f'{ROOT_INITIAL_WIDTH}x{ROOT_INITIAL_HEIGHT}+{pixelsRight}+{pixelsDown}'
        )
        self.root.deiconify()
        self.root.iconphoto(True, tk.PhotoImage(file='resources/images/logo.png'))
        self.root.title('Musically')


    def init_menu(self):
        self.menu = tk.Menu(self.root)

        fileMenu = tk.Menu(self.menu, tearoff=0)
        fileMenu.add_command(label='Open', command=self._open_file)
        fileMenu.add_separator()
        fileMenu.add_command(label='Exit', command=self.root.destroy)
        self.menu.add_cascade(label='File', menu=fileMenu)

        preferencesMenu = tk.Menu(self.menu, tearoff=0)

        solfege_submenu = tk.Menu(preferencesMenu, tearoff=0)
        solfege_submenu.add_radiobutton(label='Do/Re/Mi', command=lambda: self.change_solfege_notes('classic'))
        solfege_submenu.add_radiobutton(label='A0/B0/C0', command=lambda: self.change_solfege_notes('new'))
        preferencesMenu.add_cascade(label='Solfege', menu=solfege_submenu)

        notes_submenu = tk.Menu(preferencesMenu, tearoff=0)
        notes_submenu.add_checkbutton(label='Connected notes')
        notes_submenu.add_command(label='Color')
        notes_submenu.add_command(label='Shape')
        notes_submenu.add_command(label='Opacity')
        preferencesMenu.add_cascade(label='Notes', menu=notes_submenu)

        self.menu.add_cascade(label='Preferences', menu=preferencesMenu)

        self.menu.add_cascade(label='Help')

        self.root.config(menu=self.menu)


    def init_sidebar_notes(self):
        for i, note in enumerate(self.sidebar.notes):
            self.sidebar.itemconfig(note.id, fill=note.color)
            self.sidebar.activeNotes[i] = 0


    def init_canvas_notes(self):
        for track_id in range(len(self.canvas.note_id)):
            for note in self.canvas.note_id[track_id]:
                self.canvas.itemconfig(note, fill=self.tracks[track_id].color)


    def updateSize(self, event):
        self.canvas.updateSize(event, self.root)
        self.sidebar.updateSize(event, self.root)
        self.musicPlayer.updateSize(event, self.root)
        self.trackSidebar.updateSize(event, self.root)


    def change_solfege_notes(self, notation=None):
        for note in self.sidebar.notes:
            if note.textId:
                new_text = note.pitch
                self.canvas.init_tooltips()
                if notation == 'classic':
                    new_text = note.classic_pitch
                    self.canvas.init_tooltips('classic')

                self.sidebar.itemconfigure(note.textId, text=new_text)


    def _open_file(self):
        self.root.filename = filedialog.askopenfilename(
            initialdir='./resources/songs',
            title='Select A File',
            filetypes=(('midi', '*.mid'),('all files', '*.*'))
        )
        if not self.root.filename:
            return

        self.init_sidebar_notes()
        pygame.mixer.music.stop()
        self.musicPlayer.is_playing = None
        self.tracks = self.import_song(self.root.filename)
        for track in self.tracks:
            track.notes.sort(key=lambda y: y[1])

        # Create a new canvas
        self.canvas.grid_remove()
        self.canvas = PianoRoll(self.root, self.sidebar, self.tracks)
        self.canvas.configure_scrollbars(self.root)

        for i, track in enumerate(self.tracks):
            self.trackSidebar.buttons[i].show()
            self.trackSidebar.buttons[i]['text'] = track.name
        for i in range(len(self.tracks), len(self.trackSidebar.buttons)):
            self.trackSidebar.buttons[i].hide()

        # Snap to the first note
        h = 10 ** 6
        for track in self.tracks:
            h = min(h, self.canvas.get_note_height(track.notes[0][0]))
        self.canvas.yview_moveto(h / self.canvas.get_note_height(0) - 0.1)
        self.sidebar.yview_moveto(h / self.canvas.get_note_height(0) - 0.1)

        # Update track button colors
        for btn in self.trackSidebar.buttons:
            btn.update_color()

        # Compute speed to the timestamp
        self.length_in_seconds = tick2second(self.length_in_ticks, self.ticks_per_beat, self.tempo)
        self.fps = 100
        self.timestamp_speed = self.length_in_ticks / self.length_in_seconds / self.fps
        self.seconds_elapsed = 0
        self.tick_to_track = self.length_in_seconds / self.length_in_ticks
        self.init_current_playing_notes()
        self.canvas.init_tooltips()



    def init_current_playing_notes(self):
        self.current_notes = []
        self.note_index_to_play = []
        for i in range(len(self.tracks)):
            self.current_notes.append([])
            self.note_index_to_play.append(0)


    def import_song(self, songname):
        mid = MidiFile(songname)
        self.ticks_per_beat = mid.ticks_per_beat
        self.length_in_ticks = 0

        tracks = []
        i = 0
        for track in mid.tracks:
            # Each note, for example C4 should have (start, end) pair
            current_track_dict = {}
            ticks = 0

            instrument_track = []
            for msg in track:
                if isinstance(msg, Message) and (msg.type == 'note_on' or msg.type == 'note_off'):
                    pitch = msg.note
                    ticks += msg.time

                    # This is the start of a note
                    if msg.type == 'note_on' and msg.velocity != 0:
                        if pitch in current_track_dict:
                            print(f'Info: note {pitch} starts playing again before it ended')

                        current_track_dict[pitch] = [ticks, -1]

                    # This is the and of a note
                    elif (msg.type == 'note_on' and msg.velocity == 0) or msg.type == 'note_off':
                        if pitch not in current_track_dict:
                            print(f'Info: note {pitch} ended before it started')
                            continue

                        current_track_dict[pitch][1] = ticks
                        start = current_track_dict[pitch][0]
                        end = current_track_dict[pitch][1]
                        current_track_dict.pop(pitch, 'None')
                        instrument_track.append((pitch, start , end))
                elif isinstance(msg, MetaMessage) and msg.type == 'set_tempo':
                    if msg.tempo != 0:
                        self.tempo = msg.tempo
                else:
                    ticks += msg.time
                self.length_in_ticks = ticks

            # Save only the tracks that have notes
            if len(instrument_track) != 0:
                if len(track.name) == 0:
                    track.name = f'track_{len(tracks)}'
                tracks.append(Track(track.name, instrument_track, TRACKS_PATELLTE[list(TRACKS_PATELLTE.keys())[i]]))
                i += 1

        return tracks


    def run(self):
        self.root.mainloop()
