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

        # Category-specific UI elements
        self.category_frames = {}
        self.category_progress_bars = {}
        self.category_labels = {}
        self.category_buttons = {}

        self.setup_ui()

    def setup_ui(self):
        # Create main scrollable frame
        main_scrollable = ctk.CTkScrollableFrame(self.parent)
        main_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Email configuration
        config_frame = ctk.CTkFrame(main_scrollable)
        config_frame.pack(fill="x", padx=10, pady=10)

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

        # Email and password
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

        # Send All Emails section
        send_all_frame = ctk.CTkFrame(main_scrollable)
        send_all_frame.pack(fill="x", padx=10, pady=10)

        send_all_label = ctk.CTkLabel(
            send_all_frame,
            text="Send All Emails",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        send_all_label.pack(pady=(10, 10))

        # Overall progress section
        overall_progress_frame = ctk.CTkFrame(send_all_frame)
        overall_progress_frame.pack(fill="x", padx=10, pady=10)

        self.send_progress = ctk.CTkProgressBar(overall_progress_frame, width=400)
        self.send_progress.pack(pady=10)
        self.send_progress.set(0)

        self.progress_label = ctk.CTkLabel(
            overall_progress_frame,
            text="Ready to send emails",
            font=ctk.CTkFont(size=12),
        )
        self.progress_label.pack(pady=5)

        # Send all button
        self.send_button = ctk.CTkButton(
            send_all_frame,
            text="Send All Emails",
            command=self.send_all_emails,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.send_button.pack(pady=20)

        # Category-specific sections
        self.setup_category_sections(main_scrollable)

    def setup_category_sections(self, parent):
        """Setup individual category sections for targeted email sending"""
        categories = {
            "significantly": {
                "title": "Significantly Off-Track",
                "description": "Apprentices who are significantly behind (>30 hours or >5 days absent)",
                "color": "#ff4444",
            },
            "moderately": {
                "title": "Moderately Off-Track",
                "description": "Apprentices who are moderately behind (10-30 hours or 2-5 days absent)",
                "color": "#ff8800",
            },
            "slightly": {
                "title": "Slightly Off-Track",
                "description": "Apprentices who are slightly behind (<10 hours or <2 days absent)",
                "color": "#ffaa00",
            },
        }

        for category_id, category_info in categories.items():
            # Create frame for this category
            category_frame = ctk.CTkFrame(parent)
            category_frame.pack(fill="x", padx=10, pady=10)
            self.category_frames[category_id] = category_frame

            # Category header
            header_frame = ctk.CTkFrame(category_frame)
            header_frame.pack(fill="x", padx=10, pady=(10, 5))

            title_label = ctk.CTkLabel(
                header_frame,
                text=category_info["title"],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=category_info["color"],
            )
            title_label.pack(side="left", padx=10, pady=5)

            # Category count label
            count_label = ctk.CTkLabel(
                header_frame,
                text="0 recipients",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            )
            count_label.pack(side="right", padx=10, pady=5)
            self.category_labels[f"{category_id}_count"] = count_label

            # Description
            desc_label = ctk.CTkLabel(
                category_frame,
                text=category_info["description"],
                font=ctk.CTkFont(size=11),
                text_color="gray",
                wraplength=600,
            )
            desc_label.pack(padx=10, pady=(0, 10))

            # Progress section for this category
            progress_frame = ctk.CTkFrame(category_frame)
            progress_frame.pack(fill="x", padx=10, pady=5)

            progress_bar = ctk.CTkProgressBar(progress_frame, width=300)
            progress_bar.pack(pady=5)
            progress_bar.set(0)
            self.category_progress_bars[category_id] = progress_bar

            progress_label = ctk.CTkLabel(
                progress_frame, text="Ready to send", font=ctk.CTkFont(size=11)
            )
            progress_label.pack(pady=2)
            self.category_labels[category_id] = progress_label

            # Send button for this category
            send_button = ctk.CTkButton(
                category_frame,
                text=f"Send {category_info['title']} Emails",
                command=lambda cat=category_id: self.send_category_emails(cat),
                width=250,
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=category_info["color"],
                hover_color=self._darken_color(category_info["color"]),
            )
            send_button.pack(pady=(5, 15))
            self.category_buttons[category_id] = send_button

    def _darken_color(self, hex_color):
        """Darken a hex color for hover effect"""
        # Remove # if present
        hex_color = hex_color.lstrip("#")

        # Convert to RGB
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        # Darken by reducing each component by 20%
        darkened_rgb = tuple(int(component * 0.8) for component in rgb)

        # Convert back to hex
        return f"#{darkened_rgb[0]:02x}{darkened_rgb[1]:02x}{darkened_rgb[2]:02x}"

    def get_category_data(self, category):
        """Get data for a specific category using data_processor"""
        return self.data_processor.get_category_data(category)

    def update_data_status(self):
        """Update the UI based on data availability"""
        all_data = self.data_processor.get_processed_data()
        total_count = len(all_data)

        if total_count > 0:
            self.progress_label.configure(text=f"Ready to send {total_count} emails")

            # Update category counts
            for category in ["significantly", "moderately", "slightly"]:
                category_data = self.get_category_data(category)
                count = len(category_data)

                count_label = self.category_labels.get(f"{category}_count")
                if count_label:
                    count_label.configure(
                        text=f"{count} recipient{'s' if count != 1 else ''}"
                    )

                progress_label = self.category_labels.get(category)
                if progress_label:
                    if count > 0:
                        progress_label.configure(text=f"Ready to send {count} emails")
                    else:
                        progress_label.configure(text="No recipients in this category")

                # Enable/disable buttons based on data availability
                button = self.category_buttons.get(category)
                if button:
                    button.configure(state="normal" if count > 0 else "disabled")

            # Enable/disable the main send button
            self.send_button.configure(state="normal")
        else:
            self.progress_label.configure(text="No data loaded")
            self.send_button.configure(state="disabled")

            # Reset all category displays
            for category in ["significantly", "moderately", "slightly"]:
                count_label = self.category_labels.get(f"{category}_count")
                if count_label:
                    count_label.configure(text="0 recipients")

                progress_label = self.category_labels.get(category)
                if progress_label:
                    progress_label.configure(text="No data loaded")

                button = self.category_buttons.get(category)
                if button:
                    button.configure(state="disabled")

    def send_all_emails(self):
        """Send emails to all categories"""
        if not self.data_processor.get_processed_data():
            messagebox.showerror("Error", "Please upload a data file first!")
            return

        if not self._validate_smtp_config():
            return

        self._initiate_email_sending(self.data_processor.get_processed_data(), "All")

    def send_category_emails(self, category):
        """Send emails to a specific category"""
        category_data = self.get_category_data(category)

        if not category_data:
            messagebox.showwarning(
                "Warning", f"No recipients found for {category} category!"
            )
            return

        if not self._validate_smtp_config():
            return

        category_names = {
            "significantly": "Significantly Off-Track",
            "moderately": "Moderately Off-Track",
            "slightly": "Slightly Off-Track",
        }

        category_name = category_names.get(category, category)
        self._initiate_email_sending(category_data, category_name, category)

    def _validate_smtp_config(self):
        """Validate SMTP configuration"""
        if not self.sender_email.get() or not self.sender_password.get():
            messagebox.showerror("Error", "Please enter email credentials!")
            return False
        return True

    def _initiate_email_sending(self, data, category_name, category_id=None):
        """Initiate the email sending process"""
        # Configure email manager
        config = {
            "smtp_server": self.smtp_server.get() or "smtp.gmail.com",
            "smtp_port": int(self.smtp_port.get() or "587"),
            "sender_email": self.sender_email.get(),
            "sender_password": self.sender_password.get(),
        }

        self.email_manager.configure(config)

        # Show sending splash
        self.sending_splash = SendingSplash(
            self.parent,
            lambda: self.on_sending_complete(category_id),
            title=f"Sending {category_name} Emails"
        )

        # Start sending in a separate thread
        threading.Thread(
            target=self._send_emails_thread, args=(data, category_id), daemon=True
        ).start()

    def _send_emails_thread(self, data, category_id=None):
        """Send emails in a separate thread"""
        try:
            # Get templates - prepare all templates for bulk sending
            templates = self.template_manager.get_all_templates()

            # Filter data based on category if specified
            if category_id:
                # When sending category-specific emails, only send to that category
                filtered_data = [
                    record
                    for record in data
                    if self.template_manager.determine_template_type(record)
                    == category_id
                ]
            else:
                # When sending all emails, include all data
                filtered_data = data

            # Send bulk emails using the email manager
            self.email_manager.send_bulk_emails(
                filtered_data,
                templates,
                progress_callback=lambda current, total, email: self.update_sending_progress(
                    current, total, email, category_id
                ),
            )

        except Exception as e:
            # Use parent.after to ensure messagebox is shown on main thread
            self.parent.after(
                0,
                lambda: messagebox.showerror(
                    "Error", f"Failed to send emails: {str(e)}"
                ),
            )
        finally:
            self.parent.after(0, lambda: self.on_sending_complete(category_id))

    def update_sending_progress(
        self, current, total, current_email="", category_id=None
    ):
        """Update sending progress"""
        if self.sending_splash:
            self.sending_splash.update_progress(current, total, current_email)

        # Update category-specific progress if applicable
        if category_id and category_id in self.category_progress_bars:
            progress = current / total if total > 0 else 0
            self.category_progress_bars[category_id].set(progress)

            if category_id in self.category_labels:
                self.category_labels[category_id].configure(
                    text=f"Sending... {current}/{total}"
                )

        # Update overall progress bar
        if not category_id:  # Only update overall progress when sending all emails
            progress = current / total if total > 0 else 0
            self.send_progress.set(progress)
            self.progress_label.configure(text=f"Sending... {current}/{total}")

        if self.status_callback:
            self.status_callback()

    def on_sending_complete(self, category_id=None):
        """Handle sending completion"""
        if self.sending_splash:
            self.sending_splash.close()
            self.sending_splash = None

        # Show completion message
        status = self.email_manager.get_status()

        category_text = ""
        if category_id:
            category_names = {
                "significantly": "Significantly Off-Track",
                "moderately": "Moderately Off-Track",
                "slightly": "Slightly Off-Track",
            }
            category_text = f" ({category_names.get(category_id, category_id)})"

        messagebox.showinfo(
            "Email Sending Complete",
            f"Emails{category_text} sent successfully!\n\n"
            f"Total: {status['total']}\n"
            f"Sent: {status['sent']}\n"
            f"Failed: {status['failed']}",
        )

        self.update_progress_display(category_id)

    def update_progress_display(self, category_id=None):
        """Update progress display after completion"""
        status = self.email_manager.get_status()

        if status["total"] > 0:
            # Update overall progress
            progress = (status["sent"] + status["failed"]) / status["total"]
            self.send_progress.set(progress)
            self.progress_label.configure(
                text=f"Complete: {status['sent']} sent, {status['failed']} failed"
            )

            # Update category-specific progress if applicable
            if category_id and category_id in self.category_progress_bars:
                self.category_progress_bars[category_id].set(1.0)

                if category_id in self.category_labels:
                    self.category_labels[category_id].configure(
                        text=f"Complete: {status['sent']} sent, {status['failed']} failed"
                    )
