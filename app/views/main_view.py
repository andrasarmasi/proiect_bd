from typing import Callable

import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class MainView(ctk.CTk):
    """Fereastra principala a aplicatiei (header cu rol/logout + container dinamic)."""

    def __init__(self):
        super().__init__()

        self.title("Aplicatie Feroviara - Sistem de Gestiune si Bilete")
        self.geometry("1180x680")
        self.minsize(1000, 600)

        self._logout_cb: Callable[[], None] | None = None
        self.tabview: ctk.CTkTabview | None = None

        self._build_layout()

    def _build_layout(self):
        self.header = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E3A8A", height=56)
        self.header.pack(fill="x", side="top")

        self.title_lbl = ctk.CTkLabel(
            self.header,
            text="Sistem Feroviar — Autentificare",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
        )
        self.title_lbl.pack(side="left", padx=20, pady=12)

        self.user_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.user_lbl = ctk.CTkLabel(
            self.user_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#E2E8F0",
        )
        self.user_lbl.pack(side="left", padx=(0, 12))

        self.btn_logout = ctk.CTkButton(
            self.user_frame,
            text="Deconectare",
            width=110,
            height=30,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self._handle_logout,
        )
        self.btn_logout.pack(side="left")

        self.body_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_container.pack(fill="both", expand=True)

    def _handle_logout(self):
        if self._logout_cb:
            self._logout_cb()

    def reset_body(self):
        for widget in self.body_container.winfo_children():
            widget.destroy()
        self.tabview = None

    def show_login_header(self):
        self.title("Aplicatie Feroviara - Autentificare")
        self.title_lbl.configure(text="Sistem Feroviar — Autentificare")
        self._logout_cb = None
        self.user_frame.pack_forget()

    def show_authenticated_header(
        self,
        window_title: str,
        header_title: str,
        user_label: str,
        on_logout: Callable[[], None],
    ):
        self.title(window_title)
        self.title_lbl.configure(text=header_title)
        self.user_lbl.configure(text=user_label)
        self._logout_cb = on_logout
        self.user_frame.pack(side="right", padx=20, pady=10)

    def create_tabview(self) -> ctk.CTkTabview:
        self.tabview = ctk.CTkTabview(self.body_container, anchor="nw")
        self.tabview.pack(fill="both", expand=True, padx=16, pady=12)
        return self.tabview

    def add_tab(self, name: str):
        if self.tabview is None:
            self.create_tabview()
        return self.tabview.add(name)
