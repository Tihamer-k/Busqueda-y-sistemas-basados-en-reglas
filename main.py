from src.gui.app import RouteApp
import src.version as version
import tkinter as tk

def main():
    root = tk.Tk()
    RouteApp(root)
    root.mainloop()

if __name__ == '__main__':
    print(f"Versión del sistema experto: {version.__version__}")
    main()
