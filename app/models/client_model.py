import mysql.connector

from config.db_config import get_connection
from models.cursa_model import DatabaseError


class ClientModel:
    """Model pentru fluxul clientului: cautare curse, locuri libere, cumparare si anulare bilete."""

    BASE_TARIFF_PER_KM = 0.25
    CLASS_1_MULTIPLIER = 1.20
    CLASS_2_MULTIPLIER = 1.00

    @classmethod
    def calculate_price(
        cls,
        distanta_km: float,
        coeficient_pret: float,
        clasa: int,
        procent_reducere: float,
    ) -> float:
        factor_clasa = cls.CLASS_1_MULTIPLIER if clasa == 1 else cls.CLASS_2_MULTIPLIER
        brut = float(distanta_km) * cls.BASE_TARIFF_PER_KM * float(coeficient_pret) * factor_clasa
        net = brut * (1.0 - float(procent_reducere) / 100.0)
        return round(max(net, 0.0), 2)

    def get_active_statii(self) -> list[dict]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_statie, nume, oras FROM Statii "
                "WHERE activ = TRUE ORDER BY nume ASC"
            )
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def get_reduceri(self) -> list[dict]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_reducere, denumire, procent "
                "FROM Reduceri ORDER BY procent ASC"
            )
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def search_curse(
        self,
        id_statie_urcare: int | None = None,
        id_statie_coborare: int | None = None,
        data_filter: str | None = None,
    ) -> list[dict]:
        """
        Cauta curse active (neanulate).
        Daca sunt specificate statii de urcare si coborare, returneaza doar cursele care
        opresc in ambele in ordinea corecta (ou.ordine < oc.ordine), cu orele si distanta pe segment.
        Altfel returneaza toate cursele disponibile de la prima la ultima oprire a rutei.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            params: list = []
            if id_statie_urcare is not None and id_statie_coborare is not None:
                segment_filter = "AND ou.id_statie = %s AND oc.id_statie = %s"
                params.extend([id_statie_urcare, id_statie_coborare])
            else:
                segment_filter = (
                    "AND ou.ordine = (SELECT MIN(o1.ordine) FROM Opriri o1 WHERE o1.id_ruta = c.id_ruta) "
                    "AND oc.ordine = (SELECT MAX(o2.ordine) FROM Opriri o2 WHERE o2.id_ruta = c.id_ruta)"
                )

            date_filter_sql = ""
            if data_filter:
                date_filter_sql = "AND c.data_cursa = %s"
                params.append(data_filter)

            query = f"""
                SELECT
                    c.id_cursa,
                    c.id_ruta,
                    r.denumire AS ruta,
                    c.id_tren,
                    t.nume AS tren,
                    tt.denumire AS tip_tren,
                    tt.coeficient_pret,
                    DATE_FORMAT(c.data_cursa, '%Y-%m-%d') AS data_cursa,
                    c.status,
                    c.intarziere_minute,
                    ou.id_statie AS id_statie_urcare,
                    su.nume AS statie_urcare,
                    ou.ordine AS ordine_urcare,
                    oc.id_statie AS id_statie_coborare,
                    sc.nume AS statie_coborare,
                    oc.ordine AS ordine_coborare,
                    ROUND(oc.distanta - ou.distanta, 1) AS distanta_km,
                    TIME_FORMAT(
                        SEC_TO_TIME(
                            MOD(
                                TIME_TO_SEC(c.ora_plecare)
                                + TIME_TO_SEC(ou.ora_plecare)
                                - TIME_TO_SEC(o_start.ora_plecare),
                                86400
                            )
                        ),
                        '%H:%i'
                    ) AS ora_plecare_segment,
                    TIME_FORMAT(
                        SEC_TO_TIME(
                            MOD(
                                TIME_TO_SEC(c.ora_plecare)
                                + TIME_TO_SEC(oc.ora_sosire)
                                - TIME_TO_SEC(o_start.ora_plecare),
                                86400
                            )
                        ),
                        '%H:%i'
                    ) AS ora_sosire_segment,
                    (
                        SELECT COUNT(*)
                        FROM Locuri l
                        JOIN Vagoane v ON l.id_vagon = v.id_vagon
                        WHERE v.id_tren = c.id_tren
                          AND NOT EXISTS (
                              SELECT 1
                              FROM Bilete b
                              JOIN Opriri bo_u
                                ON bo_u.id_ruta = c.id_ruta AND bo_u.id_statie = b.id_statie_urcare
                              JOIN Opriri bo_c
                                ON bo_c.id_ruta = c.id_ruta AND bo_c.id_statie = b.id_statie_coborare
                              WHERE b.id_cursa = c.id_cursa
                                AND b.id_loc = l.id_loc
                                AND b.status_bilet = 'valid'
                                AND bo_u.ordine < oc.ordine
                                AND bo_c.ordine > ou.ordine
                          )
                    ) AS locuri_libere
                FROM Curse c
                JOIN Rute r ON c.id_ruta = r.id_ruta
                JOIN Trenuri t ON c.id_tren = t.id_tren
                JOIN Tipuri_tren tt ON t.id_tip = tt.id_tip
                JOIN Opriri ou ON ou.id_ruta = c.id_ruta
                JOIN Opriri oc ON oc.id_ruta = c.id_ruta AND ou.ordine < oc.ordine
                JOIN Opriri o_start
                    ON o_start.id_ruta = c.id_ruta
                   AND o_start.ordine = (
                       SELECT MIN(os.ordine) FROM Opriri os WHERE os.id_ruta = c.id_ruta
                   )
                JOIN Statii su ON su.id_statie = ou.id_statie
                JOIN Statii sc ON sc.id_statie = oc.id_statie
                WHERE c.status <> 'anulata'
                  {segment_filter}
                  {date_filter_sql}
                ORDER BY c.data_cursa ASC, ora_plecare_segment ASC
            """

            cursor.execute(query, params)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def get_available_seats(
        self,
        id_cursa: int,
        id_ruta: int,
        id_tren: int,
        ordine_urcare: int,
        ordine_coborare: int,
    ) -> list[dict]:
        """Returneaza locurile libere pe segmentul [ordine_urcare, ordine_coborare] pentru o cursa."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT l.id_loc, l.nr_loc, v.nr_vagon, v.clasa
                FROM Locuri l
                JOIN Vagoane v ON l.id_vagon = v.id_vagon
                WHERE v.id_tren = %s
                  AND NOT EXISTS (
                      SELECT 1
                      FROM Bilete b
                      JOIN Opriri bo_u
                        ON bo_u.id_ruta = %s AND bo_u.id_statie = b.id_statie_urcare
                      JOIN Opriri bo_c
                        ON bo_c.id_ruta = %s AND bo_c.id_statie = b.id_statie_coborare
                      WHERE b.id_cursa = %s
                        AND b.id_loc = l.id_loc
                        AND b.status_bilet = 'valid'
                        AND bo_u.ordine < %s
                        AND bo_c.ordine > %s
                  )
                ORDER BY v.clasa ASC, v.nr_vagon ASC, l.nr_loc ASC
                """,
                (id_tren, id_ruta, id_ruta, id_cursa, ordine_coborare, ordine_urcare),
            )
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def buy_bilet(
        self,
        id_client: int,
        id_cursa: int,
        id_ruta: int,
        id_loc: int,
        id_statie_urcare: int,
        id_statie_coborare: int,
        ordine_urcare: int,
        ordine_coborare: int,
        id_reducere: int | None,
        pret_platit: float,
    ) -> tuple[bool, str]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Reverifica disponibilitatea locului inainte de inserare pentru siguranta
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM Bilete b
                JOIN Opriri bo_u
                  ON bo_u.id_ruta = %s AND bo_u.id_statie = b.id_statie_urcare
                JOIN Opriri bo_c
                  ON bo_c.id_ruta = %s AND bo_c.id_statie = b.id_statie_coborare
                WHERE b.id_cursa = %s
                  AND b.id_loc = %s
                  AND b.status_bilet = 'valid'
                  AND bo_u.ordine < %s
                  AND bo_c.ordine > %s
                """,
                (id_ruta, id_ruta, id_cursa, id_loc, ordine_coborare, ordine_urcare),
            )
            if cursor.fetchone()[0] > 0:
                return False, "Locul selectat a fost deja ocupat pe acest segment. Alege alt loc."

            cursor.execute(
                """
                INSERT INTO Bilete (
                    id_client, id_cursa, id_loc, id_statie_urcare,
                    id_statie_coborare, id_reducere, pret_platit, status_bilet
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'valid')
                """,
                (
                    id_client,
                    id_cursa,
                    id_loc,
                    id_statie_urcare,
                    id_statie_coborare,
                    id_reducere,
                    pret_platit,
                ),
            )
            conn.commit()
            return True, f"Biletul #{cursor.lastrowid} a fost cumparat cu succes ({pret_platit:.2f} RON)!"
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return False, f"Eroare la emiterea biletului ({err.errno}): {err.msg}"
        finally:
            if conn:
                conn.close()

    def get_client_bilete(self, id_client: int) -> list[dict]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    b.id_bilet,
                    DATE_FORMAT(c.data_cursa, '%Y-%m-%d') AS data_cursa,
                    TIME_FORMAT(c.ora_plecare, '%H:%i') AS ora_plecare,
                    r.denumire AS ruta,
                    t.nume AS tren,
                    su.nume AS statie_urcare,
                    sc.nume AS statie_coborare,
                    v.nr_vagon,
                    v.clasa,
                    l.nr_loc,
                    COALESCE(red.denumire, 'Fara reducere') AS reducere,
                    b.pret_platit,
                    b.status_bilet,
                    DATE_FORMAT(b.data_cumpararii, '%Y-%m-%d %H:%i') AS data_cumpararii
                FROM Bilete b
                JOIN Curse c ON b.id_cursa = c.id_cursa
                JOIN Rute r ON c.id_ruta = r.id_ruta
                JOIN Trenuri t ON c.id_tren = t.id_tren
                JOIN Statii su ON b.id_statie_urcare = su.id_statie
                JOIN Statii sc ON b.id_statie_coborare = sc.id_statie
                JOIN Locuri l ON b.id_loc = l.id_loc
                JOIN Vagoane v ON l.id_vagon = v.id_vagon
                LEFT JOIN Reduceri red ON b.id_reducere = red.id_reducere
                WHERE b.id_client = %s
                ORDER BY b.data_cumpararii DESC, b.id_bilet DESC
                """,
                (id_client,),
            )
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def cancel_bilet(self, id_bilet: int, id_client: int) -> tuple[bool, str]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE Bilete
                SET status_bilet = 'anulat'
                WHERE id_bilet = %s AND id_client = %s AND status_bilet = 'valid'
                """,
                (id_bilet, id_client),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return False, "Biletul nu a putut fi anulat (este deja anulat sau nu iti apartine)."
            return True, f"Biletul #{id_bilet} a fost anulat cu succes."
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return False, f"Eroare la anularea biletului ({err.errno}): {err.msg}"
        finally:
            if conn:
                conn.close()
