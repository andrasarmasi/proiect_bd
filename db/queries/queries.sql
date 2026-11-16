USE aplicatie_trenuri;

SELECT id_client, nume, prenume, email, parola_hash 
FROM Clienti 
WHERE email = 'andrei.popescu@gmail.com';

SELECT id_cursa, id_ruta, id_tren, ora_plecare, status, intarziere_minute
FROM Curse
WHERE data_cursa = '2026-11-20' AND status <> 'anulata'
ORDER BY ora_plecare ASC;

SELECT id_statie, nume, judet 
FROM Statii 
WHERE oras LIKE 'Bucuresti%' AND activ = TRUE;

SELECT o.ordine, s.nume AS statie, o.ora_sosire, o.ora_plecare, o.distanta
FROM Opriri o
JOIN Statii s ON o.id_statie = s.id_statie
WHERE o.id_ruta = 1
ORDER BY o.ordine ASC;

SELECT c.id_cursa, c.data_cursa, c.ora_plecare, r.denumire AS ruta, t.nume AS tren, tt.denumire AS categorie
FROM Curse c
JOIN Rute r ON c.id_ruta = r.id_ruta
JOIN Trenuri t ON c.id_tren = t.id_tren
JOIN Tipuri_tren tt ON t.id_tip = tt.id_tip
WHERE c.data_cursa = '2026-11-20';

SELECT l.id_loc, l.nr_loc, v.nr_vagon, v.clasa
FROM Locuri l
JOIN Vagoane v ON l.id_vagon = v.id_vagon
WHERE v.id_tren = 1 AND v.nr_vagon = 1
ORDER BY l.nr_loc ASC;

INSERT INTO Clienti (nume, prenume, email, parola_hash, nr_telefon)
VALUES ('Vasile', 'Dan', 'dan.vasile@gmail.com', '$2y$10$hashNou123456789', '0733123456');

INSERT INTO Bilete (id_client, id_cursa, id_loc, id_statie_urcare, id_statie_coborare, id_reducere, pret_platit, status_bilet)
VALUES (1, 1, 5, 1, 4, 2, 25.00, 'valid');

UPDATE Bilete
SET status_bilet = 'anulat'
WHERE id_bilet = 4 AND id_client = 1;

UPDATE Curse
SET status = 'intarziata', intarziere_minute = 20
WHERE id_cursa = 2;

UPDATE Rute
SET activ = FALSE
WHERE id_ruta = 4;

DELETE FROM Clienti
WHERE id_client = 5;

SELECT b.id_bilet, c.data_cursa, r.denumire AS ruta, su.nume AS urcare, sc.nume AS coborare, b.pret_platit, b.status_bilet
FROM Bilete b
JOIN Curse c ON b.id_cursa = c.id_cursa
JOIN Rute r ON c.id_ruta = r.id_ruta
JOIN Statii su ON b.id_statie_urcare = su.id_statie
JOIN Statii sc ON b.id_statie_coborare = sc.id_statie
WHERE b.id_client = 1
ORDER BY b.data_cumpararii DESC;

SELECT t.nume AS tren, COUNT(v.id_vagon) AS numar_vagoane
FROM Trenuri t
LEFT JOIN Vagoane v ON t.id_tren = v.id_tren
GROUP BY t.id_tren, t.nume;

SELECT c.id_cursa, c.data_cursa, COUNT(b.id_bilet) AS bilete_vandute, COALESCE(SUM(b.pret_platit), 0) AS total_incasat
FROM Curse c
LEFT JOIN Bilete b ON c.id_cursa = b.id_cursa AND b.status_bilet = 'valid'
GROUP BY c.id_cursa, c.data_cursa;

SELECT c.id_cursa, c.data_cursa, SUM(b.pret_platit) AS incasari_totale
FROM Curse c
JOIN Bilete b ON c.id_cursa = b.id_cursa
WHERE b.status_bilet = 'valid'
GROUP BY c.id_cursa, c.data_cursa
HAVING SUM(b.pret_platit) > 50.00;

SELECT id_bilet, id_client, pret_platit, data_cumpararii
FROM Bilete
WHERE pret_platit > (SELECT AVG(pret_platit) FROM Bilete WHERE status_bilet = 'valid');

SELECT id_statie, nume, oras 
FROM Statii
WHERE id_statie NOT IN (SELECT DISTINCT id_statie FROM Opriri);

CREATE OR REPLACE VIEW v_curse_detaliate AS
SELECT c.id_cursa, c.data_cursa, c.ora_plecare, r.denumire AS ruta, t.nume AS tren, c.status
FROM Curse c
JOIN Rute r ON c.id_ruta = r.id_ruta
JOIN Trenuri t ON c.id_tren = t.id_tren;

SELECT * FROM v_curse_detaliate WHERE status = 'la timp';


