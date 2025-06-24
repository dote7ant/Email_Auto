import customtkinter as ctk
import threading
import time
from ui.splash_screen import SplashScreen
from ui.file_upload_tab import FileUploadTab
from ui.templates_tab import TemplatesTab
from ui.send_emails_tab import SendEmailsTab
from ui.status_tab import StatusTab
from core.email_manager import EmailManager
from core.data_processor import DataProcessor
from core.template_manager import TemplateManager


class MainWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Apprentice Email Automation")

        # calculate DPI scaling for window sizing
        self.dpi_scale = self.get_dpi_scale()

        # set window size with DPI scaling
        base_width = 1200
        base_height = 800
        scaled_width = int(base_width * self.dpi_scale)
        scaled_height = int(base_height * self.dpi_scale)
        self.root.geometry(f"{scaled_width}x{scaled_height}")
        self.root.resizable(True, True)

        # set minimum size with DPI scaling
        min_width = int(800 * self.dpi_scale)
        min_height = int(600 * self.dpi_scale)
        self.root.minsize(min_width, min_height)

        # initialize core components
        self.email_manager = EmailManager()
        self.data_processor = DataProcessor()
        self.template_manager = TemplateManager()

        # initialize UI components
        self.splash_screen = None
        self.file_upload_tab = None
        self.templates_tab = None
        self.send_emails_tab = None
        self.status_tab = None

        # show splash screen first
        self.show_splash_screen()

    def get_dpi_scale(self):
        # get DPI scaling factor for the current display
        try:
            # calculate DPI scaling
            dpi = self.root.winfo_fpixels("1i")
            standard_dpi = 96.0
            scale_factor = dpi / standard_dpi

            # clamp the scale factor to reasonable bounds
            return max(0.8, min(2.5, scale_factor))

        except:
            return 1.0  # fallback to no scaling

    def get_scaled_font_size(self, base_size):
        # calculate scaled font size based on DPI
        scaled_size = base_size * self.dpi_scale
        return max(8, int(scaled_size))

    def show_splash_screen(self):
        self.splash_screen = SplashScreen(
            self.root, on_complete=self.create_main_interface
        )

    def create_main_interface(self):
        # main container
        self.main_frame = ctk.CTkFrame(self.root)
        padding = int(10 * self.dpi_scale)
        self.main_frame.pack(fill="both", expand=True, padx=padding, pady=padding)

        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Apprentice Email Automation",
            font=ctk.CTkFont(size=self.get_scaled_font_size(24), weight="bold"),
        )

        title_padding = (int(10 * self.dpi_scale), int(20 * self.dpi_scale))
        title_label.pack(pady=title_padding)

        self.tabview = ctk.CTkTabview(self.main_frame)
        tab_padding = int(10 * self.dpi_scale)
        self.tabview.pack(fill="both", expand=True, padx=tab_padding, pady=tab_padding)

        self.tabview.add("File Upload")
        self.tabview.add("Email Templates")
        self.tabview.add("Send Emails")
        self.tabview.add("Status & Reports")

        self.setup_tabs()
        # scaling
        self.root.bind("<Configure>", self.on_window_resize)

    def setup_tabs(self):
        # initialize tab components
        self.file_upload_tab = FileUploadTab(
            self.tabview.tab("File Upload"), self.data_processor, self.on_data_updated
        )
        self.templates_tab = TemplatesTab(
            self.tabview.tab("Email Templates"), self.template_manager
        )
        self.send_emails_tab = SendEmailsTab(
            self.tabview.tab("Send Emails"),
            self.email_manager,
            self.data_processor,
            self.template_manager,
            self.on_email_status_updated,
        )

        self.status_tab = StatusTab(
            self.tabview.tab("Status & Reports"), self.email_manager
        )

    def on_window_resize(self, event=None):
        # handle main window resize events
        if event and event.widget == self.root:
            # update title font size based on window width
            try:
                window_width = self.root.winfo_width()
                if window_width > 100:  # only if window is properly initialized
                    # adjust font scaling based on window size
                    window_scale = min(
                        1.3, max(0.9, window_width / (1200 * self.dpi_scale))
                    )
                    adjusted_font_size = self.get_scaled_font_size(24) * window_scale
                    # find and update title label
                    for widget in self.main_frame.winfo_children():
                        if isinstance(
                            widget, ctk.CTkLabel
                        ) and "Apprentice Email Automation" in str(widget.cget("text")):

                            widget.configure(
                                font=ctk.CTkFont(
                                    size=int(adjusted_font_size), weight="bold"
                                )
                            )
                            break
            except:
                pass

    def on_data_updated(self):
        # callback when data is updated
        if self.send_emails_tab:
            self.send_emails_tab.update_data_status()
        if self.status_tab:
            self.status_tab.update_display()

    def on_email_status_updated(self):
        # callback when email status is updated
        if self.status_tab:
            self.status_tab.update_display()

    def run(self):
        # application launch
        self.root.mainloop()
