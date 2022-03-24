import tkinter as tk
from common import Track
from constants import ROOT_INITIAL_HEIGHT, ROOT_INITIAL_WIDTH, COLOR_PALETTE, TRACKS_PATELLTE
from pianoRoll import PianoRoll
from sidebar import PianoNoteSidebar, MusicPlayer, TrackSidebar
from mido import MidiFile, Message, tick2second
from tkinter import filedialog
import pygame


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.parent = self
        self.tracks = None
        self.root.filename = None

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

        self.menu.add_cascade(label='View')
        self.menu.add_cascade(label='Help')

        self.root.config(menu=self.menu)


    def updateSize(self, event):
        self.canvas.updateSize(event, self.root)
        self.sidebar.updateSize(event, self.root)
        self.musicPlayer.updateSize(event, self.root)
        self.trackSidebar.updateSize(event, self.root)


    def _open_file(self):
        self.root.filename = filedialog.askopenfilename(
            initialdir='./resources/songs',
            title='Select A File',
            filetypes=(('midi', '*.mid'),('all files', '*.*'))
        )
        pygame.mixer.music.stop()
        self.musicPlayer.is_playing = None
        self.tracks = self.import_song(self.root.filename)

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

        l = self.tracks[0].notes[-1][2]
        tempo = 461538
        ticks_per_beat = 96
        # print(f'{l} ticks -> {tick2second(l, ticks_per_beat, tempo)} sec')


    def import_song(self, songname):
        mid = MidiFile(songname)
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

            # Save only the tracks that have notes
            if len(instrument_track) != 0:
                if len(track.name) == 0:
                    track.name = f'track_{len(tracks)}'
                tracks.append(Track(track.name, instrument_track, TRACKS_PATELLTE[list(TRACKS_PATELLTE.keys())[i]]))
                i += 1

        return tracks


    def run(self):
        self.root.mainloop()
