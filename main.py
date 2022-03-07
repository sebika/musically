from textwrap import fill
import tkinter as tk

def update_l1(event):
    l1.config(text=f'W:{parent.winfo_width()} H:{parent.winfo_height()}')

parent = tk.Tk()
parent.geometry("500x500")
parent.bind('<Configure>', update_l1)

canvas_x = 1
canvas_y = 1
canvas = tk.Canvas(parent, width=300, height=300, bg='white')
canvas.create_oval(10, 10, 20, 20, fill="red")
canvas.create_oval(400, 400, 420, 420, fill="blue")
canvas.create_rectangle(600, 10, 640, 50)
canvas.grid(row=canvas_x+1, column=canvas_y)

scroll_x = tk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
scroll_x.grid(row=canvas_x, column=canvas_y, sticky="ew", columnspan=2)

scroll_y = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
scroll_y.grid(row=canvas_x+1, column=canvas_y+1, sticky="ns")

canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
canvas.configure(scrollregion=canvas.bbox("all"))

l1 = tk.Label(parent, text=f'aaaaaaaaaa')
l1.grid(row=0, column=0, columnspan=2)

l2 = tk.Label(parent, text='bbbb')
l2.grid(row=1, column=0, rowspan=2)

# while True:
#     # update_l1()
#     parent.update()

parent.mainloop()
