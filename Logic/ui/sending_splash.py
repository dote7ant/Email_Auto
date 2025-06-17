import customtkinter as ctk


class SendingSplash:
    def __init__(self, parent, on_complete_callback=None):
        self.on_complete = on_complete_callback

        self.splash_window = ctk.CTkToplevel(parent)
        self.splash_window.title("Sending Emails")
        self.splash_window.geometry("400x300")
        self.splash_window.resizable(False, False)

        # center the window
        self.splash_window.transient(parent)
        self.splash_window.grab_set()

        self.setup_ui()

    def setup_ui(self):
        # title
        title_label = ctk.CTkLabel(
            self.splash_window,
            text="Sending Emails",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(50, 20))

        # progress bar
        self.progress_bar = ctk.CTkProgressBar(self.splash_window, width=300)
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)

        # status label
        self.status_label = ctk.CTkLabel(
            self.splash_window, text="Preparing to send...", font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)

        # count label
        self.count_label = ctk.CTkLabel(
            self.splash_window, text="0 / 0", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.count_label.pack(pady=5)

    def update_progress(self, current, total, current_email=""):
        # update progress display
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)

        self.count_label.configure(text=f"{current} / {total}")

        if current_email:
            self.status_label.configure(text=f"Sending to {current_email}")
        else:
            self.status_label.configure(text="Processing...")

    def close(self):
        try:
            self.splash_window.destroy()
        except:
            pass
