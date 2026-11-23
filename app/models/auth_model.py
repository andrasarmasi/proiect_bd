import hashlib
import hmac
import os

import mysql.connector

from config.db_config import get_connection
from models.cursa_model import DatabaseError

DEMO_ADMIN_PASSWORD = "admin123"
DEMO_CLIENT_PASSWORD = "client123"


def hash_password(password: str) -> str:
    """Genereaza un hash PBKDF2-HMAC-SHA256 cu salt aleatoriu."""
    salt = os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"pbkdf2_sha256${salt}${dk.hex()}"


def verify_password(password: str, stored_hash: str, role: str) -> bool:
    """Verifica parola impotriva hash-ului PBKDF2 sau a placeholder-elor din seed.sql."""
    if not stored_hash:
        return False

    if stored_hash.startswith("pbkdf2_sha256$"):
        parts = stored_hash.split("$")
        if len(parts) != 3:
            return False
        _, salt, expected_hex = parts
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
        return hmac.compare_digest(dk.hex(), expected_hex)

    # Compatibilitate cu hash-urile placeholder ($2y$10$...) din db/seed/seed.sql
    if stored_hash.startswith("$2y$"):
        demo_pass = DEMO_ADMIN_PASSWORD if role == "admin" else DEMO_CLIENT_PASSWORD
        return hmac.compare_digest(password, demo_pass)

    return hmac.compare_digest(password, stored_hash)


class AuthModel:
    """Model pentru autentificarea administratorilor/clientilor si inregistrarea clientilor."""

    def authenticate_admin(self, email: str, password: str) -> dict | None:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_admin, nume, prenume, email, parola_hash "
                "FROM Admini WHERE email = %s",
                (email,),
            )
            row = cursor.fetchone()
            if not row or not verify_password(password, row["parola_hash"], role="admin"):
                return None
            return {
                "role": "admin",
                "id": row["id_admin"],
                "nume": row["nume"],
                "prenume": row["prenume"],
                "nume_complet": f"{row['prenume']} {row['nume']}",
                "email": row["email"],
            }
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def authenticate_client(self, email: str, password: str) -> dict | None:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_client, nume, prenume, email, parola_hash, nr_telefon "
                "FROM Clienti WHERE email = %s",
                (email,),
            )
            row = cursor.fetchone()
            if not row or not verify_password(password, row["parola_hash"], role="client"):
                return None
            return {
                "role": "client",
                "id": row["id_client"],
                "nume": row["nume"],
                "prenume": row["prenume"],
                "nume_complet": f"{row['prenume']} {row['nume']}",
                "email": row["email"],
                "nr_telefon": row["nr_telefon"],
            }
        except mysql.connector.Error as err:
            raise DatabaseError(str(err)) from err
        finally:
            if conn:
                conn.close()

    def register_client(
        self,
        nume: str,
        prenume: str,
        email: str,
        password: str,
        nr_telefon: str | None = None,
    ) -> tuple[bool, str]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            pwd_hash = hash_password(password)
            telefon_val = nr_telefon.strip() if nr_telefon and nr_telefon.strip() else None
            cursor.execute(
                """
                INSERT INTO Clienti (nume, prenume, email, parola_hash, nr_telefon)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nume, prenume, email, pwd_hash, telefon_val),
            )
            conn.commit()
            return True, "Contul de client a fost creat cu succes! Te poti autentifica acum."
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            if err.errno == 1062:
                return False, "Exista deja un cont inregistrat cu aceasta adresa de email."
            return False, f"Eroare baza de date ({err.errno}): {err.msg}"
        finally:
            if conn:
                conn.close()
