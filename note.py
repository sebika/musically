from constants import COLOR_PALETTE

class SidebarNote():
    def __init__(self, x, y, width, height, color, pitch, canvas, addNoteText=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.pitch = pitch
        self.id = canvas.create_rectangle(x, y, width, height, fill=color)
        self.textId = None

        if addNoteText:
            self.textId = canvas.create_text(0, 0, text=self.pitch)

        if pitch.find('#') != -1:
            canvas.itemconfig(self.id, activefill=COLOR_PALETTE['space_cadet'])
        else:
            canvas.itemconfig(self.id, activefill=COLOR_PALETTE['blue_gray'])
