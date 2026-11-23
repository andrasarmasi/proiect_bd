from tkinter import messagebox, ttk
from typing import Callable

import customtkinter as ctk


class ClientView:
    """View pentru portalul clientului: cautare/cumparare bilete si vizualizare/anulare bilete."""

    def __init__(self, tab_search, tab_tickets):
        self.tab_search = tab_search
        self.tab_tickets = tab_tickets

        self._on_cursa_select_cb: Callable[[int], None] | None = None
        self._on_ticket_select_cb: Callable[[int], None] | None = None
        self._on_price_inputs_change_cb: Callable[[], None] | None = None

        self._configure_treeview_style()
        self._build_search_tab()
        self._build_tickets_tab()

    @staticmethod
    def _configure_treeview_style():
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

    def _build_search_tab(self):
        self.tab_search.grid_columnconfigure(0, weight=3)
        self.tab_search.grid_columnconfigure(1, weight=1, minsize=310)
        self.tab_search.grid_rowconfigure(1, weight=1)

        # Bara de cautare (sus stanga)
        search_bar = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        search_bar.grid(row=0, column=0, sticky="ew", padx=(4, 12), pady=(4, 8))

        ctk.CTkLabel(search_bar, text="Plecare:").pack(side="left", padx=(0, 4))
        self.combo_urcare = ctk.CTkComboBox(search_bar, width=145, values=[], state="readonly")
        self.combo_urcare.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(search_bar, text="Sosire:").pack(side="left", padx=(0, 4))
        self.combo_coborare = ctk.CTkComboBox(search_bar, width=145, values=[], state="readonly")
        self.combo_coborare.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(search_bar, text="Data:").pack(side="left", padx=(0, 4))
        self.entry_search_date = ctk.CTkEntry(
            search_bar, width=105, placeholder_text="YYYY-MM-DD"
        )
        self.entry_search_date.pack(side="left", padx=(0, 8))

        self.btn_search = ctk.CTkButton(search_bar, text="Cauta", width=75)
        self.btn_search.pack(side="left", padx=(0, 6))

        self.btn_show_all = ctk.CTkButton(
            search_bar,
            text="Toate",
            width=70,
            fg_color="#475569",
            hover_color="#334155",
        )
        self.btn_show_all.pack(side="left")

        # Tabelul cu curse disponibile (stanga)
        table_container = ctk.CTkFrame(self.tab_search)
        table_container.grid(row=1, column=0, sticky="nsew", padx=(4, 12), pady=4)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        columns = (
            "id_cursa",
            "segment",
            "tren",
            "tip_tren",
            "data_cursa",
            "plecare",
            "sosire",
            "distanta",
            "status",
            "locuri_libere",
        )
        self.tree_curse = ttk.Treeview(
            table_container, columns=columns, show="headings", selectmode="browse"
        )
        headings = [
            ("id_cursa", "ID", 42, "center"),
            ("segment", "Traseu selectat", 205, "w"),
            ("tren", "Tren", 155, "w"),
            ("tip_tren", "Categorie", 105, "w"),
            ("data_cursa", "Data", 90, "center"),
            ("plecare", "Plecare", 68, "center"),
            ("sosire", "Sosire", 68, "center"),
            ("distanta", "Dist. (km)", 75, "center"),
            ("status", "Status", 82, "center"),
            ("locuri_libere", "Locuri libere", 88, "center"),
        ]
        for col_id, label, width, anchor in headings:
            self.tree_curse.heading(col_id, text=label)
            self.tree_curse.column(col_id, width=width, anchor=anchor)

        scroll_y = ttk.Scrollbar(
            table_container, orient="vertical", command=self.tree_curse.yview
        )
        scroll_x = ttk.Scrollbar(
            table_container, orient="horizontal", command=self.tree_curse.xview
        )
        self.tree_curse.configure(
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
        )

        self.tree_curse.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=(6, 0))
        scroll_y.grid(row=0, column=1, sticky="ns", pady=(6, 0), padx=(0, 6))
        scroll_x.grid(row=1, column=0, sticky="ew", padx=(6, 0), pady=(0, 6))

        self.tree_curse.bind("<<TreeviewSelect>>", self._emit_cursa_select)

        # Panou cumparare bilet (dreapta): campuri scrolabile + buton fixat jos
        buy_panel = ctk.CTkFrame(self.tab_search, corner_radius=10)
        buy_panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 4), pady=4)
        buy_panel.grid_rowconfigure(0, weight=1)
        buy_panel.grid_rowconfigure(1, weight=0)
        buy_panel.grid_columnconfigure(0, weight=1)

        buy_scroll = ctk.CTkScrollableFrame(buy_panel, fg_color="transparent")
        buy_scroll.grid(row=0, column=0, sticky="nsew", padx=4, pady=(6, 2))

        ctk.CTkLabel(
            buy_scroll,
            text="Cumpara Bilet",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(4, 6))

        self.lbl_cursa_details = ctk.CTkLabel(
            buy_scroll,
            text="Selecteaza o cursa din tabel pentru\na vedea locurile disponibile si pretul.",
            justify="left",
            text_color="#475569",
            wraplength=260,
        )
        self.lbl_cursa_details.pack(anchor="w", padx=10, pady=(0, 12))

        ctk.CTkLabel(buy_scroll, text="Loc disponibil (Vagon / Clasa / Loc):").pack(
            anchor="w", padx=10
        )
        self.combo_loc = ctk.CTkComboBox(
            buy_scroll,
            values=["Selecteaza o cursa"],
            state="readonly",
            command=lambda _val: self._emit_price_change(),
        )
        self.combo_loc.pack(fill="x", padx=10, pady=(2, 10))

        ctk.CTkLabel(buy_scroll, text="Reducere aplicabila:").pack(anchor="w", padx=10)
        self.combo_reducere = ctk.CTkComboBox(
            buy_scroll,
            values=["Fara reducere (0%)"],
            state="readonly",
            command=lambda _val: self._emit_price_change(),
        )
        self.combo_reducere.pack(fill="x", padx=10, pady=(2, 12))

        price_card = ctk.CTkFrame(buy_scroll, fg_color="#EFF6FF", corner_radius=8)
        price_card.pack(fill="x", padx=10, pady=(4, 8))

        ctk.CTkLabel(
            price_card,
            text="Total de plata:",
            font=ctk.CTkFont(size=12),
            text_color="#1E40AF",
        ).pack(anchor="w", padx=12, pady=(8, 0))

        self.lbl_price = ctk.CTkLabel(
            price_card,
            text="0.00 RON",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1E3A8A",
        )
        self.lbl_price.pack(anchor="w", padx=12, pady=(0, 8))

        # Buton cumparare fixat in partea de jos
        buy_actions = ctk.CTkFrame(buy_panel, fg_color="transparent")
        buy_actions.grid(row=1, column=0, sticky="ew", padx=10, pady=(4, 10))

        self.btn_buy = ctk.CTkButton(
            buy_actions,
            text="Cumpara Bilet",
            height=36,
            fg_color="#16A34A",
            hover_color="#15803D",
        )
        self.btn_buy.pack(fill="x")

    def _build_tickets_tab(self):
        self.tab_tickets.grid_columnconfigure(0, weight=1)
        self.tab_tickets.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self.tab_tickets, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 8))

        ctk.CTkLabel(
            top_bar,
            text="Istoricul biletelor tale (selecteaza un bilet valid pentru anulare):",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left")

        self.btn_refresh_tickets = ctk.CTkButton(
            top_bar,
            text="Refresh",
            width=95,
            fg_color="#475569",
            hover_color="#334155",
        )
        self.btn_refresh_tickets.pack(side="right")

        table_container = ctk.CTkFrame(self.tab_tickets)
        table_container.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        columns = (
            "id_bilet",
            "data_cursa",
            "ora_plecare",
            "tren",
            "urcare",
            "coborare",
            "loc",
            "clasa",
            "reducere",
            "pret",
            "status",
            "cumparat_la",
        )
        self.tree_tickets = ttk.Treeview(
            table_container, columns=columns, show="headings", selectmode="browse"
        )
        headings = [
            ("id_bilet", "ID", 45, "center"),
            ("data_cursa", "Data cursa", 88, "center"),
            ("ora_plecare", "Plecare", 68, "center"),
            ("tren", "Tren", 150, "w"),
            ("urcare", "Statie urcare", 120, "w"),
            ("coborare", "Statie coborare", 120, "w"),
            ("loc", "Vagon / Loc", 90, "center"),
            ("clasa", "Clasa", 55, "center"),
            ("reducere", "Reducere", 115, "w"),
            ("pret", "Pret (RON)", 82, "center"),
            ("status", "Status", 70, "center"),
            ("cumparat_la", "Data cumpararii", 125, "center"),
        ]
        for col_id, label, width, anchor in headings:
            self.tree_tickets.heading(col_id, text=label)
            self.tree_tickets.column(col_id, width=width, anchor=anchor)

        scroll_y = ttk.Scrollbar(
            table_container, orient="vertical", command=self.tree_tickets.yview
        )
        scroll_x = ttk.Scrollbar(
            table_container, orient="horizontal", command=self.tree_tickets.xview
        )
        self.tree_tickets.configure(
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
        )

        self.tree_tickets.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=(6, 0))
        scroll_y.grid(row=0, column=1, sticky="ns", pady=(6, 0), padx=(0, 6))
        scroll_x.grid(row=1, column=0, sticky="ew", padx=(6, 0), pady=(0, 6))

        self.tree_tickets.bind("<<TreeviewSelect>>", self._emit_ticket_select)

        bottom_bar = ctk.CTkFrame(self.tab_tickets, fg_color="transparent")
        bottom_bar.grid(row=2, column=0, sticky="ew", padx=4, pady=(8, 4))

        self.lbl_selected_ticket = ctk.CTkLabel(
            bottom_bar, text="Selectie: Niciun bilet selectat", text_color="#475569"
        )
        self.lbl_selected_ticket.pack(side="left")

        self.btn_cancel_ticket = ctk.CTkButton(
            bottom_bar,
            text="Anuleaza Bilet Selectat",
            width=190,
            height=34,
            fg_color="#DC2626",
            hover_color="#B91C1C",
        )
        self.btn_cancel_ticket.pack(side="right")

    def bind_handlers(
        self,
        *,
        on_search: Callable[[], None],
        on_show_all: Callable[[], None],
        on_cursa_select: Callable[[int], None],
        on_price_inputs_change: Callable[[], None],
        on_buy_ticket: Callable[[], None],
        on_refresh_tickets: Callable[[], None],
        on_ticket_select: Callable[[int], None],
        on_cancel_ticket: Callable[[], None],
    ):
        self.btn_search.configure(command=on_search)
        self.btn_show_all.configure(command=on_show_all)
        self._on_cursa_select_cb = on_cursa_select
        self._on_price_inputs_change_cb = on_price_inputs_change
        self.btn_buy.configure(command=on_buy_ticket)
        self.btn_refresh_tickets.configure(command=on_refresh_tickets)
        self._on_ticket_select_cb = on_ticket_select
        self.btn_cancel_ticket.configure(command=on_cancel_ticket)

    def _emit_cursa_select(self, _event):
        if not self._on_cursa_select_cb:
            return
        sel = self.tree_curse.selection()
        if not sel:
            return
        self._on_cursa_select_cb(int(sel[0]))

    def _emit_ticket_select(self, _event):
        if not self._on_ticket_select_cb:
            return
        sel = self.tree_tickets.selection()
        if not sel:
            return
        self._on_ticket_select_cb(int(sel[0]))

    def _emit_price_change(self):
        if self._on_price_inputs_change_cb:
            self._on_price_inputs_change_cb()

    def set_statii_options(self, statii_labels: list[str]):
        self.combo_urcare.configure(values=statii_labels)
        self.combo_coborare.configure(values=statii_labels)
        if statii_labels:
            self.combo_urcare.set(statii_labels[0])
            self.combo_coborare.set(statii_labels[-1] if len(statii_labels) > 1 else statii_labels[0])

    def set_reduceri_options(self, reduceri_labels: list[str]):
        self.combo_reducere.configure(values=reduceri_labels)
        if reduceri_labels:
            self.combo_reducere.set(reduceri_labels[0])

    def get_search_filters(self) -> dict[str, str]:
        return {
            "urcare": self.combo_urcare.get(),
            "coborare": self.combo_coborare.get(),
            "data": self.entry_search_date.get().strip(),
        }

    def clear_search_date(self):
        self.entry_search_date.delete(0, "end")

    def set_curse_rows(self, rows: list[dict]):
        for item in self.tree_curse.get_children():
            self.tree_curse.delete(item)

        for idx, r in enumerate(rows):
            status_text = (
                f"{r['status']} (+{r['intarziere_minute']}m)"
                if r["intarziere_minute"] > 0
                else r["status"]
            )
            self.tree_curse.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    r["id_cursa"],
                    f"{r['statie_urcare']} -> {r['statie_coborare']}",
                    r["tren"],
                    r["tip_tren"],
                    r["data_cursa"],
                    r["ora_plecare_segment"],
                    r["ora_sosire_segment"],
                    f"{r['distanta_km']} km",
                    status_text,
                    r["locuri_libere"],
                ),
            )

    def set_selected_cursa_details(self, text: str):
        self.lbl_cursa_details.configure(text=text)

    def set_seat_options(self, seat_labels: list[str]):
        if seat_labels:
            self.combo_loc.configure(values=seat_labels)
            self.combo_loc.set(seat_labels[0])
        else:
            self.combo_loc.configure(values=["Nu exista locuri libere"])
            self.combo_loc.set("Nu exista locuri libere")

    def get_booking_selection(self) -> dict[str, str]:
        return {
            "seat_label": self.combo_loc.get(),
            "reducere_label": self.combo_reducere.get(),
        }

    def set_calculated_price(self, text: str):
        self.lbl_price.configure(text=text)

    def set_ticket_rows(self, rows: list[dict]):
        for item in self.tree_tickets.get_children():
            self.tree_tickets.delete(item)

        for r in rows:
            self.tree_tickets.insert(
                "",
                "end",
                iid=str(r["id_bilet"]),
                values=(
                    r["id_bilet"],
                    r["data_cursa"],
                    r["ora_plecare"],
                    r["tren"],
                    r["statie_urcare"],
                    r["statie_coborare"],
                    f"V{r['nr_vagon']} / Loc {r['nr_loc']}",
                    f"Cl. {r['clasa']}",
                    r["reducere"],
                    f"{float(r['pret_platit']):.2f}",
                    r["status_bilet"],
                    r["data_cumpararii"],
                ),
            )

    def set_selected_ticket_label(self, text: str):
        self.lbl_selected_ticket.configure(text=text)

    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message)

    def show_warning(self, title: str, message: str):
        messagebox.showwarning(title, message)

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message)

    def ask_confirm(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)
