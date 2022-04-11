import tkinter as tk
from sidebar import Track
from constants import (
    CONSONANCES,
    FPS,
    ROOT_INITIAL_HEIGHT,
    ROOT_INITIAL_WIDTH,
    COLOR_PALETTE,
    SCROLL_SPEED,
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
        self.init_class_members()
        self.init_mixer()
        self.init_window()
        self.init_menu()

        self.root.bind('<Configure>', self.updateSize)
        self.root.bind('<space>', self.musicPlayer.play_song)
        self.root.bind('r', self.musicPlayer.stop_song)
        self.root.bind('m', self.musicPlayer.mute_unmute)
        self.root.bind("<Left>",  lambda event: self.canvas.xview_scroll(-SCROLL_SPEED, "units"))
        self.root.bind("<Right>", lambda event: self.canvas.xview_scroll(SCROLL_SPEED, "units"))
        self.root.bind("<Up>",    lambda event: (
            self.canvas.yview_scroll(-SCROLL_SPEED, "units"),
            self.sidebar.yview_scroll(-SCROLL_SPEED, "units"),
        ))
        self.root.bind("<Down>",  lambda event: (
            self.canvas.yview_scroll(SCROLL_SPEED, "units"),
            self.sidebar.yview_scroll(SCROLL_SPEED, "units"),
        ))

        self.root.configure(bg=COLOR_PALETTE['black_coral'])

    def init_class_members(self):
        self.root = tk.Tk()
        self.root.parent = self
        self.tracks = None
        self.root.filename = None
        self.length_in_seconds = None
        self.consonant_percent = -1
        self.seconds_elapsed = None
        self.menu = None
        self.tooltip = Pmw.Balloon()
        self.tooltips_active = False

        self.sidebar = PianoNoteSidebar(self.root)
        self.canvas = PianoRoll(self.root, self.sidebar)
        self.canvas.configure_scrollbars(self.root)
        self.musicPlayer = MusicPlayer(self.root)
        self.trackSidebar = TrackSidebar(self.root)


    def init_mixer(self):
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
        pygame.mixer.init()


    def init_window(self):
        self.screenWidth = self.root.winfo_screenwidth()
        self.screenHeight = self.root.winfo_screenheight()
        pixelsRight = (self.screenWidth - ROOT_INITIAL_WIDTH) // 2
        pixelsDown = (self.screenHeight - ROOT_INITIAL_HEIGHT) // 3
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
        fileMenu.add_command(
            label='Play/Pause                [Space]',
            command=lambda: self.musicPlayer.play_song(None)
        )
        fileMenu.add_command(
            label='Stop                           [R]',
            command=lambda: self.musicPlayer.stop_song(None)
        )
        fileMenu.add_command(
            label='Mute/Unmute         [M]',
            command=lambda: self.musicPlayer.mute_unmute(None)
        )
        fileMenu.add_separator()
        fileMenu.add_command(label='Exit', command=self.root.destroy)
        self.menu.add_cascade(label='File', menu=fileMenu)

        viewMenu = tk.Menu(self.menu, tearoff=0)
        viewMenu.add_command(label='Consonances', command=lambda: self.canvas.show_consonances())
        viewMenu.add_command(label='Notes connected', command=lambda: self.canvas.connect_notes())
        viewMenu.add_command(label='Tooltips', command=lambda: self.canvas.enable_tooltips())
        viewMenu.add_separator()
        viewMenu.add_command(label='Song info', command=lambda: self.song_info())

        appearance_submenu = tk.Menu(viewMenu, tearoff=0)
        solfege_submenu = tk.Menu(viewMenu, tearoff=0)
        solfege_submenu.add_command(label='Classic       [Do/Re/Mi]', command=lambda: self.change_solfege_notes('classic'))
        solfege_submenu.add_command(label='Modern     [A0/B0/C0]', command=lambda: self.change_solfege_notes('new'))
        appearance_submenu.add_cascade(label='Solfege', menu=solfege_submenu)

        notes_submenu = tk.Menu(viewMenu, tearoff=0)
        notes_submenu.add_command(label='Outline', command=lambda: self.canvas.outline())
        shape_submenu = tk.Menu(notes_submenu, tearoff=0)
        shape_submenu.add_command(label='Rectangle', command=lambda: (
            self.canvas.draw_notes('rectangle'),
            self.canvas.init_tooltips(),
        ))
        shape_submenu.add_command(label='Oval', command=lambda: (
            self.canvas.draw_notes('oval'),
            self.canvas.init_tooltips(),
        ))
        shape_submenu.add_command(label='Line', command=lambda: (
            self.canvas.draw_notes('line'),
            self.canvas.init_tooltips(),
        ))
        notes_submenu.add_cascade(label='Shape', menu=shape_submenu)

        opacity_submenu = tk.Menu(notes_submenu, tearoff=0)
        opacity_submenu.add_command(
            label='Opac',
            command=lambda: self.canvas.change_opacity('')
        )
        opacity_submenu.add_command(
            label='gray75',
            command=lambda: self.canvas.change_opacity('gray75')
        )
        opacity_submenu.add_command(
            label='gray50',
            command=lambda: self.canvas.change_opacity('gray50')
        )
        opacity_submenu.add_command(
            label='gray25',
            command=lambda: self.canvas.change_opacity('gray25')
        )
        opacity_submenu.add_command(
            label='gray12',
            command=lambda: self.canvas.change_opacity('gray12')
        )
        notes_submenu.add_cascade(label='Opacity', menu=opacity_submenu)
        appearance_submenu.add_cascade(label='Notes', menu=notes_submenu)

        self.menu.add_cascade(label='View', menu=viewMenu)
        self.menu.add_cascade(label='Appearance', menu=appearance_submenu)
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


    def song_info(self):
        if self.root.filename:
            song_name = self.root.filename.split('/')[-1].split('.')[0].replace('_', ' ').title()
            tk.messagebox.showinfo(
                title=f'{song_name} - additional information',
                message=(
                    f'Song length: {self.length_in_seconds:.2f}s\n'
                    f'Time signature: {self.numerator}/{self.denominator}\n'
                    f'Number of tracks: {len(self.tracks)}\n'
                    f'Number of notes: {sum([len(track.notes) for track in self.tracks])}\n'
                    f'Consonances percent: {self.consonant_percent:.2f}%'
                )
            )


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
        file = filedialog.askopenfilename(
            initialdir='./resources/songs',
            title='Select A File',
            filetypes=(('midi', '*.mid'),('all files', '*.*'))
        )
        if not file:
            return

        self.root.filename = file

        self.init_sidebar_notes()
        pygame.mixer.music.stop()
        self.musicPlayer.is_playing = None
        self.tracks = self.import_song(self.root.filename)
        for track in self.tracks:
            track.notes.sort(key=lambda y: y[1])

        self.compute_consonances_and_dissonances()

        # Create a new canvas
        self.canvas.grid_remove()
        self.canvas = PianoRoll(self.root, self.sidebar, self.tracks)
        self.canvas.configure_scrollbars(self.root)

        track_names = [track.name for track in self.tracks]
        self.trackSidebar.draw(track_names)
        self.trackSidebar.update()

        # Update track button colors
        for btn in self.trackSidebar.buttons:
            btn.update_color()

        # Snap to the first note
        h = 10 ** 6
        for track in self.tracks:
            h = min(h, self.canvas.get_note_height(track.notes[0][0]))
        self.canvas.yview_moveto(h / self.canvas.get_note_height(0) - 0.1)
        self.sidebar.yview_moveto(h / self.canvas.get_note_height(0) - 0.1)

        # Compute speed of the timestamp
        self.length_in_seconds = tick2second(self.length_in_ticks, self.ticks_per_beat, self.tempo)
        self.fps = FPS
        self.timestamp_speed = self.length_in_ticks / self.length_in_seconds / self.fps
        self.seconds_elapsed = 0
        self.tick_to_track = self.length_in_seconds / self.length_in_ticks
        self.init_current_playing_notes()
        self.canvas.init_tooltips()


    def init_current_playing_notes(self):
        self.current_notes = []
        self.note_index_to_play = []
        for _ in range(len(self.tracks)):
            self.current_notes.append([])
            self.note_index_to_play.append(0)


    def compute_consonances_and_dissonances(self):
        self.consonances = []
        no_consonant = 0
        no_dissonant = 0
        for t in range(0, self.length_in_ticks+1, 10):
            notes_now = []
            for track in self.tracks:
                for note in track.notes:
                    if note[1] <= t and note[2] >= t:
                        notes_now.append(note[0])
                    elif note[1] > t:
                        break
            if len(notes_now) > 1:
                notes_now.sort()
                consonants = 0
                total = 0
                for i in range(len(notes_now)-1):
                    for j in range(i+1, len(notes_now)):
                        if (notes_now[j] - notes_now[i]) % 12 in CONSONANCES:
                            consonants += 1
                        total += 1
                percent = consonants / total * 100
                if percent >= 50:
                    self.consonances.append((t, 'consonant'))
                    no_consonant += 1
                else:
                    self.consonances.append((t, 'dissonant'))
                    no_dissonant += 1
            else:
                self.consonances.append((t, 'less than 2 notes are playing'))

        self.consonant_percent = no_consonant / (no_consonant + no_dissonant) * 100


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
                elif isinstance(msg, MetaMessage) and msg.type == 'time_signature':
                    self.numerator = msg.numerator
                    self.denominator = msg.denominator
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
