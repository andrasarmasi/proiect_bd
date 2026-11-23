import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from controllers.auth_controller import AuthController
from controllers.client_controller import ClientController
from controllers.cursa_controller import CursaController
from models.auth_model import AuthModel
from models.client_model import ClientModel
from models.cursa_model import CursaModel
from views.client_view import ClientView
from views.curse_view import CurseView
from views.login_view import LoginView
from views.main_view import MainView


class AppCoordinator:
    """Coordoneaza tranzitiile MVC intre Login, Panou Admin si Portal Client."""

    def __init__(self):
        self.main_view = MainView()
        self.active_controller = None
        self.show_login()

    def show_login(self):
        self.main_view.reset_body()
        self.main_view.show_login_header()

        login_view = LoginView(self.main_view.body_container)
        auth_model = AuthModel()
        self.active_controller = AuthController(
            model=auth_model,
            view=login_view,
            on_authenticated=self._on_authenticated,
        )

    def _on_authenticated(self, user: dict):
        if user["role"] == "admin":
            self._show_admin_dashboard(user)
        else:
            self._show_client_portal(user)

    def _show_admin_dashboard(self, admin_user: dict):
        self.main_view.reset_body()
        self.main_view.show_authenticated_header(
            window_title="Aplicatie Feroviara - Panou Administrator",
            header_title="Sistem Feroviar — Panou Administrator (CRUD)",
            user_label=f"Admin: {admin_user['nume_complet']}",
            on_logout=self.show_login,
        )

        tab_curse = self.main_view.add_tab("Curse")
        curse_view = CurseView(tab_curse)
        cursa_model = CursaModel()
        self.active_controller = CursaController(cursa_model, curse_view)

    def _show_client_portal(self, client_user: dict):
        self.main_view.reset_body()
        self.main_view.show_authenticated_header(
            window_title="Aplicatie Feroviara - Portal Client",
            header_title="Sistem Feroviar — Portal Client (Bilete)",
            user_label=f"Client: {client_user['nume_complet']}",
            on_logout=self.show_login,
        )

        tab_search = self.main_view.add_tab("Cauta & Cumpara Bilet")
        tab_tickets = self.main_view.add_tab("Biletele Mele")
        client_view = ClientView(tab_search, tab_tickets)
        client_model = ClientModel()
        self.active_controller = ClientController(
            model=client_model,
            view=client_view,
            client_user=client_user,
        )

    def run(self):
        self.main_view.mainloop()


def main():
    coordinator = AppCoordinator()
    coordinator.run()


if __name__ == "__main__":
    main()
