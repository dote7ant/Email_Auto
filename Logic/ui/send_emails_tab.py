import customtkinter as ctk
from tkinter import messagebox
import threading
from ui.sending_splash import SendingSplash


class SendEmailsTab:
    def __init__(
        self, parent, email_manager, data_processor, template_manager, status_callback
    ):
        self.parent = parent
        self.email_manager = email_manager
        self.data_processor = data_processor
        self.template_manager = template_manager
        self.status_callback = status_callback

        self.smtp_server = None
        self.smtp_port = None
        self.sender_email = None
        self.sender_password = None
        self.send_progress = None
        self.progress_label = None
        self.send_button = None
        self.sending_splash = None

        self.setup_ui()

    def setup_ui(self):
        # email configuration
        config_frame = ctk.CTkFrame(self.parent)
        config_frame.pack(fill="x", padx=20, pady=20)

        config_label = ctk.CTkLabel(
            config_frame,
            text="Email Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        config_label.pack(pady=(10, 10))

        # SMTP settings
        smtp_frame = ctk.CTkFrame(config_frame)
        smtp_frame.pack(fill="x", padx=10, pady=10)

        # SMTP Server
        ctk.CTkLabel(smtp_frame, text="SMTP Server:").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        self.smtp_server = ctk.CTkEntry(smtp_frame, placeholder_text="smtp.gmail.com")
        self.smtp_server.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # SMTP Port
        ctk.CTkLabel(smtp_frame, text="Port:").grid(
            row=0, column=2, padx=10, pady=5, sticky="w"
        )
        self.smtp_port = ctk.CTkEntry(smtp_frame, placeholder_text="587", width=80)
        self.smtp_port.grid(row=0, column=3, padx=10, pady=5)

        # email and password
        ctk.CTkLabel(smtp_frame, text="Email:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.sender_email = ctk.CTkEntry(
            smtp_frame, placeholder_text="your-email@domain.com"
        )
        self.sender_email.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(smtp_frame, text="Password:").grid(
            row=1, column=2, padx=10, pady=5, sticky="w"
        )
        self.sender_password = ctk.CTkEntry(
            smtp_frame, placeholder_text="password", show="*"
        )
        self.sender_password.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        smtp_frame.grid_columnconfigure(1, weight=1)
        smtp_frame.grid_columnconfigure(3, weight=1)

        # send emails section
        send_frame = ctk.CTkFrame(self.parent)
        send_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        send_label = ctk.CTkLabel(
            send_frame, text="Send Emails", font=ctk.CTkFont(size=16, weight="bold")
        )
        send_label.pack(pady=(10, 10))

        # progress section
        progress_frame = ctk.CTkFrame(send_frame)
        progress_frame.pack(fill="x", padx=10, pady=10)

        self.send_progress = ctk.CTkProgressBar(progress_frame, width=400)
        self.send_progress.pack(pady=10)
        self.send_progress.set(0)

        self.progress_label = ctk.CTkLabel(
            progress_frame, text="Ready to send emails", font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=5)

        # send button
        self.send_button = ctk.CTkButton(
            send_frame,
            text="Send All Emails",
            command=self.send_emails,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.send_button.pack(pady=20)

    def update_data_status(self):
        # update the UI based on data availability
        data_count = len(self.data_processor.get_processed_data())
        if data_count > 0:
            self.progress_label.configure(text=f"Ready to send {data_count} emails")
        else:
            self.progress_label.configure(text="No data loaded")

    def send_emails(self):
        # initiate email sending process
        if not self.data_processor.get_processed_data():
            messagebox.showerror("Error", "Please upload a data file first!")
            return

        if not self.sender_email.get() or not self.sender_password.get():
            messagebox.showerror("Error", "Please enter email credentials!")
            return

        # configure email manager
        config = {
            "smtp_server": self.smtp_server.get() or "smtp.gmail.com",
            "smtp_port": int(self.smtp_port.get() or "587"),
            "sender_email": self.sender_email.get(),
            "sender_password": self.sender_password.get(),
        }

        self.email_manager.configure(config)

        # show sending splash
        self.sending_splash = SendingSplash(self.parent, self.on_sending_complete)

        # start sending in a separate thread
        threading.Thread(target=self._send_emails_thread, daemon=True).start()

    def _send_emails_thread(self):
        # send emails in a separate thread
        try:
            data = self.data_processor.get_processed_data()
            templates = self.template_manager.get_all_templates()

            self.email_manager.send_bulk_emails(
                data, templates, progress_callback=self.update_sending_progress
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send emails: {str(e)}")
        finally:
            self.parent.after(0, self.on_sending_complete)

    def update_sending_progress(self, current, total, current_email=""):
        if self.sending_splash:
            self.sending_splash.update_progress(current, total, current_email)

        if self.status_callback:
            self.status_callback()

    def on_sending_complete(self):
        # handle sending completion
        if self.sending_splash:
            self.sending_splash.close()
            self.sending_splash = None

        # show completion message
        status = self.email_manager.get_status()
        messagebox.showinfo(
            "Email Sending Complete",
            f"Emails sent successfully!\n\n"
            f"Total: {status['total']}\n"
            f"Sent: {status['sent']}\n"
            f"Failed: {status['failed']}",
        )

        self.update_progress_display()

    def update_progress_display(self):
        status = self.email_manager.get_status()

        if status["total"] > 0:
            progress = (status["sent"] + status["failed"]) / status["total"]
            self.send_progress.set(progress)
            self.progress_label.configure(
                text=f"Complete: {status['sent']} sent, {status['failed']} failed"
            )
