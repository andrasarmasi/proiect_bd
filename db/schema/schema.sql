DROP DATABASE IF EXISTS aplicatie_trenuri;
CREATE DATABASE aplicatie_trenuri CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aplicatie_trenuri;

CREATE TABLE Admini (
    id_admin INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(50) NOT NULL,
    prenume VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    parola_hash VARCHAR(255) NOT NULL
);

CREATE TABLE Tipuri_tren (
    id_tip INT AUTO_INCREMENT PRIMARY KEY,
    denumire VARCHAR(30) NOT NULL UNIQUE,
    coeficient_pret DECIMAL(4,2) NOT NULL CHECK (coeficient_pret > 0)
);

CREATE TABLE Trenuri (
    id_tren INT AUTO_INCREMENT PRIMARY KEY,
    id_tip INT NOT NULL,
    nume VARCHAR(50) NOT NULL UNIQUE,
    activ BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_tren_tip FOREIGN KEY (id_tip) 
        REFERENCES Tipuri_tren(id_tip) 
        ON DELETE RESTRICT
);

CREATE TABLE Vagoane (
    id_vagon INT AUTO_INCREMENT PRIMARY KEY,
    id_tren INT NOT NULL,
    nr_vagon SMALLINT NOT NULL CHECK (nr_vagon >= 1),
    clasa SMALLINT NOT NULL CHECK (clasa IN (1, 2)),
    CONSTRAINT fk_vagon_tren FOREIGN KEY (id_tren) 
        REFERENCES Trenuri(id_tren) 
        ON DELETE RESTRICT,
    CONSTRAINT uq_tren_nr_vagon UNIQUE (id_tren, nr_vagon)
);

CREATE TABLE Locuri (
    id_loc INT AUTO_INCREMENT PRIMARY KEY,
    id_vagon INT NOT NULL,
    nr_loc SMALLINT NOT NULL CHECK (nr_loc >= 1),
    CONSTRAINT fk_loc_vagon FOREIGN KEY (id_vagon) 
        REFERENCES Vagoane(id_vagon) 
        ON DELETE RESTRICT,
    CONSTRAINT uq_vagon_nr_loc UNIQUE (id_vagon, nr_loc)
);


CREATE TABLE Rute (
    id_ruta INT AUTO_INCREMENT PRIMARY KEY,
    denumire VARCHAR(100) NOT NULL UNIQUE,
    activ BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE Statii (
    id_statie INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(100) NOT NULL,
    oras VARCHAR(100) NOT NULL,
    judet VARCHAR(50) NOT NULL,
    activ BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_statie_oras UNIQUE (nume, oras)
);

CREATE TABLE Opriri (
    id_oprire INT AUTO_INCREMENT PRIMARY KEY,
    id_ruta INT NOT NULL,
    id_statie INT NOT NULL,
    ordine SMALLINT NOT NULL CHECK (ordine >= 1),
    ora_sosire TIME NULL,
    ora_plecare TIME NULL,
    distanta DECIMAL(6,1) NOT NULL CHECK (distanta >= 0),
    CONSTRAINT fk_oprire_ruta FOREIGN KEY (id_ruta) 
        REFERENCES Rute(id_ruta) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_oprire_statie FOREIGN KEY (id_statie) 
        REFERENCES Statii(id_statie) 
        ON DELETE RESTRICT,
    CONSTRAINT uq_ruta_statie UNIQUE (id_ruta, id_statie),
    CONSTRAINT uq_ruta_ordine UNIQUE (id_ruta, ordine)
);

CREATE TABLE Curse (
    id_cursa INT AUTO_INCREMENT PRIMARY KEY,
    id_admin INT NOT NULL,
    id_ruta INT NOT NULL,
    id_tren INT NOT NULL,
    data_cursa DATE NOT NULL,
    ora_plecare TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'la timp' 
        CHECK (status IN ('la timp', 'intarziata', 'anulata')),
    intarziere_minute SMALLINT NOT NULL DEFAULT 0 
        CHECK (intarziere_minute >= 0),
    CONSTRAINT fk_cursa_admin FOREIGN KEY (id_admin) 
        REFERENCES Admini(id_admin) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_cursa_ruta FOREIGN KEY (id_ruta) 
        REFERENCES Rute(id_ruta) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_cursa_tren FOREIGN KEY (id_tren) 
        REFERENCES Trenuri(id_tren) 
        ON DELETE RESTRICT,
    CONSTRAINT uq_cursa_plecare UNIQUE (id_ruta, id_tren, data_cursa, ora_plecare)
);

CREATE TABLE Clienti (
    id_client INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(50) NOT NULL,
    prenume VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    parola_hash VARCHAR(255) NOT NULL,
    nr_telefon VARCHAR(15) NULL
);

CREATE TABLE Reduceri (
    id_reducere INT AUTO_INCREMENT PRIMARY KEY,
    denumire VARCHAR(50) NOT NULL UNIQUE,
    procent DECIMAL(5,2) NOT NULL CHECK (procent BETWEEN 0 AND 100)
);

CREATE TABLE Bilete (
    id_bilet INT AUTO_INCREMENT PRIMARY KEY,
    id_client INT NOT NULL,
    id_cursa INT NOT NULL,
    id_loc INT NOT NULL,
    id_statie_urcare INT NOT NULL,
    id_statie_coborare INT NOT NULL,
    id_reducere INT NULL,
    pret_platit DECIMAL(8,2) NOT NULL CHECK (pret_platit >= 0),
    status_bilet VARCHAR(10) NOT NULL DEFAULT 'valid' 
        CHECK (status_bilet IN ('valid', 'anulat')),
    data_cumpararii TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bilet_client FOREIGN KEY (id_client) 
        REFERENCES Clienti(id_client) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_bilet_cursa FOREIGN KEY (id_cursa) 
        REFERENCES Curse(id_cursa) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_bilet_loc FOREIGN KEY (id_loc) 
        REFERENCES Locuri(id_loc) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_bilet_urcare FOREIGN KEY (id_statie_urcare) 
        REFERENCES Statii(id_statie) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_bilet_coborare FOREIGN KEY (id_statie_coborare) 
        REFERENCES Statii(id_statie) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_bilet_reducere FOREIGN KEY (id_reducere) 
        REFERENCES Reduceri(id_reducere) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_statii_diferite CHECK (id_statie_urcare <> id_statie_coborare)
);


CREATE TABLE Predictii_Aglomerare (
    id_predictie INT AUTO_INCREMENT PRIMARY KEY,
    id_cursa INT NOT NULL,
    grad_ocupare_estimat DECIMAL(5,2) NOT NULL,
    nivel_aglomerare VARCHAR(20) NOT NULL, -- 'Scazut', 'Mediu', 'Ridicat'
    data_predictie TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pred_cursa FOREIGN KEY (id_cursa) 
        REFERENCES Curse(id_cursa) 
        ON DELETE CASCADE
);

CREATE INDEX idx_opriri_cautare ON Opriri (id_statie, id_ruta, ordine);
CREATE INDEX idx_curse_cautare ON Curse (data_cursa, id_ruta, status);
CREATE INDEX idx_bilete_loc_cursa ON Bilete (id_cursa, id_loc, status_bilet);
