import customtkinter as ctk
from datetime import datetime


class StatusTab:
    def __init__(self, parent, email_manager):
        self.parent = parent
        self.email_manager = email_manager

        self.total_label = None
        self.sent_label = None
        self.failed_label = None
        self.report_text = None

        self.setup_ui()

    def setup_ui(self):
        # status overview
        status_frame = ctk.CTkFrame(self.parent)
        status_frame.pack(fill="x", padx=20, pady=20)

        status_label = ctk.CTkLabel(
            status_frame,
            text="Email Status Overview",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        status_label.pack(pady=(10, 10))

        # status cards
        cards_frame = ctk.CTkFrame(status_frame)
        cards_frame.pack(fill="x", padx=10, pady=10)

        # total emails card
        total_card = ctk.CTkFrame(cards_frame)
        total_card.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.total_label = ctk.CTkLabel(
            total_card, text="Total Emails\n0", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.total_label.pack(pady=20)

        # sent emails card
        sent_card = ctk.CTkFrame(cards_frame)
        sent_card.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.sent_label = ctk.CTkLabel(
            sent_card,
            text="Sent Successfully\n0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="green",
        )
        self.sent_label.pack(pady=20)

        # failed emails card
        failed_card = ctk.CTkFrame(cards_frame)
        failed_card.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.failed_label = ctk.CTkLabel(
            failed_card,
            text="Failed\n0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="red",
        )
        self.failed_label.pack(pady=20)

        # detailed report
        report_frame = ctk.CTkFrame(self.parent)
        report_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        report_label = ctk.CTkLabel(
            report_frame,
            text="Detailed Report",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        report_label.pack(pady=(10, 5))

        self.report_text = ctk.CTkTextbox(
            report_frame, height=200, font=ctk.CTkFont(size=11)
        )
        self.report_text.pack(fill="both", expand=True, padx=10, pady=10)

    def update_display(self):
        status = self.email_manager.get_status()

        self.total_label.configure(text=f"Total Emails\n{status['total']}")
        self.sent_label.configure(text=f"Sent Successfully\n{status['sent']}")
        self.failed_label.configure(text=f"Failed\n{status['failed']}")

        self.generate_report()

    def generate_report(self):
        # generate detailed report
        status = self.email_manager.get_status()

        report = (
            f"Email Sending Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        report += "=" * 50 + "\n\n"
        report += f"Total emails to send: {status['total']}\n"
        report += f"Successfully sent: {status['sent']}\n"
        report += f"Failed to send: {status['failed']}\n"

        if status["total"] > 0:
            success_rate = status["sent"] / status["total"] * 100
            report += f"Success rate: {success_rate:.1f}%\n\n"

        if status["failed"] > 0:
            report += "Failed emails may be due to:\n"
            report += "- Invalid email addresses\n"
            report += "- SMTP server issues\n"
            report += "- Network connectivity problems\n"
            report += "- Email provider limitations\n"

        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", report)
