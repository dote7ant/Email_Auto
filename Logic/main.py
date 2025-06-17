import customtkinter as ctk
from ui.main_window import MainWindow


def main():

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # create and run the main application
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
