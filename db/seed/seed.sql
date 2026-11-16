

USE mersul_trenurilor;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE Bilete;
TRUNCATE TABLE Curse;
TRUNCATE TABLE Opriri;
TRUNCATE TABLE Locuri;
TRUNCATE TABLE Vagoane;
TRUNCATE TABLE Trenuri;
TRUNCATE TABLE Rute;
TRUNCATE TABLE Statii;
TRUNCATE TABLE Reduceri;
TRUNCATE TABLE Tipuri_tren;
TRUNCATE TABLE Clienti;
TRUNCATE TABLE Admini;

SET FOREIGN_KEY_CHECKS = 1;


INSERT INTO Admini (id_admin, nume, prenume, email, parola_hash) VALUES
(1, 'Ionescu', 'Mihai', 'admin.ionescu@cfr-proiect.ro', '$2y$10$e8mUjC.x9jK1fF5v4N2qUeY8w7h9x3p0qL1z6aB8c5d2e3f4g5h6i'),
(2, 'Popa', 'Elena', 'admin.popa@cfr-proiect.ro', '$2y$10$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a');


INSERT INTO Tipuri_tren (id_tip, denumire, coeficient_pret) VALUES
(1, 'Regio (R)', 1.00),
(2, 'InterRegio (IR)', 1.35),
(3, 'InterCity (IC)', 1.70);


INSERT INTO Trenuri (id_tren, id_tip, nume, activ) VALUES
(1, 3, 'IC 531 "Astra"', TRUE),
(2, 2, 'IR 1745 "Transilvania"', TRUE),
(3, 1, 'R 4110 "Somes"', TRUE),
(4, 2, 'IR 1632 "Carpati"', TRUE),
(5, 1, 'R 3001 (Retras)', FALSE);


INSERT INTO Vagoane (id_vagon, id_tren, nr_vagon, clasa) VALUES
(1, 1, 1, 1), -- Tren 1: Vagon 1 (Clasa 1)
(2, 1, 2, 2), -- Tren 1: Vagon 2 (Clasa 2)
(3, 2, 1, 1), -- Tren 2: Vagon 1 (Clasa 1)
(4, 2, 2, 2), -- Tren 2: Vagon 2 (Clasa 2)
(5, 3, 1, 2); -- Tren 3: Vagon 1 (Clasa 2)


INSERT INTO Locuri (id_loc, id_vagon, nr_loc) VALUES
-- Tren 1, Vagon 1 (Clasa 1)
(1, 1, 11), (2, 1, 12), (3, 1, 13), (4, 1, 14),
-- Tren 1, Vagon 2 (Clasa 2)
(5, 2, 21), (6, 2, 22), (7, 2, 23), (8, 2, 24),
-- Tren 2, Vagon 1 (Clasa 1)
(9, 3, 11), (10, 3, 12),
-- Tren 2, Vagon 2 (Clasa 2)
(11, 4, 21), (12, 4, 22), (13, 4, 23), (14, 4, 24),
-- Tren 3, Vagon 1 (Clasa 2)
(15, 5, 1), (16, 5, 2), (17, 5, 3), (18, 5, 4);


INSERT INTO Statii (id_statie, nume, oras, judet, activ) VALUES
(1, 'Bucuresti Nord', 'Bucuresti', 'Bucuresti', TRUE),
(2, 'Ploiesti Vest', 'Ploiesti', 'Prahova', TRUE),
(3, 'Sinaia', 'Sinaia', 'Prahova', TRUE),
(4, 'Brasov', 'Brasov', 'Brasov', TRUE),
(5, 'Cluj-Napoca', 'Cluj-Napoca', 'Cluj', TRUE),
(6, 'Dej Calatori', 'Dej', 'Cluj', TRUE),
(7, 'Baia Mare', 'Baia Mare', 'Maramures', TRUE),
(8, 'Halta Veche Vale', 'Valea Lunga', 'Alba', FALSE);


INSERT INTO Rute (id_ruta, denumire, activ) VALUES
(1, 'Bucuresti Nord - Brasov', TRUE),
(2, 'Cluj-Napoca - Baia Mare', TRUE),
(3, 'Bucuresti Nord - Cluj-Napoca (via Brasov)', TRUE),
(4, 'Ruta Veche Inchisa', FALSE);


-- Ruta 1: Bucuresti Nord -> Brasov (166 km)
INSERT INTO Opriri (id_oprire, id_ruta, id_statie, ordine, ora_sosire, ora_plecare, distanta) VALUES
(1, 1, 1, 1, NULL, '06:00:00', 0.0),
(2, 1, 2, 2, '06:40:00', '06:43:00', 59.0),
(3, 1, 3, 3, '07:35:00', '07:38:00', 121.0),
(4, 1, 4, 4, '08:30:00', NULL, 166.0);

-- Ruta 2: Cluj-Napoca -> Baia Mare (149 km)
INSERT INTO Opriri (id_oprire, id_ruta, id_statie, ordine, ora_sosire, ora_plecare, distanta) VALUES
(5, 2, 5, 1, NULL, '07:15:00', 0.0),
(6, 2, 6, 2, '08:10:00', '08:15:00', 59.0),
(7, 2, 7, 3, '10:05:00', NULL, 149.0);

-- Ruta 3: Bucuresti Nord -> Cluj-Napoca (497 km)
INSERT INTO Opriri (id_oprire, id_ruta, id_statie, ordine, ora_sosire, ora_plecare, distanta) VALUES
(8, 3, 1, 1, NULL, '14:00:00', 0.0),
(9, 3, 2, 2, '14:38:00', '14:40:00', 59.0),
(10, 3, 4, 3, '16:20:00', '16:30:00', 166.0),
(11, 3, 5, 4, '22:15:00', NULL, 497.0);


INSERT INTO Curse (id_cursa, id_admin, id_ruta, id_tren, data_cursa, ora_plecare, status, intarziere_minute) VALUES
(1, 1, 1, 1, '2026-11-20', '06:00:00', 'la timp', 0),
(2, 1, 1, 1, '2026-11-20', '16:00:00', 'intarziata', 25),
(3, 2, 2, 3, '2026-11-20', '07:15:00', 'la timp', 0),
(4, 1, 3, 2, '2026-11-21', '14:00:00', 'la timp', 0),
(5, 2, 1, 4, '2026-11-21', '06:00:00', 'anulata', 0);


INSERT INTO Reduceri (id_reducere, denumire, procent) VALUES
(1, 'Elev (100%)', 100.00),
(2, 'Student (90%)', 90.00),
(3, 'Pensionar (50%)', 50.00);


INSERT INTO Clienti (id_client, nume, prenume, email, parola_hash, nr_telefon) VALUES
(1, 'Popescu', 'Andrei', 'andrei.popescu@gmail.com', '$2y$10$hashclient1andrei1234567890abcdefghijklmnopq', '0722111222'),
(2, 'Radu', 'Ioana', 'ioana.radu@yahoo.com', '$2y$10$hashclient2ioana1234567890abcdefghijklmnopqr', '0744333444'),
(3, 'Stan', 'Cristian', 'cristi.stan@outlook.com', '$2y$10$hashclient3cristi1234567890abcdefghijklmnop', '0755666777'),
(4, 'Dumitru', 'Maria', 'maria.dumitru@gmail.com', '$2y$10$hashclient4maria1234567890abcdefghijklmnop', '0766888999');


INSERT INTO Bilete (id_bilet, id_client, id_cursa, id_loc, id_statie_urcare, id_statie_coborare, id_reducere, pret_platit, status_bilet, data_cumpararii) VALUES
(1, 1, 1, 5, 1, 2, NULL, 25.00, 'valid', '2026-11-18 10:15:00'),
(2, 2, 1, 5, 2, 4, 2, 4.50, 'valid', '2026-11-18 11:30:00'),
(3, 3, 1, 1, 1, 3, NULL, 62.00, 'valid', '2026-11-19 09:00:00'),
(4, 4, 1, 6, 1, 4, 3, 35.00, 'anulat', '2026-11-17 14:20:00'),
(5, 1, 3, 15, 5, 7, 2, 3.75, 'valid', '2026-11-19 16:45:00'),
(6, 2, 4, 11, 1, 5, NULL, 168.00, 'valid', '2026-11-19 18:00:00');
