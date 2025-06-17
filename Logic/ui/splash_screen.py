import customtkinter as ctk
import threading
import time


class SplashScreen:
    def __init__(self, parent, on_complete=None):
        self.parent = parent
        self.on_complete = on_complete

        self.splash_frame = ctk.CTkFrame(parent)
        self.splash_frame.pack(fill="both", expand=True)

        # logo
        title_label = ctk.CTkLabel(
            self.splash_frame,
            text="Apprentice Email\nAutomation System",
            font=ctk.CTkFont(size=36, weight="bold"),
        )
        title_label.pack(pady=(200, 20))

        subtitle_label = ctk.CTkLabel(
            self.splash_frame,
            text="Streamline your apprentice communications",
            font=ctk.CTkFont(size=16),
        )
        subtitle_label.pack(pady=(0, 20))

        # loading indicator
        self.loading_label = ctk.CTkLabel(
            self.splash_frame, text="Loading...", font=ctk.CTkFont(size=14)
        )
        self.loading_label.pack(pady=20)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.splash_frame, width=300)
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)

        # start loading animation
        self.animate_loading()

    def animate_loading(self):

        def update_progress():
            for i in range(101):
                self.progress_bar.set(i / 100)
                self.parent.update_idletasks()
                time.sleep(0.02)

            # hide splash and show main app
            self.splash_frame.destroy()
            if self.on_complete:
                self.on_complete()

        threading.Thread(target=update_progress, daemon=True).start()
