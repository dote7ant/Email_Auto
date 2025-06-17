import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk


class FileUploadTab:
    def __init__(self, parent, data_processor, callback=None):
        self.parent = parent
        self.data_processor = data_processor
        self.callback = callback
        self.setup_ui()

    def setup_ui(self):
        # file upload section
        upload_frame = ctk.CTkFrame(self.parent)
        upload_frame.pack(fill="x", padx=20, pady=20)
        upload_label = ctk.CTkLabel(
            upload_frame,
            text="Upload Apprentice Data File",
            font=ctk.CTkFont(size=18, weight="bold"),
        )

        upload_label.pack(pady=(20, 10))
        upload_button = ctk.CTkButton(
            upload_frame,
            text="Choose File",
            command=self.upload_file,
            width=200,
            height=40,
        )

        upload_button.pack(pady=10)
        self.file_label = ctk.CTkLabel(
            upload_frame, text="No file selected", font=ctk.CTkFont(size=12)
        )
        self.file_label.pack(pady=(5, 20))

        # data preview section
        preview_frame = ctk.CTkFrame(self.parent)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        preview_label = ctk.CTkLabel(
            preview_frame, text="Data Preview", font=ctk.CTkFont(size=16, weight="bold")
        )
        preview_label.pack(pady=(10, 5))

        # create treeview for data preview
        self.tree_frame = ctk.CTkFrame(preview_frame)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def upload_file(self):
        # handle file upload
        file_path = filedialog.askopenfilename(
            title="Select Apprentice Data File",
            filetypes=[
                ("All Supported Files", "*.xlsx *.xls *.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
            ],
        )
        if file_path:
            success, message = self.data_processor.load_file(file_path)
            if success:
                self.file_label.configure(text=self.data_processor.get_file_info())
                self.create_data_preview()
                messagebox.showinfo("Success", message)
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Error", message)

    def create_data_preview(self):
        # clear existing tree
        for widget in self.tree_frame.winfo_children():
            widget.destroy()

        df = self.data_processor.get_data_preview()
        if df is None:
            return

        # create new treeview
        columns = list(df.columns)
        tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=8)

        # configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, minwidth=50)

        # insert data
        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        # add scrollbars
        v_scrollbar = ttk.Scrollbar(
            self.tree_frame, orient="vertical", command=tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            self.tree_frame, orient="horizontal", command=tree.xview
        )
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        # pack widgets
        tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
