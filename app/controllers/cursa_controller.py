from models.cursa_model import CursaModel, DatabaseError
from views.curse_view import CurseView


class CursaController:
    """Controller care coordoneaza interactiunea dintre CurseView si CursaModel."""

    def __init__(self, model: CursaModel, view: CurseView):
        self.model = model
        self.view = view

        self.selected_cursa_id: int | None = None
        self.rute_map: dict[str, int] = {}
        self.trenuri_map: dict[str, int] = {}
        self.admini_map: dict[str, int] = {}
        self.curse_by_id: dict[int, dict] = {}

        self.view.bind_handlers(
            on_filter=self.handle_filter,
            on_reset_filter=self.handle_reset_filter,
            on_row_select=self.handle_row_select,
            on_create=self.handle_create,
            on_update=self.handle_update,
            on_delete=self.handle_delete,
            on_clear=self.handle_clear,
        )

        self.load_reference_data()
        self.refresh_table()

    def load_reference_data(self):
        try:
            rute = self.model.get_active_rute()
            trenuri = self.model.get_active_trenuri()
            admini = self.model.get_all_admini()

            self.rute_map = {
                f"{r['id_ruta']} - {r['denumire']}": r["id_ruta"] for r in rute
            }
            self.trenuri_map = {
                f"{t['id_tren']} - {t['nume']}": t["id_tren"] for t in trenuri
            }
            self.admini_map = {
                f"{a['id_admin']} - {a['nume_complet']}": a["id_admin"] for a in admini
            }

            self.view.set_reference_options(
                list(self.rute_map.keys()),
                list(self.trenuri_map.keys()),
                list(self.admini_map.keys()),
            )
        except DatabaseError as err:
            self.view.show_error(
                "Eroare conectare MySQL",
                f"Nu s-a putut conecta la baza de date 'aplicatie_trenuri'.\n"
                f"Verifica daca MySQL este pornit in XAMPP.\n\nDetalii: {err}",
            )

    def refresh_table(self, data_filter: str | None = None):
        self.curse_by_id.clear()
        try:
            rows = self.model.get_all_curse(data_filter)
            for r in rows:
                self.curse_by_id[r["id_cursa"]] = r
            self.view.set_curse_rows(rows)
        except DatabaseError as err:
            self.view.set_curse_rows([])
            self.view.show_error("Eroare citire date", str(err))

    def handle_filter(self):
        val = self.view.get_filter_date()
        self.refresh_table(val if val else None)

    def handle_reset_filter(self):
        self.view.clear_filter_date()
        self.load_reference_data()
        self.refresh_table()

    def handle_row_select(self, cursa_id: int):
        cursa = self.curse_by_id.get(cursa_id)
        if not cursa:
            return

        self.selected_cursa_id = cursa_id
        self.view.set_selected_label(f"Selectie: Cursa ID #{cursa_id}")

        admin_key = f"{cursa['id_admin']} - {cursa['admin_nume']}"
        ruta_key = f"{cursa['id_ruta']} - {cursa['ruta']}"
        tren_key = f"{cursa['id_tren']} - {cursa['tren']}"

        self.view.populate_form(
            admin_key=admin_key if admin_key in self.admini_map else None,
            ruta_key=ruta_key if ruta_key in self.rute_map else None,
            tren_key=tren_key if tren_key in self.trenuri_map else None,
            data_cursa=cursa["data_cursa"],
            ora_plecare=cursa["ora_plecare"],
            status=cursa["status"],
            intarziere_minute=cursa["intarziere_minute"],
        )

    def _read_and_validate_form(self):
        data = self.view.get_form_data()
        admin_key = data["admin_key"]
        ruta_key = data["ruta_key"]
        tren_key = data["tren_key"]

        if (
            admin_key not in self.admini_map
            or ruta_key not in self.rute_map
            or tren_key not in self.trenuri_map
        ):
            self.view.show_warning(
                "Date incomplete", "Selecteaza un administrator, o ruta si un tren."
            )
            return None

        data_cursa = data["data_cursa"]
        ora_plecare = data["ora_plecare"]
        status = data["status"]
        intarziere_text = data["intarziere_text"]

        if not data_cursa or not ora_plecare:
            self.view.show_warning(
                "Date incomplete",
                "Completeaza data (YYYY-MM-DD) si ora de plecare (HH:MM:SS).",
            )
            return None

        try:
            intarziere = int(intarziere_text)
        except ValueError:
            self.view.show_warning(
                "Valoare invalida",
                "Minutele de intarziere trebuie sa fie un numar intreg.",
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

    def handle_create(self):
        values = self._read_and_validate_form()
        if not values:
            return
        ok, msg = self.model.add_cursa(*values)
        if ok:
            self.view.show_info("Succes", msg)
            self.handle_clear()
            self.refresh_table()
        else:
            self.view.show_error("Eroare la adaugare", msg)

    def handle_update(self):
        if self.selected_cursa_id is None:
            self.view.show_warning(
                "Nicio selectie",
                "Selecteaza mai intai o cursa din tabel pentru a o actualiza.",
            )
            return
        values = self._read_and_validate_form()
        if not values:
            return
        ok, msg = self.model.update_cursa(self.selected_cursa_id, *values)
        if ok:
            self.view.show_info("Succes", msg)
            self.refresh_table()
        else:
            self.view.show_error("Eroare la actualizare", msg)

    def handle_delete(self):
        if self.selected_cursa_id is None:
            self.view.show_warning(
                "Nicio selectie",
                "Selecteaza mai intai o cursa din tabel pentru a o sterge.",
            )
            return
        confirm = self.view.ask_confirm(
            "Confirmare stergere",
            f"Sigur doresti sa stergi cursa cu ID #{self.selected_cursa_id}?",
        )
        if not confirm:
            return
        ok, msg = self.model.delete_cursa(self.selected_cursa_id)
        if ok:
            self.view.show_info("Succes", msg)
            self.handle_clear()
            self.refresh_table()
        else:
            self.view.show_error("Stergere blocata / Eroare", msg)

    def handle_clear(self):
        self.selected_cursa_id = None
        self.view.clear_form()
