import tkinter as tk
from constants import ROOT_INITIAL_HEIGHT, ROOT_INITIAL_WIDTH
from pianoRoll import PianoRoll, PianoNoteSidebar


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.canvas = PianoRoll(self.root)
        self.sidebar = PianoNoteSidebar(self.root)

        self.canvas.configure_scrollbars(self.root, self.sidebar)

        l1 = tk.Label(self.root, text='(0, 1)')
        l1.grid(row=0, column=1, columnspan=3)

        self.root.update()
        l2 = tk.Label(self.root, text='(1, 0)')
        l2.grid(row=1, column=0, rowspan=2)

        self.root.update()
        l2 = tk.Label(self.root, text='(0, 0)')
        l2.grid(row=0, column=0)

        self.init_window()
        self.init_menu()

        self.root.bind('<Configure>', self.updateSize)


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


    def run(self):
        self.root.mainloop()
