from typing import Callable

from models.auth_model import AuthModel
from models.cursa_model import DatabaseError
from views.login_view import LoginView


class AuthController:
    """Controller pentru autentificare (Admin / Client) si inregistrare client nou."""

    def __init__(
        self,
        model: AuthModel,
        view: LoginView,
        on_authenticated: Callable[[dict], None],
    ):
        self.model = model
        self.view = view
        self.on_authenticated = on_authenticated

        self.view.bind_handlers(
            on_login=self.handle_login,
            on_register=self.handle_register,
        )

    def handle_login(self):
        data = self.view.get_login_data()
        role = data["role"]
        email = data["email"]
        password = data["password"]

        if not email or not password:
            self.view.show_warning(
                "Date incomplete", "Introdu adresa de email si parola."
            )
            return

        try:
            if role == "admin":
                user = self.model.authenticate_admin(email, password)
            else:
                user = self.model.authenticate_client(email, password)
        except DatabaseError as err:
            self.view.show_error(
                "Eroare conectare MySQL",
                f"Nu s-a putut conecta la baza de date 'aplicatie_trenuri'.\n"
                f"Verifica daca MySQL este pornit in XAMPP.\n\nDetalii: {err}",
            )
            return

        if user is None:
            self.view.show_error(
                "Autentificare esuata",
                "Email sau parola incorecta pentru tipul de cont selectat.",
            )
            return

        self.on_authenticated(user)

    def handle_register(self):
        data = self.view.get_register_data()
        nume = data["nume"]
        prenume = data["prenume"]
        email = data["email"]
        telefon = data["telefon"]
        password = data["password"]
        confirm = data["confirm"]

        if not nume or not prenume or not email or not password:
            self.view.show_warning(
                "Date incomplete",
                "Completeaza numele, prenumele, emailul si parola.",
            )
            return

        if "@" not in email or "." not in email:
            self.view.show_warning("Email invalid", "Introdu o adresa de email valida.")
            return

        if len(password) < 4:
            self.view.show_warning(
                "Parola prea scurta",
                "Parola trebuie sa aiba cel putin 4 caractere.",
            )
            return

        if password != confirm:
            self.view.show_warning(
                "Parole diferite", "Parola si confirmarea parolei nu coincid."
            )
            return

        ok, msg = self.model.register_client(
            nume=nume,
            prenume=prenume,
            email=email,
            password=password,
            nr_telefon=telefon,
        )
        if ok:
            self.view.show_info("Cont creat", msg)
            self.view.clear_register_and_prefill_login(email)
        else:
            self.view.show_error("Eroare inregistrare", msg)
