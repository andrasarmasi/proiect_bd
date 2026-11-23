import mysql.connector

from config.db_config import get_connection


class DatabaseError(Exception):
    """Eroare generica de acces la baza de date, decuplata de driverul MySQL."""


class CursaModel:
    """Model responsabil exclusiv de operatiile SQL pentru gestiunea curselor."""

    @staticmethod
    def format_db_error(err: mysql.connector.Error) -> str:
        code = err.errno
        if code == 1062:
            return (
                "Constrangere UNIQUE incalcata (uq_cursa_plecare)!\n"
                "Exista deja o cursa cu aceeasi ruta, acelasi tren, aceeasi data si ora de plecare."
            )
        if code == 1451:
            return (
                "Constrangere ON DELETE RESTRICT activata!\n"
                "Nu poti sterge aceasta cursa deoarece exista deja bilete emise pentru ea.\n"
                "Pentru anulare, schimba statusul cursei in 'anulata'."
            )
        if code in (3819, 4025):
            return (
                "Constrangere CHECK incalcata!\n"
                "Verifica valorile introduse (ex: intarziere_minute >= 0, status valid)."
            )
        if code == 1292:
            return (
                "Format invalid pentru data sau ora!\n"
                "Foloseste YYYY-MM-DD pentru data si HH:MM:SS pentru ora."
            )
        return f"Eroare baza de date ({code}): {err.msg}"

    def get_active_rute(self) -> list[dict]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_ruta, denumire FROM Rute WHERE activ = TRUE ORDER BY id_ruta ASC"
            )
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def get_active_trenuri(self) -> list[dict]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_tren, nume FROM Trenuri WHERE activ = TRUE ORDER BY id_tren ASC"
            )
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def get_all_admini(self) -> list[dict]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_admin, CONCAT(prenume, ' ', nume) AS nume_complet "
                "FROM Admini ORDER BY id_admin ASC"
            )
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def get_all_curse(self, data_filter: str | None = None) -> list[dict]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT
                    c.id_cursa,
                    c.id_admin,
                    CONCAT(a.prenume, ' ', a.nume) AS admin_nume,
                    c.id_ruta,
                    r.denumire AS ruta,
                    c.id_tren,
                    t.nume AS tren,
                    DATE_FORMAT(c.data_cursa, '%Y-%m-%d') AS data_cursa,
                    TIME_FORMAT(c.ora_plecare, '%H:%i:%s') AS ora_plecare,
                    c.status,
                    c.intarziere_minute
                FROM Curse c
                JOIN Rute r ON c.id_ruta = r.id_ruta
                JOIN Trenuri t ON c.id_tren = t.id_tren
                JOIN Admini a ON c.id_admin = a.id_admin
            """
            params = []
            if data_filter:
                query += " WHERE c.data_cursa = %s"
                params.append(data_filter)
            query += " ORDER BY c.data_cursa ASC, c.ora_plecare ASC"

            cursor.execute(query, params)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def add_cursa(
        self,
        id_admin: int,
        id_ruta: int,
        id_tren: int,
        data_cursa: str,
        ora_plecare: str,
        status: str,
        intarziere_minute: int,
    ) -> tuple[bool, str]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Curse (
                    id_admin, id_ruta, id_tren, data_cursa, ora_plecare, status, intarziere_minute
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (id_admin, id_ruta, id_tren, data_cursa, ora_plecare, status, intarziere_minute),
            )
            conn.commit()
            return True, f"Cursa a fost adaugata cu succes (ID: {cursor.lastrowid})."
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return False, self.format_db_error(err)
        finally:
            if conn:
                conn.close()

    def update_cursa(
        self,
        id_cursa: int,
        id_admin: int,
        id_ruta: int,
        id_tren: int,
        data_cursa: str,
        ora_plecare: str,
        status: str,
        intarziere_minute: int,
    ) -> tuple[bool, str]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE Curse
                SET id_admin = %s,
                    id_ruta = %s,
                    id_tren = %s,
                    data_cursa = %s,
                    ora_plecare = %s,
                    status = %s,
                    intarziere_minute = %s
                WHERE id_cursa = %s
                """,
                (
                    id_admin,
                    id_ruta,
                    id_tren,
                    data_cursa,
                    ora_plecare,
                    status,
                    intarziere_minute,
                    id_cursa,
                ),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return (
                    False,
                    "Nu s-a modificat niciun rand (ID-ul nu a fost gasit sau datele sunt identice).",
                )
            return True, f"Cursa cu ID {id_cursa} a fost actualizata."
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return False, self.format_db_error(err)
        finally:
            if conn:
                conn.close()

    def delete_cursa(self, id_cursa: int) -> tuple[bool, str]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Curse WHERE id_cursa = %s", (id_cursa,))
            conn.commit()
            if cursor.rowcount == 0:
                return False, "Cursa selectata nu mai exista."
            return True, f"Cursa cu ID {id_cursa} a fost stearsa."
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return False, self.format_db_error(err)
        finally:
            if conn:
                conn.close()
