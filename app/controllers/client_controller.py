from models.client_model import ClientModel
from models.cursa_model import DatabaseError
from views.client_view import ClientView


class ClientController:
    """Controller pentru portalul clientului: cautare curse, cumparare si anulare bilete."""

    def __init__(self, model: ClientModel, view: ClientView, client_user: dict):
        self.model = model
        self.view = view
        self.client_user = client_user

        self.statii_map: dict[str, int] = {}
        self.reduceri_map: dict[str, dict | None] = {}
        self.current_curse: list[dict] = []
        self.selected_cursa: dict | None = None
        self.seats_map: dict[str, dict] = {}
        self.tickets_by_id: dict[int, dict] = {}
        self.selected_ticket_id: int | None = None
        self._last_search_args: tuple[int | None, int | None, str | None] = (None, None, None)

        self.view.bind_handlers(
            on_search=self.handle_search,
            on_show_all=self.handle_show_all,
            on_cursa_select=self.handle_cursa_select,
            on_price_inputs_change=self.update_price_preview,
            on_buy_ticket=self.handle_buy_ticket,
            on_refresh_tickets=self.refresh_tickets,
            on_ticket_select=self.handle_ticket_select,
            on_cancel_ticket=self.handle_cancel_ticket,
        )

        self.load_reference_data()
        self.handle_show_all()
        self.refresh_tickets()

    def load_reference_data(self):
        try:
            statii = self.model.get_active_statii()
            reduceri = self.model.get_reduceri()

            self.statii_map = {s["nume"]: s["id_statie"] for s in statii}
            self.view.set_statii_options(list(self.statii_map.keys()))

            self.reduceri_map = {"Fara reducere (0%)": None}
            for red in reduceri:
                self.reduceri_map[red["denumire"]] = red
            self.view.set_reduceri_options(list(self.reduceri_map.keys()))
        except DatabaseError as err:
            self.view.show_error(
                "Eroare conectare MySQL",
                f"Nu s-au putut incarca statiile si reducerile.\n\nDetalii: {err}",
            )

    def _run_search(
        self,
        id_urcare: int | None,
        id_coborare: int | None,
        data_filter: str | None,
    ):
        self._last_search_args = (id_urcare, id_coborare, data_filter)
        self.selected_cursa = None
        self.seats_map.clear()
        self.view.set_selected_cursa_details(
            "Selecteaza o cursa din tabel pentru\na vedea locurile disponibile si pretul."
        )
        self.view.set_seat_options([])
        self.view.set_calculated_price("0.00 RON")

        try:
            self.current_curse = self.model.search_curse(
                id_statie_urcare=id_urcare,
                id_statie_coborare=id_coborare,
                data_filter=data_filter,
            )
            self.view.set_curse_rows(self.current_curse)
        except DatabaseError as err:
            self.current_curse = []
            self.view.set_curse_rows([])
            self.view.show_error("Eroare cautare curse", str(err))

    def handle_search(self):
        filters = self.view.get_search_filters()
        urcare_label = filters["urcare"]
        coborare_label = filters["coborare"]
        data_val = filters["data"] or None

        if urcare_label not in self.statii_map or coborare_label not in self.statii_map:
            self.view.show_warning(
                "Date incomplete", "Selecteaza statia de plecare si statia de sosire."
            )
            return

        id_urcare = self.statii_map[urcare_label]
        id_coborare = self.statii_map[coborare_label]
        if id_urcare == id_coborare:
            self.view.show_warning(
                "Statii identice",
                "Statia de plecare trebuie sa fie diferita de statia de sosire.",
            )
            return

        self._run_search(id_urcare, id_coborare, data_val)

    def handle_show_all(self):
        self.view.clear_search_date()
        self._run_search(None, None, None)

    def handle_cursa_select(self, row_index: int):
        if row_index < 0 or row_index >= len(self.current_curse):
            return

        cursa = self.current_curse[row_index]
        self.selected_cursa = cursa

        details = (
            f"Cursa #{cursa['id_cursa']} — {cursa['tren']} ({cursa['tip_tren']})\n"
            f"Traseu: {cursa['statie_urcare']} -> {cursa['statie_coborare']}\n"
            f"Data: {cursa['data_cursa']} | {cursa['ora_plecare_segment']} - {cursa['ora_sosire_segment']}\n"
            f"Distanta: {cursa['distanta_km']} km | Locuri libere: {cursa['locuri_libere']}"
        )
        self.view.set_selected_cursa_details(details)

        try:
            seats = self.model.get_available_seats(
                id_cursa=cursa["id_cursa"],
                id_ruta=cursa["id_ruta"],
                id_tren=cursa["id_tren"],
                ordine_urcare=cursa["ordine_urcare"],
                ordine_coborare=cursa["ordine_coborare"],
            )
        except DatabaseError as err:
            self.seats_map.clear()
            self.view.set_seat_options([])
            self.view.set_calculated_price("0.00 RON")
            self.view.show_error("Eroare incarcare locuri", str(err))
            return

        self.seats_map = {
            f"Vagon {s['nr_vagon']} (Clasa {s['clasa']}) - Loc {s['nr_loc']}": s
            for s in seats
        }
        self.view.set_seat_options(list(self.seats_map.keys()))
        self.update_price_preview()

    def _compute_current_price(self) -> tuple[dict, dict | None, float] | None:
        if not self.selected_cursa:
            return None
        selection = self.view.get_booking_selection()
        seat = self.seats_map.get(selection["seat_label"])
        if not seat:
            return None
        reducere = self.reduceri_map.get(selection["reducere_label"])
        procent = float(reducere["procent"]) if reducere else 0.0
        price = self.model.calculate_price(
            distanta_km=float(self.selected_cursa["distanta_km"]),
            coeficient_pret=float(self.selected_cursa["coeficient_pret"]),
            clasa=int(seat["clasa"]),
            procent_reducere=procent,
        )
        return seat, reducere, price

    def update_price_preview(self):
        result = self._compute_current_price()
        if not result:
            self.view.set_calculated_price("0.00 RON")
            return
        _, _, price = result
        self.view.set_calculated_price(f"{price:.2f} RON")

    def handle_buy_ticket(self):
        if not self.selected_cursa:
            self.view.show_warning(
                "Nicio cursa selectata",
                "Selecteaza mai intai o cursa din tabel.",
            )
            return

        computed = self._compute_current_price()
        if not computed:
            self.view.show_warning(
                "Niciun loc disponibil",
                "Nu exista locuri libere disponibile pentru aceasta cursa pe segmentul selectat.",
            )
            return

        seat, reducere, price = computed
        cursa = self.selected_cursa
        red_label = reducere["denumire"] if reducere else "Fara reducere"

        confirm = self.view.ask_confirm(
            "Confirmare cumparare bilet",
            f"Confirmi cumpararea biletului?\n\n"
            f"Tren: {cursa['tren']}\n"
            f"Traseu: {cursa['statie_urcare']} -> {cursa['statie_coborare']}\n"
            f"Data: {cursa['data_cursa']} ({cursa['ora_plecare_segment']} - {cursa['ora_sosire_segment']})\n"
            f"Loc: Vagon {seat['nr_vagon']} (Clasa {seat['clasa']}), Loc {seat['nr_loc']}\n"
            f"Reducere: {red_label}\n"
            f"Total de plata: {price:.2f} RON",
        )
        if not confirm:
            return

        ok, msg = self.model.buy_bilet(
            id_client=self.client_user["id"],
            id_cursa=cursa["id_cursa"],
            id_ruta=cursa["id_ruta"],
            id_loc=seat["id_loc"],
            id_statie_urcare=cursa["id_statie_urcare"],
            id_statie_coborare=cursa["id_statie_coborare"],
            ordine_urcare=cursa["ordine_urcare"],
            ordine_coborare=cursa["ordine_coborare"],
            id_reducere=reducere["id_reducere"] if reducere else None,
            pret_platit=price,
        )
        if ok:
            self.view.show_info("Bilet emis", msg)
            self._run_search(*self._last_search_args)
            self.refresh_tickets()
        else:
            self.view.show_error("Eroare cumparare", msg)

    def refresh_tickets(self):
        self.selected_ticket_id = None
        self.tickets_by_id.clear()
        self.view.set_selected_ticket_label("Selectie: Niciun bilet selectat")
        try:
            rows = self.model.get_client_bilete(self.client_user["id"])
            for r in rows:
                self.tickets_by_id[r["id_bilet"]] = r
            self.view.set_ticket_rows(rows)
        except DatabaseError as err:
            self.view.set_ticket_rows([])
            self.view.show_error("Eroare citire bilete", str(err))

    def handle_ticket_select(self, id_bilet: int):
        ticket = self.tickets_by_id.get(id_bilet)
        if not ticket:
            return
        self.selected_ticket_id = id_bilet
        self.view.set_selected_ticket_label(
            f"Selectie: Bilet #{id_bilet} ({ticket['statie_urcare']} -> {ticket['statie_coborare']}, status: {ticket['status_bilet']})"
        )

    def handle_cancel_ticket(self):
        if self.selected_ticket_id is None:
            self.view.show_warning(
                "Niciun bilet selectat",
                "Selecteaza mai intai un bilet din tabel pentru a-l anula.",
            )
            return

        ticket = self.tickets_by_id.get(self.selected_ticket_id)
        if not ticket or ticket["status_bilet"] != "valid":
            self.view.show_warning(
                "Bilet deja anulat",
                "Poti anula doar biletele care au statusul 'valid'.",
            )
            return

        confirm = self.view.ask_confirm(
            "Confirmare anulare",
            f"Sigur doresti sa anulezi biletul #{self.selected_ticket_id}?\n"
            f"Locul va deveni din nou disponibil pentru alti calatori.",
        )
        if not confirm:
            return

        ok, msg = self.model.cancel_bilet(
            id_bilet=self.selected_ticket_id,
            id_client=self.client_user["id"],
        )
        if ok:
            self.view.show_info("Bilet anulat", msg)
            self.refresh_tickets()
            self._run_search(*self._last_search_args)
        else:
            self.view.show_error("Eroare anulare", msg)
