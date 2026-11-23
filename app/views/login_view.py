from tkinter import messagebox
from typing import Callable

import customtkinter as ctk


class LoginView:
    """View pentru autentificare (Client / Administrator) si inregistrare cont nou de client."""

    def __init__(self, parent):
        self.parent = parent
        self._on_login_cb: Callable[[], None] | None = None
        self._on_register_cb: Callable[[], None] | None = None
        self._build_ui()

    def _build_ui(self):
        wrapper = ctk.CTkFrame(self.parent, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(wrapper, width=480, corner_radius=12)
        card.grid(row=0, column=0, sticky="ns")
        card.grid_propagate(False)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Bine ai venit in Aplicatia Feroviara",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, pady=(18, 6), padx=20)

        self.tabview = ctk.CTkTabview(card)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 16))

        tab_login = self.tabview.add("Autentificare")
        tab_register = self.tabview.add("Creeaza cont Client")

        self._build_login_tab(tab_login)
        self._build_register_tab(tab_register)

    def _build_login_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        ctk.CTkLabel(scroll, text="Tip cont:", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=8, pady=(6, 4)
        )
        self.role_selector = ctk.CTkSegmentedButton(
            scroll, values=["Client", "Administrator"]
        )
        self.role_selector.set("Client")
        self.role_selector.pack(fill="x", padx=8, pady=(0, 12))

        ctk.CTkLabel(scroll, text="Email:").pack(anchor="w", padx=8)
        self.entry_login_email = ctk.CTkEntry(
            scroll, placeholder_text="ex: andrei.popescu@gmail.com"
        )
        self.entry_login_email.pack(fill="x", padx=8, pady=(2, 10))

        ctk.CTkLabel(scroll, text="Parola:").pack(anchor="w", padx=8)
        self.entry_login_password = ctk.CTkEntry(
            scroll, placeholder_text="Introdu parola", show="*"
        )
        self.entry_login_password.pack(fill="x", padx=8, pady=(2, 16))
        self.entry_login_password.bind("<Return>", lambda _e: self._emit_login())

        self.btn_login = ctk.CTkButton(
            scroll,
            text="Autentifica-te",
            height=36,
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            command=self._emit_login,
        )
        self.btn_login.pack(fill="x", padx=8, pady=(0, 16))

        demo_box = ctk.CTkFrame(scroll, fg_color="#E2E8F0", corner_radius=8)
        demo_box.pack(fill="x", padx=8, pady=(4, 8))

        ctk.CTkLabel(
            demo_box,
            text=(
                "Conturi demo (din seed.sql):\n"
                "• Client: andrei.popescu@gmail.com  |  parola: client123\n"
                "• Admin:  admin.ionescu@cfr-proiect.ro  |  parola: admin123"
            ),
            justify="left",
            font=ctk.CTkFont(size=12),
            text_color="#334155",
        ).pack(anchor="w", padx=10, pady=8)

    def _build_register_tab(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=4, pady=(4, 2))

        ctk.CTkLabel(scroll, text="Nume:").pack(anchor="w", padx=8)
        self.entry_reg_nume = ctk.CTkEntry(scroll, placeholder_text="ex: Popescu")
        self.entry_reg_nume.pack(fill="x", padx=8, pady=(2, 6))

        ctk.CTkLabel(scroll, text="Prenume:").pack(anchor="w", padx=8)
        self.entry_reg_prenume = ctk.CTkEntry(scroll, placeholder_text="ex: Andrei")
        self.entry_reg_prenume.pack(fill="x", padx=8, pady=(2, 6))

        ctk.CTkLabel(scroll, text="Email:").pack(anchor="w", padx=8)
        self.entry_reg_email = ctk.CTkEntry(scroll, placeholder_text="ex: nume@email.com")
        self.entry_reg_email.pack(fill="x", padx=8, pady=(2, 6))

        ctk.CTkLabel(scroll, text="Telefon (optional):").pack(anchor="w", padx=8)
        self.entry_reg_telefon = ctk.CTkEntry(scroll, placeholder_text="ex: 0722111222")
        self.entry_reg_telefon.pack(fill="x", padx=8, pady=(2, 6))

        ctk.CTkLabel(scroll, text="Parola (minim 4 caractere):").pack(anchor="w", padx=8)
        self.entry_reg_password = ctk.CTkEntry(scroll, show="*")
        self.entry_reg_password.pack(fill="x", padx=8, pady=(2, 6))

        ctk.CTkLabel(scroll, text="Confirma parola:").pack(anchor="w", padx=8)
        self.entry_reg_confirm = ctk.CTkEntry(scroll, show="*")
        self.entry_reg_confirm.pack(fill="x", padx=8, pady=(2, 8))

        actions = ctk.CTkFrame(parent, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 8))

        self.btn_register = ctk.CTkButton(
            actions,
            text="Creeaza cont Client",
            height=34,
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self._emit_register,
        )
        self.btn_register.pack(fill="x")

    def bind_handlers(
        self,
        *,
        on_login: Callable[[], None],
        on_register: Callable[[], None],
    ):
        self._on_login_cb = on_login
        self._on_register_cb = on_register

    def _emit_login(self):
        if self._on_login_cb:
            self._on_login_cb()

    def _emit_register(self):
        if self._on_register_cb:
            self._on_register_cb()

    def get_login_data(self) -> dict[str, str]:
        return {
            "role": "admin" if self.role_selector.get() == "Administrator" else "client",
            "email": self.entry_login_email.get().strip(),
            "password": self.entry_login_password.get(),
        }

    def get_register_data(self) -> dict[str, str]:
        return {
            "nume": self.entry_reg_nume.get().strip(),
            "prenume": self.entry_reg_prenume.get().strip(),
            "email": self.entry_reg_email.get().strip(),
            "telefon": self.entry_reg_telefon.get().strip(),
            "password": self.entry_reg_password.get(),
            "confirm": self.entry_reg_confirm.get(),
        }

    def clear_register_and_prefill_login(self, email: str):
        for entry in (
            self.entry_reg_nume,
            self.entry_reg_prenume,
            self.entry_reg_email,
            self.entry_reg_telefon,
            self.entry_reg_password,
            self.entry_reg_confirm,
        ):
            entry.delete(0, "end")

        self.tabview.set("Autentificare")
        self.role_selector.set("Client")
        self.entry_login_email.delete(0, "end")
        self.entry_login_email.insert(0, email)
        self.entry_login_password.delete(0, "end")

    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message)

    def show_warning(self, title: str, message: str):
        messagebox.showwarning(title, message)

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message)
