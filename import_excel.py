import tkinter as tk
from tkinter import filedialog
import pandas as pd


def get_excel():
    path = filedialog.askopenfilename()
    df = pd.read_excel(path)
    print(df)


def main():
    root = tk.Tk()
    canvas = tk.Canvas(root,
                       width=300,
                       height=300,
                       bg='lightsteelblue')
    canvas.pack()
    browse_button = tk.Button(text='Import Excel File',
                              command=get_excel,
                              bg='green',
                              fg='white',
                              font=('helvetica', 12, 'bold'))
    canvas.create_window(150, 150, window=browse_button)
    root.mainloop()


if __name__ == '__main__':
    main()
