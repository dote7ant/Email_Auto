import customtkinter as ctk
from tkinter import messagebox


class TemplatesTab:
    def __init__(self, parent, template_manager):
        self.parent = parent
        self.template_manager = template_manager

        self.setup_ui()

    def setup_ui(self):
        # template selection
        template_select_frame = ctk.CTkFrame(self.parent)
        template_select_frame.pack(fill="x", padx=20, pady=20)

        select_label = ctk.CTkLabel(
            template_select_frame,
            text="Select Template to Edit",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        select_label.pack(pady=(10, 5))

        self.template_var = ctk.StringVar(value="significantly")
        template_menu = ctk.CTkOptionMenu(
            template_select_frame,
            values=self.template_manager.get_template_names(),
            variable=self.template_var,
            command=self.load_template,
        )
        template_menu.pack(pady=10)

        # template editing
        edit_frame = ctk.CTkFrame(self.parent)
        edit_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # subject
        subject_label = ctk.CTkLabel(
            edit_frame, text="Subject:", font=ctk.CTkFont(size=14, weight="bold")
        )
        subject_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.subject_entry = ctk.CTkEntry(
            edit_frame, height=40, font=ctk.CTkFont(size=12)
        )
        self.subject_entry.pack(fill="x", padx=10, pady=(0, 10))

        # body
        body_label = ctk.CTkLabel(
            edit_frame, text="Body:", font=ctk.CTkFont(size=14, weight="bold")
        )
        body_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.body_text = ctk.CTkTextbox(
            edit_frame, height=300, font=ctk.CTkFont(size=11)
        )
        self.body_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # save button
        save_button = ctk.CTkButton(
            edit_frame,
            text="Save Template",
            command=self.save_template,
            width=150,
            height=35,
        )
        save_button.pack(pady=10)

        # load initial template
        self.load_template("significantly")

    def load_template(self, template_name):
        # for editing
        template = self.template_manager.get_template(template_name)

        self.subject_entry.delete(0, "end")
        self.subject_entry.insert(0, template.get("subject", ""))

        self.body_text.delete("1.0", "end")
        self.body_text.insert("1.0", template.get("body", ""))

    def save_template(self):
        # save edited template
        template_name = self.template_var.get()
        subject = self.subject_entry.get()
        body = self.body_text.get("1.0", "end-1c")

        if self.template_manager.update_template(template_name, subject, body):
            messagebox.showinfo(
                "Success", f"Template '{template_name}' saved successfully!"
            )
        else:
            messagebox.showerror("Error", "Failed to save template!")
