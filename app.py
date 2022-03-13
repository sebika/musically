from collections import OrderedDict
import tkinter as tk
from constants import ROOT_INITIAL_HEIGHT, ROOT_INITIAL_WIDTH
from pianoRoll import PianoRoll
from sidebar import PianoNoteSidebar
from mido import MidiFile, Message


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.sidebar = PianoNoteSidebar(self.root)
        self.canvas = PianoRoll(self.root, self.sidebar)

        self.canvas.configure_scrollbars(self.root)

        self.root.update()
        l1 = tk.Label(self.root, text='(0, 0)')
        l1.grid(row=0, column=0)

        self.root.update()
        l2 = tk.Frame(self.root, background='lightgray', width=ROOT_INITIAL_WIDTH*0.86, height=100)
        l2.grid(row=0, column=1, columnspan=3, sticky='w')

        self.root.update()
        l3 = tk.Frame(self.root, background='lightgray', width=100, height=ROOT_INITIAL_HEIGHT* 0.75)
        l3.grid(row=1, column=0, rowspan=2, stick='S')

        self.init_window()
        self.init_menu()

        self.root.bind('<Configure>', self.updateSize)
        self.root.configure(bg='white')


    def init_window(self):
        self.screenWidth = self.root.winfo_screenwidth()
        self.screenHeight = self.root.winfo_screenheight()
        pixelsRight = (self.screenWidth - ROOT_INITIAL_WIDTH) // 2
        pixelsDown = (self.screenHeight - ROOT_INITIAL_HEIGHT) // 2
        self.root.geometry(
            f'{ROOT_INITIAL_WIDTH}x{ROOT_INITIAL_HEIGHT}+{pixelsRight}+{pixelsDown}'
        )
        self.root.deiconify()
        self.root.iconphoto(True, tk.PhotoImage(file='resources/logo.png'))
        self.root.title('Musically')


    def init_menu(self):
        self.menu = tk.Menu(self.root)

        fileMenu = tk.Menu(self.menu, tearoff=0)
        fileMenu.add_command(label='Open', command='')
        fileMenu.add_command(label='Save', command='')
        fileMenu.add_separator()
        fileMenu.add_command(label='Exit', command=self.root.destroy)
        self.menu.add_cascade(label='File', menu=fileMenu)

        self.menu.add_cascade(label='Preferences')
        self.menu.add_cascade(label='Help')

        self.root.config(menu=self.menu)


    def updateSize(self, event):
        self.canvas.updateSize(event, self.root)
        self.sidebar.updateSize(event, self.root)


    def import_song(self, songname):
        tracks = OrderedDict()
        mid = MidiFile(songname)
        for track in mid.tracks:
            tracks[track.name] = []

            # Each note, for example C4 should have (start, end) pair
            current_track_dict = {}
            ticks = 0

            for msg in track:
                if isinstance(msg, Message) and (msg.type == 'note_on' or msg.type == 'note_off'):
                    pitch = self.sidebar.notes[msg.note].pitch
                    ticks += msg.time

                    # This is the start of a note
                    if msg.type == 'note_on' and msg.velocity != 0:
                        if pitch in current_track_dict:
                            print("Error: note {pitch} starts playing again before it ended")
                        current_track_dict[pitch] = [ticks, -1]

                    # This is the and of a note
                    elif (msg.type == 'note_on' and msg.velocity == 0) or msg.type == 'note_off':
                        if pitch not in current_track_dict:
                            print("Error: note {pitch} ended before it started")
                        current_track_dict[pitch][1] = ticks
                        tracks[track.name].append([pitch, current_track_dict[pitch]])

                        current_track_dict.pop(pitch, 'None')

            # Remove empty tracks
            if len(tracks[track.name]) == 0:
                tracks.pop(track.name)

        print(tracks)

    def run(self):
        self.import_song('resources\song.mid')
        self.root.mainloop()
