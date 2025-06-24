import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time
from datetime import datetime


class EmailManager:
    def __init__(self):
        self.email_status = {"sent": 0, "failed": 0, "total": 0}
        self.is_sending = False
        self.failed_emails = []
        self.sending_log = []
        self.smtp_config = {}

    def configure(self, config):
        """Configure SMTP settings"""
        self.smtp_config = config

    def reset_status(self):
        # reset email sending status"""
        self.email_status = {"sent": 0, "failed": 0, "total": 0}
        self.failed_emails = []
        self.sending_log = []

    def send_bulk_emails(self, data, templates, progress_callback=None):
        """
        send bulk emails with progress callback
        this method is used by the UI for synchronous sending
        """
        try:
            self.is_sending = True
            self.reset_status()
            self.email_status["total"] = len(data)

            # connect to SMTP server
            server = smtplib.SMTP(
                self.smtp_config["smtp_server"], self.smtp_config["smtp_port"]
            )
            server.starttls()
            server.login(
                self.smtp_config["sender_email"], self.smtp_config["sender_password"]
            )

            for i, record in enumerate(data):
                try:
                    # determine template type using the template manager approach
                    template_type = self._determine_template_type(record)
                    template = templates.get(
                        template_type, templates.get("on_track", {})
                    )

                    if not template:
                        raise Exception(f"No template found for type: {template_type}")

                    # create email
                    msg = MIMEMultipart()
                    msg["From"] = self.smtp_config["sender_email"]
                    msg["To"] = record.get("email", "")

                    # replace placeholders in subject and body
                    subject = self._replace_placeholders(
                        template.get("subject", ""), record
                    )
                    body = self._replace_placeholders(template.get("body", ""), record)

                    msg["Subject"] = subject
                    msg.attach(MIMEText(body, "plain"))

                    # send email
                    server.sendmail(
                        self.smtp_config["sender_email"],
                        record.get("email", ""),
                        msg.as_string(),
                    )

                    self.email_status["sent"] += 1
                    self.sending_log.append(
                        {
                            "email": record.get("email", ""),
                            "name": record.get("name", "Unknown"),
                            "status": "sent",
                            "template": template_type,
                            "timestamp": datetime.now(),
                        }
                    )

                except Exception as e:
                    self.email_status["failed"] += 1
                    self.failed_emails.append(
                        {
                            "email": record.get("email", ""),
                            "name": record.get("name", "Unknown"),
                            "error": str(e),
                        }
                    )
                    self.sending_log.append(
                        {
                            "email": record.get("email", ""),
                            "name": record.get("name", "Unknown"),
                            "status": "failed",
                            "error": str(e),
                            "timestamp": datetime.now(),
                        }
                    )

                # update progress
                if progress_callback:
                    current_email = (
                        f"{record.get('name', 'Unknown')} ({record.get('email', '')})"
                    )
                    progress_callback(i + 1, len(data), current_email)

                # delay to prevent overwhelming the server
                time.sleep(0.1)

            server.quit()

        except Exception as e:
            print(f"SMTP Error: {e}")
            # add any remaining emails as failed if server connection failed
            remaining_count = (
                self.email_status["total"]
                - self.email_status["sent"]
                - self.email_status["failed"]
            )
            self.email_status["failed"] += remaining_count
        finally:
            self.is_sending = False

    def send_emails(
        self,
        data,
        template_manager,
        smtp_config,
        progress_callback=None,
        completion_callback=None,
    ):
        # send emails in a separate thread (legacy method for backward compatibility)

        def send_thread():
            try:
                self.is_sending = True
                self.reset_status()
                self.email_status["total"] = len(data)

                # connect to SMTP server
                server = smtplib.SMTP(smtp_config["server"], smtp_config["port"])
                server.starttls()
                server.login(smtp_config["email"], smtp_config["password"])

                for i, record in enumerate(data):
                    try:
                        # determine template type
                        template_type = template_manager.determine_template_type(record)
                        template = template_manager.get_template(template_type)

                        # create email
                        msg = MIMEMultipart()
                        msg["From"] = smtp_config["email"]
                        msg["To"] = record.get("email", "")
                        msg["Subject"] = template_manager.replace_placeholders(
                            template["subject"], record
                        )

                        body = template_manager.replace_placeholders(
                            template["body"], record
                        )
                        msg.attach(MIMEText(body, "plain"))

                        # send email
                        server.sendmail(
                            smtp_config["email"],
                            record.get("email", ""),
                            msg.as_string(),
                        )

                        self.email_status["sent"] += 1
                        self.sending_log.append(
                            {
                                "email": record.get("email", ""),
                                "name": record.get("name", "Unknown"),
                                "status": "sent",
                                "template": template_type,
                                "timestamp": datetime.now(),
                            }
                        )

                    except Exception as e:
                        self.email_status["failed"] += 1
                        self.failed_emails.append(
                            {
                                "email": record.get("email", ""),
                                "name": record.get("name", "Unknown"),
                                "error": str(e),
                            }
                        )
                        self.sending_log.append(
                            {
                                "email": record.get("email", ""),
                                "name": record.get("name", "Unknown"),
                                "status": "failed",
                                "error": str(e),
                                "timestamp": datetime.now(),
                            }
                        )

                    # update progress
                    if progress_callback:
                        progress_callback(i + 1, len(data))

                    # delay to prevent overwhelming the server
                    time.sleep(0.1)

                server.quit()

            except Exception as e:
                print(f"SMTP Error: {e}")
            finally:
                self.is_sending = False
                if completion_callback:
                    completion_callback()

        threading.Thread(target=send_thread, daemon=True).start()

    def _determine_template_type(self, record):

        if "off_track_category" in record:
            category = record["off_track_category"]
            # ensure the category maps to a valid template
            valid_categories = ["significantly", "moderately", "slightly", "on_track"]
            if category in valid_categories:
                return category

        # fallback to manual calculation for backward compatibility
        hours_behind = record.get("hours_behind", record.get("off_the_job", 0))
        days_absent = record.get("days_absent", record.get("last_attended", 0))

        # convert to numeric values if they're strings
        try:
            hours_behind = int(hours_behind) if hours_behind else 0
            days_absent = int(days_absent) if days_absent else 0
        except (ValueError, TypeError):
            hours_behind = 0
            days_absent = 0

        if hours_behind >= 30 and days_absent > 30:
            return "significantly"
        elif hours_behind >= 15:
            return "moderately"
        elif hours_behind > 10:
            return "slightly"
        else:
            return "on_track"

    def _replace_placeholders(self, text, record):
        if not text:
            return ""

        # generate comprehensive replacement dictionary
        replacements = self._generate_replacements(record)

        result = text
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, str(value))

        return result

    def _generate_replacements(self, record):
        # generate comprehensive replacement dictionary for placeholders
        from datetime import datetime, timedelta

        replacements = {}

        # direct field replacements
        for key, value in record.items():
            placeholder = f"{{{key}}}"
            replacements[placeholder] = str(value) if value is not None else ""

        # calculated/derived replacements
        current_date = datetime.now()

        # power hour date (5 days from today)
        power_hour_date = current_date + timedelta(days=5)
        replacements["{power_hour_date}"] = power_hour_date.strftime("%A, %B %d, %Y")

        # deadline date (one week from today)
        deadline_date = current_date + timedelta(days=7)
        replacements["{deadline_date}"] = deadline_date.strftime("%A, %B %d, %Y")

        # handle common field variations and defaults
        replacements["{name}"] = record.get(
            "name", record.get("Name", record.get("apprentice_name", "there"))
        )
        replacements["{email}"] = record.get(
            "email", record.get("Email", record.get("email_address", ""))
        )

        # manager information
        replacements["{manager_name}"] = record.get(
            "manager_name", record.get("Manager", "your manager")
        )
        replacements["{manager_email}"] = record.get(
            "manager_email", record.get("manager_email_address", "")
        )

        # handle hours and days with better formatting
        hours_behind = record.get("off_the_job", record.get("hours_behind", 0))
        days_absent = record.get("last_attended", record.get("days_absent", 0))

        # ensure numeric values
        try:
            hours_behind = int(hours_behind) if hours_behind else 0
            days_absent = int(days_absent) if days_absent else 0
        except (ValueError, TypeError):
            hours_behind = 0
            days_absent = 0

        replacements["{off_the_job}"] = str(hours_behind)
        replacements["{hours_behind}"] = str(hours_behind)
        replacements["{last_attended}"] = str(days_absent)
        replacements["{days_absent}"] = str(days_absent)

        replacements["{hours_plural}"] = "hour" if hours_behind == 1 else "hours"
        replacements["{days_plural}"] = "day" if days_absent == 1 else "days"

        return replacements

    def get_status(self):
        # get current email sending status
        return self.email_status.copy()

    def get_failed_emails(self):
        # get list of failed emails
        return self.failed_emails.copy()

    def get_sending_log(self):
        # get complete sending log
        return self.sending_log.copy()

    def is_currently_sending(self):
        # check if emails are currently being sent
        return self.is_sending

    def get_success_rate(self):
        # calculate and return success rate as percentage
        if self.email_status["total"] == 0:
            return 0.0
        return (self.email_status["sent"] / self.email_status["total"]) * 100

    def generate_report(self):
        # generate detailed report
        report = (
            f"Email Sending Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        report += "=" * 50 + "\n\n"
        report += f"Total emails to send: {self.email_status['total']}\n"
        report += f"Successfully sent: {self.email_status['sent']}\n"
        report += f"Failed to send: {self.email_status['failed']}\n"

        if self.email_status["total"] > 0:
            success_rate = self.get_success_rate()
            report += f"Success rate: {success_rate:.1f}%\n\n"

        if self.failed_emails:
            report += "Failed Emails:\n"
            report += "-" * 20 + "\n"
            for failed in self.failed_emails:
                report += f"• {failed['name']} ({failed['email']}): {failed['error']}\n"
            report += "\n"

        if self.email_status["failed"] > 0:
            report += "Common failure reasons:\n"
            report += "- Invalid email addresses\n"
            report += "- SMTP server issues\n"
            report += "- Network connectivity problems\n"
            report += "- Email provider limitations\n"
            report += "- Authentication issues\n"

        return report

    def get_template_usage_stats(self):
        # get statistics on which templates were used
        template_stats = {}
        for log_entry in self.sending_log:
            if log_entry["status"] == "sent":
                template = log_entry.get("template", "unknown")
                template_stats[template] = template_stats.get(template, 0) + 1
        return template_stats

    def export_sending_log(self, file_path):
        # export sending log to CSV file
        try:
            import csv

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                if not self.sending_log:
                    return False, "No sending log data to export"

                fieldnames = [
                    "timestamp",
                    "email",
                    "name",
                    "status",
                    "template",
                    "error",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for log_entry in self.sending_log:
                    row = {
                        "timestamp": log_entry["timestamp"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "email": log_entry.get("email", ""),
                        "name": log_entry.get("name", ""),
                        "status": log_entry.get("status", ""),
                        "template": log_entry.get("template", ""),
                        "error": log_entry.get("error", ""),
                    }
                    writer.writerow(row)

            return True, f"Sending log exported to {file_path}"
        except Exception as e:
            return False, f"Failed to export sending log: {str(e)}"
