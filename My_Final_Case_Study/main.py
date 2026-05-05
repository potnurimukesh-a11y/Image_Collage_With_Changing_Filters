import tkinter as tk
from Collage import CollageApp

def main():
    root = tk.Tk()
    app = CollageApp(root)
    app.show_home()
    root.mainloop()

if __name__ == '__main__':
    main()