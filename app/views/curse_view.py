from tkinter import messagebox, ttk
from typing import Callable

import customtkinter as ctk


class CurseView:
    """View pentru tab-ul de gestiune a curselor (strict componente UI si mesaje)."""

    def __init__(self, parent):
        self.parent = parent
        self._on_row_select_cb: Callable[[int], None] | None = None
        self._build_ui()

    def _build_ui(self):
        self.parent.grid_columnconfigure(0, weight=3)
        self.parent.grid_columnconfigure(1, weight=1, minsize=300)
        self.parent.grid_rowconfigure(1, weight=1)

        # Bara de filtrare (sus stanga)
        filter_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        filter_frame.grid(row=0, column=0, sticky="ew", padx=(4, 12), pady=(4, 8))

        ctk.CTkLabel(filter_frame, text="Filtreaza dupa data (YYYY-MM-DD):").pack(
            side="left", padx=(0, 8)
        )
        self.entry_filter_date = ctk.CTkEntry(
            filter_frame, width=140, placeholder_text="ex: 2026-11-20"
        )
        self.entry_filter_date.pack(side="left", padx=(0, 8))

        self.btn_filter = ctk.CTkButton(filter_frame, text="Filtreaza", width=90)
        self.btn_filter.pack(side="left", padx=(0, 6))

        self.btn_reset_filter = ctk.CTkButton(
            filter_frame,
            text="Toate / Refresh",
            width=120,
            fg_color="#475569",
            hover_color="#334155",
        )
        self.btn_reset_filter.pack(side="left")

        # Tabelul cu curse (stanga)
        table_container = ctk.CTkFrame(self.parent)
        table_container.grid(row=1, column=0, sticky="nsew", padx=(4, 12), pady=4)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#0F172A",
            rowheight=28,
            fieldbackground="#FFFFFF",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground="#0F172A",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#2563EB")])

        columns = (
            "id_cursa",
            "ruta",
            "tren",
            "data_cursa",
            "ora_plecare",
            "status",
            "intarziere",
            "admin",
        )
        self.tree = ttk.Treeview(
            table_container, columns=columns, show="headings", selectmode="browse"
        )

        headings = [
            ("id_cursa", "ID", 45, "center"),
            ("ruta", "Ruta", 220, "w"),
            ("tren", "Tren", 165, "w"),
            ("data_cursa", "Data", 95, "center"),
            ("ora_plecare", "Ora plecare", 85, "center"),
            ("status", "Status", 85, "center"),
            ("intarziere", "Intarziere (min)", 100, "center"),
            ("admin", "Admin", 115, "w"),
        ]
        for col_id, label, width, anchor in headings:
            self.tree.heading(col_id, text=label)
            self.tree.column(col_id, width=width, anchor=anchor)

        scrollbar_y = ttk.Scrollbar(
            table_container, orient="vertical", command=self.tree.yview
        )
        scrollbar_x = ttk.Scrollbar(
            table_container, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=(6, 0))
        scrollbar_y.grid(row=0, column=1, sticky="ns", pady=(6, 0), padx=(0, 6))
        scrollbar_x.grid(row=1, column=0, sticky="ew", padx=(6, 0), pady=(0, 6))

        self.tree.bind("<<TreeviewSelect>>", self._emit_row_select)

        # Panoul formularului CRUD (dreapta): campuri scrolabile + butoane fixate jos
        form_panel = ctk.CTkFrame(self.parent, corner_radius=10)
        form_panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 4), pady=4)
        form_panel.grid_rowconfigure(0, weight=1)
        form_panel.grid_rowconfigure(1, weight=0)
        form_panel.grid_columnconfigure(0, weight=1)

        form = ctk.CTkScrollableFrame(form_panel, fg_color="transparent")
        form.grid(row=0, column=0, sticky="nsew", padx=4, pady=(6, 2))

        self.lbl_form_title = ctk.CTkLabel(
            form,
            text="Formular Cursa (Adauga / Editeaza)",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.lbl_form_title.pack(pady=(6, 4), padx=10, anchor="w")

        self.lbl_selected_id = ctk.CTkLabel(
            form, text="Selectie: Nicio cursa selectata", text_color="#475569"
        )
        self.lbl_selected_id.pack(pady=(0, 8), padx=10, anchor="w")

        # Admin
        ctk.CTkLabel(form, text="Administrator:").pack(padx=10, anchor="w")
        self.combo_admin = ctk.CTkComboBox(form, values=[], state="readonly")
        self.combo_admin.pack(fill="x", padx=10, pady=(2, 6))

        # Ruta
        ctk.CTkLabel(form, text="Ruta (doar rute active):").pack(padx=10, anchor="w")
        self.combo_ruta = ctk.CTkComboBox(form, values=[], state="readonly")
        self.combo_ruta.pack(fill="x", padx=10, pady=(2, 6))

        # Tren
        ctk.CTkLabel(form, text="Tren (doar trenuri active):").pack(padx=10, anchor="w")
        self.combo_tren = ctk.CTkComboBox(form, values=[], state="readonly")
        self.combo_tren.pack(fill="x", padx=10, pady=(2, 6))

        # Data
        ctk.CTkLabel(form, text="Data cursa (YYYY-MM-DD):").pack(padx=10, anchor="w")
        self.entry_data = ctk.CTkEntry(form, placeholder_text="2026-11-25")
        self.entry_data.pack(fill="x", padx=10, pady=(2, 6))

        # Ora plecare
        ctk.CTkLabel(form, text="Ora plecare (HH:MM:SS):").pack(padx=10, anchor="w")
        self.entry_ora = ctk.CTkEntry(form, placeholder_text="08:30:00")
        self.entry_ora.pack(fill="x", padx=10, pady=(2, 6))

        # Status
        ctk.CTkLabel(form, text="Status:").pack(padx=10, anchor="w")
        self.combo_status = ctk.CTkComboBox(
            form, values=["la timp", "intarziata", "anulata"], state="readonly"
        )
        self.combo_status.set("la timp")
        self.combo_status.pack(fill="x", padx=10, pady=(2, 6))

        # Intarziere
        ctk.CTkLabel(form, text="Minute intarziere:").pack(padx=10, anchor="w")
        self.entry_intarziere = ctk.CTkEntry(form, placeholder_text="0")
        self.entry_intarziere.insert(0, "0")
        self.entry_intarziere.pack(fill="x", padx=10, pady=(2, 8))

        # Butoane CRUD (fixate in partea de jos, mereu vizibile)
        actions_frame = ctk.CTkFrame(form_panel, fg_color="transparent")
        actions_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(4, 10))

        self.btn_create = ctk.CTkButton(
            actions_frame,
            text="Adauga Cursa (CREATE)",
            height=30,
            fg_color="#16A34A",
            hover_color="#15803D",
        )
        self.btn_create.pack(fill="x", pady=3)

        self.btn_update = ctk.CTkButton(
            actions_frame,
            text="Actualizeaza (UPDATE)",
            height=30,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
        )
        self.btn_update.pack(fill="x", pady=3)

        self.btn_delete = ctk.CTkButton(
            actions_frame,
            text="Sterge Cursa (DELETE)",
            height=30,
            fg_color="#DC2626",
            hover_color="#B91C1C",
        )
        self.btn_delete.pack(fill="x", pady=3)

        self.btn_clear = ctk.CTkButton(
            actions_frame,
            text="Curata formular",
            height=30,
            fg_color="#64748B",
            hover_color="#475569",
        )
        self.btn_clear.pack(fill="x", pady=(3, 0))

    def bind_handlers(
        self,
        *,
        on_filter: Callable[[], None],
        on_reset_filter: Callable[[], None],
        on_row_select: Callable[[int], None],
        on_create: Callable[[], None],
        on_update: Callable[[], None],
        on_delete: Callable[[], None],
        on_clear: Callable[[], None],
    ):
        self.btn_filter.configure(command=on_filter)
        self.btn_reset_filter.configure(command=on_reset_filter)
        self._on_row_select_cb = on_row_select
        self.btn_create.configure(command=on_create)
        self.btn_update.configure(command=on_update)
        self.btn_delete.configure(command=on_delete)
        self.btn_clear.configure(command=on_clear)

    def _emit_row_select(self, _event):
        if not self._on_row_select_cb:
            return
        selection = self.tree.selection()
        if not selection:
            return
        self._on_row_select_cb(int(selection[0]))

    def set_reference_options(
        self, rute_vals: list[str], tren_vals: list[str], admin_vals: list[str]
    ):
        self.combo_ruta.configure(values=rute_vals)
        self.combo_tren.configure(values=tren_vals)
        self.combo_admin.configure(values=admin_vals)

        if rute_vals:
            self.combo_ruta.set(rute_vals[0])
        if tren_vals:
            self.combo_tren.set(tren_vals[0])
        if admin_vals:
            self.combo_admin.set(admin_vals[0])

    def set_curse_rows(self, rows: list[dict]):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in rows:
            self.tree.insert(
                "",
                "end",
                iid=str(r["id_cursa"]),
                values=(
                    r["id_cursa"],
                    r["ruta"],
                    r["tren"],
                    r["data_cursa"],
                    r["ora_plecare"],
                    r["status"],
                    r["intarziere_minute"],
                    r["admin_nume"],
                ),
            )

    def get_filter_date(self) -> str:
        return self.entry_filter_date.get().strip()

    def clear_filter_date(self):
        self.entry_filter_date.delete(0, "end")

    def set_selected_label(self, text: str):
        self.lbl_selected_id.configure(text=text)

    def populate_form(
        self,
        *,
        admin_key: str | None,
        ruta_key: str | None,
        tren_key: str | None,
        data_cursa: str,
        ora_plecare: str,
        status: str,
        intarziere_minute: int,
    ):
        if admin_key is not None:
            self.combo_admin.set(admin_key)
        if ruta_key is not None:
            self.combo_ruta.set(ruta_key)
        if tren_key is not None:
            self.combo_tren.set(tren_key)

        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, data_cursa)

        self.entry_ora.delete(0, "end")
        self.entry_ora.insert(0, ora_plecare)

        self.combo_status.set(status)

        self.entry_intarziere.delete(0, "end")
        self.entry_intarziere.insert(0, str(intarziere_minute))

    def get_form_data(self) -> dict[str, str]:
        return {
            "admin_key": self.combo_admin.get(),
            "ruta_key": self.combo_ruta.get(),
            "tren_key": self.combo_tren.get(),
            "data_cursa": self.entry_data.get().strip(),
            "ora_plecare": self.entry_ora.get().strip(),
            "status": self.combo_status.get().strip(),
            "intarziere_text": self.entry_intarziere.get().strip(),
        }

    def clear_form(self):
        self.set_selected_label("Selectie: Nicio cursa selectata")
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        self.entry_data.delete(0, "end")
        self.entry_ora.delete(0, "end")
        self.combo_status.set("la timp")
        self.entry_intarziere.delete(0, "end")
        self.entry_intarziere.insert(0, "0")

    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message)

    def show_warning(self, title: str, message: str):
        messagebox.showwarning(title, message)

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message)

    def ask_confirm(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)
