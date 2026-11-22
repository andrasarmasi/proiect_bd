import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import mysql.connector

from crud_operations import (
    add_cursa,
    delete_cursa,
    get_active_rute,
    get_active_trenuri,
    get_all_admini,
    get_all_curse,
    update_cursa,
)

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class RailwayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aplicatie Feroviara - Gestiune Curse (CRUD)")
        self.geometry("1240x650")
        self.minsize(1020, 560)

        self.selected_cursa_id: int | None = None
        self.rute_map: dict[str, int] = {}
        self.trenuri_map: dict[str, int] = {}
        self.admini_map: dict[str, int] = {}
        self.curse_by_id: dict[int, dict] = {}

        self._build_layout()
        self._load_reference_data()
        self._refresh_table()

    def _build_layout(self):
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E3A8A", height=56)
        header.pack(fill="x", side="top")

        title_lbl = ctk.CTkLabel(
            header,
            text="Sistem Feroviar — Panou de Gestiune (CRUD)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
        )
        title_lbl.pack(side="left", padx=20, pady=12)

        self.tabview = ctk.CTkTabview(self, anchor="nw")
        self.tabview.pack(fill="both", expand=True, padx=16, pady=12)

        self.tab_curse = self.tabview.add("Curse")
        self._build_curse_tab()

    def _build_curse_tab(self):
        self.tab_curse.grid_columnconfigure(0, weight=3)
        self.tab_curse.grid_columnconfigure(1, weight=1)
        self.tab_curse.grid_rowconfigure(1, weight=1)

        # Bara de filtrare (sus stanga)
        filter_frame = ctk.CTkFrame(self.tab_curse, fg_color="transparent")
        filter_frame.grid(row=0, column=0, sticky="ew", padx=(4, 12), pady=(4, 8))

        ctk.CTkLabel(filter_frame, text="Filtreaza dupa data (YYYY-MM-DD):").pack(
            side="left", padx=(0, 8)
        )
        self.entry_filter_date = ctk.CTkEntry(
            filter_frame, width=140, placeholder_text="ex: 2026-11-20"
        )
        self.entry_filter_date.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            filter_frame, text="Filtreaza", width=90, command=self._apply_filter
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            filter_frame,
            text="Toate / Refresh",
            width=120,
            fg_color="#475569",
            hover_color="#334155",
            command=self._reset_filter,
        ).pack(side="left")

        # Tabelul cu curse (stanga)
        table_container = ctk.CTkFrame(self.tab_curse)
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
            ("id_cursa", "ID", 42, "center"),
            ("ruta", "Ruta", 265, "w"),
            ("tren", "Tren", 165, "w"),
            ("data_cursa", "Data", 90, "center"),
            ("ora_plecare", "Ora plecare", 82, "center"),
            ("status", "Status", 82, "center"),
            ("intarziere", "Intarziere (min)", 98, "center"),
            ("admin", "Admin", 110, "w"),
        ]
        for col_id, label, width, anchor in headings:
            self.tree.heading(col_id, text=label)
            self.tree.column(col_id, width=width, minwidth=width, anchor=anchor)

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

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

        # Formularul CRUD (dreapta - compact + scroll automat la redimensionare)
        form = ctk.CTkScrollableFrame(self.tab_curse, corner_radius=10, width=330)
        form.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 4), pady=4)

        self.lbl_form_title = ctk.CTkLabel(
            form,
            text="Formular Cursa (Adauga / Editeaza)",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.lbl_form_title.pack(pady=(8, 2), padx=10, anchor="w")

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

        # Data + Ora pe acelasi rand
        row_datetime = ctk.CTkFrame(form, fg_color="transparent")
        row_datetime.pack(fill="x", padx=10, pady=(2, 6))
        row_datetime.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row_datetime, text="Data (YYYY-MM-DD):").grid(
            row=0, column=0, sticky="w", padx=(0, 4)
        )
        ctk.CTkLabel(row_datetime, text="Ora (HH:MM:SS):").grid(
            row=0, column=1, sticky="w", padx=(4, 0)
        )
        self.entry_data = ctk.CTkEntry(row_datetime, placeholder_text="2026-11-25")
        self.entry_data.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(2, 0))
        self.entry_ora = ctk.CTkEntry(row_datetime, placeholder_text="08:30:00")
        self.entry_ora.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(2, 0))

        # Status + Intarziere pe acelasi rand
        row_status = ctk.CTkFrame(form, fg_color="transparent")
        row_status.pack(fill="x", padx=10, pady=(2, 12))
        row_status.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row_status, text="Status:").grid(
            row=0, column=0, sticky="w", padx=(0, 4)
        )
        ctk.CTkLabel(row_status, text="Intarziere (min):").grid(
            row=0, column=1, sticky="w", padx=(4, 0)
        )
        self.combo_status = ctk.CTkComboBox(
            row_status, values=["la timp", "intarziata", "anulata"], state="readonly"
        )
        self.combo_status.set("la timp")
        self.combo_status.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(2, 0))

        self.entry_intarziere = ctk.CTkEntry(row_status, placeholder_text="0")
        self.entry_intarziere.insert(0, "0")
        self.entry_intarziere.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(2, 0))

        # Butoane CRUD in grila 2x2
        btn_grid = ctk.CTkFrame(form, fg_color="transparent")
        btn_grid.pack(fill="x", padx=10, pady=(4, 10))
        btn_grid.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_grid,
            text="Adauga (CREATE)",
            fg_color="#16A34A",
            hover_color="#15803D",
            height=34,
            command=self._handle_create,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 6))

        ctk.CTkButton(
            btn_grid,
            text="Modifica (UPDATE)",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=34,
            command=self._handle_update,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=(0, 6))

        ctk.CTkButton(
            btn_grid,
            text="Sterge (DELETE)",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            height=34,
            command=self._handle_delete,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            btn_grid,
            text="Curata formular",
            fg_color="#64748B",
            hover_color="#475569",
            height=34,
            command=self._clear_form,
        ).grid(row=1, column=1, sticky="ew", padx=(4, 0))

    def _load_reference_data(self):
        try:
            rute = get_active_rute()
            trenuri = get_active_trenuri()
            admini = get_all_admini()

            self.rute_map = {f"{r['id_ruta']} - {r['denumire']}": r["id_ruta"] for r in rute}
            self.trenuri_map = {f"{t['id_tren']} - {t['nume']}": t["id_tren"] for t in trenuri}
            self.admini_map = {
                f"{a['id_admin']} - {a['nume_complet']}": a["id_admin"] for a in admini
            }

            rute_vals = list(self.rute_map.keys())
            tren_vals = list(self.trenuri_map.keys())
            admin_vals = list(self.admini_map.keys())

            self.combo_ruta.configure(values=rute_vals)
            self.combo_tren.configure(values=tren_vals)
            self.combo_admin.configure(values=admin_vals)

            if rute_vals:
                self.combo_ruta.set(rute_vals[0])
            if tren_vals:
                self.combo_tren.set(tren_vals[0])
            if admin_vals:
                self.combo_admin.set(admin_vals[0])
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Eroare conectare MySQL",
                f"Nu s-a putut conecta la baza de date 'aplicatie_trenuri'.\n"
                f"Verifica daca MySQL este pornit in XAMPP.\n\nDetalii: {err}",
            )

    def _refresh_table(self, data_filter: str | None = None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.curse_by_id.clear()

        try:
            rows = get_all_curse(data_filter)
            for r in rows:
                self.curse_by_id[r["id_cursa"]] = r
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
        except mysql.connector.Error as err:
            messagebox.showerror("Eroare citire date", str(err))

    def _apply_filter(self):
        val = self.entry_filter_date.get().strip()
        self._refresh_table(val if val else None)

    def _reset_filter(self):
        self.entry_filter_date.delete(0, "end")
        self._load_reference_data()
        self._refresh_table()

    def _on_row_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        cursa_id = int(selection[0])
        cursa = self.curse_by_id.get(cursa_id)
        if not cursa:
            return

        self.selected_cursa_id = cursa_id
        self.lbl_selected_id.configure(text=f"Selectie: Cursa ID #{cursa_id}")

        admin_key = f"{cursa['id_admin']} - {cursa['admin_nume']}"
        ruta_key = f"{cursa['id_ruta']} - {cursa['ruta']}"
        tren_key = f"{cursa['id_tren']} - {cursa['tren']}"

        if admin_key in self.admini_map:
            self.combo_admin.set(admin_key)
        if ruta_key in self.rute_map:
            self.combo_ruta.set(ruta_key)
        if tren_key in self.trenuri_map:
            self.combo_tren.set(tren_key)

        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, cursa["data_cursa"])

        self.entry_ora.delete(0, "end")
        self.entry_ora.insert(0, cursa["ora_plecare"])

        self.combo_status.set(cursa["status"])

        self.entry_intarziere.delete(0, "end")
        self.entry_intarziere.insert(0, str(cursa["intarziere_minute"]))

    def _read_form(self):
        admin_key = self.combo_admin.get()
        ruta_key = self.combo_ruta.get()
        tren_key = self.combo_tren.get()

        if admin_key not in self.admini_map or ruta_key not in self.rute_map or tren_key not in self.trenuri_map:
            messagebox.showwarning("Date incomplete", "Selecteaza un administrator, o ruta si un tren.")
            return None

        data_cursa = self.entry_data.get().strip()
        ora_plecare = self.entry_ora.get().strip()
        status = self.combo_status.get().strip()
        intarziere_text = self.entry_intarziere.get().strip()

        if not data_cursa or not ora_plecare:
            messagebox.showwarning(
                "Date incomplete", "Completeaza data (YYYY-MM-DD) si ora de plecare (HH:MM:SS)."
            )
            return None

        try:
            intarziere = int(intarziere_text)
        except ValueError:
            messagebox.showwarning(
                "Valoare invalida", "Minutele de intarziere trebuie sa fie un numar intreg."
            )
            return None

        return (
            self.admini_map[admin_key],
            self.rute_map[ruta_key],
            self.trenuri_map[tren_key],
            data_cursa,
            ora_plecare,
            status,
            intarziere,
        )

    def _handle_create(self):
        values = self._read_form()
        if not values:
            return
        ok, msg = add_cursa(*values)
        if ok:
            messagebox.showinfo("Succes", msg)
            self._clear_form()
            self._refresh_table()
        else:
            messagebox.showerror("Eroare la adaugare", msg)

    def _handle_update(self):
        if self.selected_cursa_id is None:
            messagebox.showwarning(
                "Nicio selectie", "Selecteaza mai intai o cursa din tabel pentru a o actualiza."
            )
            return
        values = self._read_form()
        if not values:
            return
        ok, msg = update_cursa(self.selected_cursa_id, *values)
        if ok:
            messagebox.showinfo("Succes", msg)
            self._refresh_table()
        else:
            messagebox.showerror("Eroare la actualizare", msg)

    def _handle_delete(self):
        if self.selected_cursa_id is None:
            messagebox.showwarning(
                "Nicio selectie", "Selecteaza mai intai o cursa din tabel pentru a o sterge."
            )
            return
        confirm = messagebox.askyesno(
            "Confirmare stergere",
            f"Sigur doresti sa stergi cursa cu ID #{self.selected_cursa_id}?",
        )
        if not confirm:
            return
        ok, msg = delete_cursa(self.selected_cursa_id)
        if ok:
            messagebox.showinfo("Succes", msg)
            self._clear_form()
            self._refresh_table()
        else:
            messagebox.showerror("Stergere blocata / Eroare", msg)

    def _clear_form(self):
        self.selected_cursa_id = None
        self.lbl_selected_id.configure(text="Selectie: Nicio cursa selectata")
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        self.entry_data.delete(0, "end")
        self.entry_ora.delete(0, "end")
        self.combo_status.set("la timp")
        self.entry_intarziere.delete(0, "end")
        self.entry_intarziere.insert(0, "0")


if __name__ == "__main__":
    app = RailwayApp()
    app.mainloop()
