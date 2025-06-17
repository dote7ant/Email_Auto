import json
import os
from datetime import datetime, timedelta


class TemplateManager:
    def __init__(self):
        self.email_templates = {
            "significantly": {
                "subject": "Attendance and OTJ Logging - Action Required",
                "body": """Hi [Apprentice's Name],

I hope you are doing well.

I am reaching out regarding your engagement with the programme. Our records show that it has been [Number of days] since your last attendance, and you are currently [Number of hours] behind on your Off-the-Job (OTJ) training hours. This places you significantly off track, as both attendance and OTJ logging are key metrics we use to monitor learner engagement.

As there has been no response to previous messages and no improvement in your engagement, I have copied in [Manager's Name], your apprentice manager, for visibility. We now need to arrange a meeting to discuss how you plan to get back on track. As discussed during the launch meeting, logging OTJ hours on a weekly basis is a mandatory requirement to ensure compliance with government regulations.

Your prompt attention to this matter is appreciated.

Your Coach,""",
            },
            "moderately": {
                "subject": "OTJ Logging - Power Hour Session",
                "body": """Hello [Apprentice's Name],

I hope you are doing well.

Our records show you are currently [No of hours] hours behind on your Off-the-Job (OTJ) training hours. As discussed during the launch meeting, logging OTJ hours on a weekly basis is mandatory to maintain compliance with government regulations.

To help you get back on track, we've scheduled an OTJ Power Hour session on [Date -- 5 days from today], during which you will log your outstanding hours.

• Opt-out: If you log all your OTJ hours before the session, you won't need to attend.
• Required attendance: If your hours remain outstanding, attendance will be mandatory.

Please reach out if you have any questions or if you anticipate any difficulty logging your hours before the session.

Your coach,""",
            },
            "slightly": {
                "subject": "OTJ Logging Required",
                "body": """Hello [Apprentice's Name],

I hope you are doing well.

I am reaching out regarding your Off-the-Job (OTJ) training hours. Our records show that you are currently [No of hours] hours behind on your OTJ logging.

As discussed during the launch meetings, weekly tracking OTJ hours is a key requirement to ensure we remain compliant with government regulations.

To avoid further escalation, I ask that you log the remaining hours by [date - one week after sending the email]. This will help us stay on track and avoid the need for involvement from the compliance team.

Please let me know if you need any support with this.

Your coach,""",
            },
        }

        self.templates_file = "email_templates.json"
        self.load_templates()

    def load_templates(self):
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, "r") as f:
                    saved_templates = json.load(f)
                    self.email_templates.update(saved_templates)
            except Exception as e:
                print(f"Error loading templates: {e}")

    def save_templates(self):
        try:
            with open(self.templates_file, "w") as f:
                json.dump(self.email_templates, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving templates: {e}")
            return False

    def get_template(self, template_name):
        # et a specific template
        return self.email_templates.get(template_name, {})

    def update_template(self, template_name, subject, body):
        # update a template"""
        self.email_templates[template_name] = {"subject": subject, "body": body}
        return self.save_templates()

    def get_template_names(self):
        # get list of available template names
        return list(self.email_templates.keys())

    def determine_template_type(self, record):
        # determine which template to use based on record data
        hours_behind = record.get("hours_behind", 0)
        days_absent = record.get("days_absent", 0)

        if hours_behind > 30 or days_absent > 5:
            return "significantly"
        elif hours_behind > 10 or days_absent > 2:
            return "moderately"
        else:
            return "slightly"

    def replace_placeholders(self, text, record):
        # replace placeholders in email template with actual data
        replacements = {
            "[Apprentice's Name]": record.get("name", "Apprentice"),
            "[App Name]": record.get("name", "Apprentice"),
            "[Number of hours]": str(record.get("hours_behind", 0)),
            "[No of hours]": str(record.get("hours_behind", 0)),
            "[Number of days]": str(record.get("days_absent", 0)),
            "[Manager's Name]": record.get("manager", "Manager"),
            "[Date -- 5 days from today]": (
                datetime.now() + timedelta(days=5)
            ).strftime("%Y-%m-%d"),
            "[date - one week after sending the email]": (
                datetime.now() + timedelta(days=7)
            ).strftime("%Y-%m-%d"),
        }

        for placeholder, value in replacements.items():
            text = text.replace(placeholder, str(value))

        return text
