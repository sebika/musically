from tkinter import Button, Toplevel

class MusicallyButton(Button):
    def __init__(self, buttonText, row, column):
        super(Button, self).__init__(text=buttonText)
        self.grid(row=row, column=column)
