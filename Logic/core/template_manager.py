import json
import os
from datetime import datetime, timedelta


class TemplateManager:
    def __init__(self):
        self.email_templates = {
            "significantly": {
                "subject": "Attendance and OTJ Logging - Action Required",
                "body": """Hi {name},

I hope you are doing well.

I am reaching out regarding your engagement with the programme. Our records show that it has been {last_attended} days since your last attendance, and you are currently {off_the_job} behind on your Off-the-Job (OTJ) training hours. This places you significantly off track, as both attendance and OTJ logging are key metrics we use to monitor learner engagement.

As there has been no response to previous messages and no improvement in your engagement, I have copied in, your apprentice manager to this email for visibility. We now need to arrange a meeting to discuss how you plan to get back on track. As discussed during the launch meeting, logging OTJ hours on a weekly basis is a mandatory requirement to ensure compliance with government regulations.

Your prompt attention to this matter is appreciated.

Your Coach,""",
            },
            "moderately": {
                "subject": "OTJ Logging - Power Hour Session",
                "body": """Hello {name},

I hope you are doing well.

Our records show you are currently {off_the_job} hours behind on your Off-the-Job (OTJ) training hours. As discussed during the launch meeting, logging OTJ hours on a weekly basis is mandatory to maintain compliance with government regulations.

To help you get back on track, we've scheduled an OTJ Power Hour session on {power_hour_date}, during which you will log your outstanding hours.

Opt-out: If you log all your OTJ hours before the session, you won't need to attend.

Required attendance: If your hours remain outstanding, attendance will be mandatory.

Please reach out if you have any questions or if you anticipate any difficulty logging your hours before the session.

Your coach,""",
            },
            "slightly": {
                "subject": "OTJ Logging Required",
                "body": """Hello {name},

I hope you are doing well.

I am reaching out regarding your Off-the-Job (OTJ) training hours. Our records show that you are currently {off_the_job} hours behind on your OTJ logging.

As discussed during the launch meetings, weekly tracking OTJ hours is a key requirement to ensure we remain compliant with government regulations.

To avoid further escalation, I ask that you log the remaining hours by {deadline_date}. This will help us stay on track and avoid the need for involvement from the compliance team.

Please let me know if you need any support with this.

Your coach,""",
            },
            "on_track": {
                "subject": "Great Progress - Keep It Up!",
                "body": """Hello {name},

I hope you are doing well.

I wanted to reach out to acknowledge your excellent progress with your Off-the-Job (OTJ) training hours and attendance. You are currently on track with your learning programme, which is fantastic!

Keep up the great work, and please don't hesitate to reach out if you need any support or have any questions.

Your coach,""",
            },
        }

        self.templates_file = "email_templates.json"
        self.load_templates()

    def load_templates(self):
        # load templates from file
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, "r") as f:
                    saved_templates = json.load(f)
                    # update only if the saved templates are valid
                    for name, template in saved_templates.items():
                        if self._validate_template_structure(template):
                            self.email_templates[name] = template
            except Exception as e:
                print(f"Error loading templates: {e}")

    def _validate_template_structure(self, template):
        # validate that a template has the required structure
        return (
            isinstance(template, dict)
            and "subject" in template
            and "body" in template
            and isinstance(template["subject"], str)
            and isinstance(template["body"], str)
        )

    def save_templates(self):
        try:
            with open(self.templates_file, "w") as f:
                json.dump(self.email_templates, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving templates: {e}")
            return False

    def get_template(self, template_name):
        return self.email_templates.get(template_name, {})

    def get_all_templates(self):
        return self.email_templates.copy()

    def update_template(self, template_name, subject, body):
        if not subject or not body:
            return False, "Subject and body cannot be empty"

        self.email_templates[template_name] = {"subject": subject, "body": body}
        success = self.save_templates()
        return success, (
            "Template updated successfully" if success else "Failed to save template"
        )

    def get_template_names(self):
        return list(self.email_templates.keys())

    def determine_template_type(self, record):
        # use preprocessed category if available
        if "off_track_category" in record:
            category = record["off_track_category"]
            # map to template names if needed
            if category in self.email_templates:
                return category

        # fallback to manual calculation for backward compatibility
        hours_behind = record.get("hours_behind", record.get("off_the_job", 0))
        days_absent = record.get("days_absent", record.get("last_attended", 0))

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

    def replace_placeholders(self, text, record):
        # replace placeholders in email template with actual data
        if not text:
            return ""

        replacements = self._generate_replacements(record)

        result = text
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, str(value))

        return result

    def _generate_replacements(self, record):
        # generate replacement dictionary for placeholders
        replacements = {}

        # Direct field replacements
        for key, value in record.items():
            placeholder = f"{{{key}}}"
            replacements[placeholder] = str(value) if value is not None else ""

        # calculated/derived replacements
        current_date = datetime.now()

        # power hour date (5 days from today) - matching sample logic
        power_hour_date = current_date + timedelta(days=5)
        replacements["{power_hour_date}"] = power_hour_date.strftime("%Y-%m-%d")

        # deadline date (one week from today)
        deadline_date = current_date + timedelta(days=7)
        replacements["{deadline_date}"] = deadline_date.strftime("%Y-%m-%d")

        # handle name fields with priority for first_name
        first_name = record.get("first_name", "")
        if not first_name:
            # fallback to full name and extract first name
            full_name = record.get("name", record.get("Name", "there"))
            first_name = (
                full_name.split()[0] if full_name and full_name != "there" else "there"
            )

        replacements["{first_name}"] = first_name
        replacements["{name}"] = record.get("name", record.get("Name", first_name))

        # email field
        replacements["{email}"] = record.get(
            "email", record.get("Email", record.get("email_address", ""))
        )

        # handle hours and days with better formatting
        hours_behind = record.get("off_the_job", record.get("hours_behind", 0))
        days_absent = record.get("last_attended", record.get("days_absent", 0))

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

        # Pluralization helpers
        replacements["{hours_plural}"] = "hour" if hours_behind == 1 else "hours"
        replacements["{days_plural}"] = "day" if days_absent == 1 else "days"

        return replacements

    def validate_template(self, template_name):
        # validate that a template has required fields
        template = self.get_template(template_name)

        if not template:
            return False, f"Template '{template_name}' not found"

        if not template.get("subject"):
            return False, f"Template '{template_name}' missing subject"

        if not template.get("body"):
            return False, f"Template '{template_name}' missing body"

        return True, "Template is valid"

    def get_template_preview(self, template_name, sample_record=None):
        # get a preview of a template with sample data
        template = self.get_template(template_name)

        if not template:
            return None

        # Use sample record or create default sample
        if not sample_record:
            sample_record = {
                "name": "old new",
                "email": "old.new@gmail.com",
                "off_the_job": 25,
                "last_attended": 15,
            }

        preview = {
            "subject": self.replace_placeholders(template["subject"], sample_record),
            "body": self.replace_placeholders(template["body"], sample_record),
        }

        return preview

    def export_templates(self, file_path):
        # export templates to a file
        try:
            with open(file_path, "w") as f:
                json.dump(self.email_templates, f, indent=2)
            return True, f"Templates exported to {file_path}"
        except Exception as e:
            return False, f"Failed to export templates: {str(e)}"

    def import_templates(self, file_path):
        try:
            with open(file_path, "r") as f:
                imported_templates = json.load(f)

            # validate imported templates
            for name, template in imported_templates.items():
                if (
                    not isinstance(template, dict)
                    or "subject" not in template
                    or "body" not in template
                ):
                    return False, f"Invalid template format for '{name}'"

            self.email_templates.update(imported_templates)
            self.save_templates()

            return True, f"Templates imported from {file_path}"
        except Exception as e:
            return False, f"Failed to import templates: {str(e)}"
