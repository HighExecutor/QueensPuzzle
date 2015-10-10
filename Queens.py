__author__ = 'Mishanya'

from tkinter import *
from Operators import GA_for_queens
import threading

n = 8
best_fit = 0
worst_fit = 0
avg_fit = 0
queen_arr = []
lines_arr = []
rect_arr = None



def init_field():
    global n, queen, canvas
    n = int(e_n.get())
    canvas.delete("all")
    d = 400 / n
    rect_arr = []
    for i in range(n):
        rect_arr.append([])
        for j in range(n):
            cur_rect = canvas.create_rectangle(2+i*d, 2+j*d, 1+(i+1)*d, 1+(j+1)*d)
            if (i+j) % 2 == 0:
                canvas.itemconfig(cur_rect, fill="brown")
            else:
                canvas.itemconfig(cur_rect, fill="orange")
            rect_arr[i].append(cur_rect)

    queen = PhotoImage(file="queen.png")
    d = int(400 / n)
    queen = queen.zoom(d, d)
    queen = queen.subsample(50, 50)


def start():
    canvas.delete('all')
    init_field()
    b_start['state'] = 'disabled'
    alg = GA_for_queens(n, canvas, queen, (e_best, e_worst, e_avg), b_start)
    thr = threading.Thread(target=alg)
    thr.start()
    pass



root = Tk()
settings = Frame(root, width=500, height=50, bg="red")
field = Frame(root, width=400, height=400, bg="green")
status = Frame(root, width=100, height=400, bg="blue")
b_start = Button(settings, text="Start", command=start, state=NORMAL)
b_init = Button(settings, text='init', command=init_field)
l_n = Label(settings, text="N=")
l_best = Label(status, text="Best_fit=")
l_worst = Label(status, text="Worst_fit=")
l_avg = Label(status, text="Avg_fit=")
e_n = Entry(settings, width=5)
e_n.insert(0, 8)
e_best = Entry(status, width=5)
e_worst = Entry(status, width=5)
e_avg = Entry(status, width=5)
canvas = Canvas(field, width=400, height=400)
canvas.pack()
settings.pack(fill=X)
status.pack(side=RIGHT, fill=Y)
field.pack(side=LEFT, fill=BOTH, expand=1)
l_n.pack(side=LEFT)
e_n.pack(side=LEFT)
b_start.pack(side=RIGHT)
b_init.pack(side=RIGHT)
l_best.pack()
e_best.pack()
l_avg.pack()
e_avg.pack()
l_worst.pack()
e_worst.pack()

init_field()
queen = PhotoImage(file="queen.png")

root.mainloop()