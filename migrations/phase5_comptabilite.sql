-- Phase 5 Migration: Comptabilite Notariale
-- Adds new fields to existing tables and creates new tables for receipts and invoices.

-- Add new fields to compta_comptes
ALTER TABLE compta_comptes ADD COLUMN IF NOT EXISTS categorie VARCHAR(20);
ALTER TABLE compta_comptes ADD COLUMN IF NOT EXISTS actif BOOLEAN DEFAULT TRUE;

-- Add new field to compta_ecritures
ALTER TABLE compta_ecritures ADD COLUMN IF NOT EXISTS numero_piece VARCHAR(50);

-- Create recus table
CREATE TABLE IF NOT EXISTS recus (
    id SERIAL PRIMARY KEY,
    numero_recu VARCHAR(50) UNIQUE NOT NULL,
    date_emission DATE NOT NULL DEFAULT CURRENT_DATE,
    dossier_id INTEGER REFERENCES dossiers(id),
    client_id INTEGER REFERENCES clients(id),
    montant NUMERIC(15, 2) NOT NULL,
    mode_paiement VARCHAR(20) NOT NULL,
    reference_paiement VARCHAR(100),
    motif TEXT NOT NULL,
    ecriture_id INTEGER REFERENCES compta_ecritures(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create factures table
CREATE TABLE IF NOT EXISTS factures (
    id SERIAL PRIMARY KEY,
    numero_facture VARCHAR(50) UNIQUE NOT NULL,
    date_emission DATE NOT NULL DEFAULT CURRENT_DATE,
    date_echeance DATE,
    dossier_id INTEGER REFERENCES dossiers(id),
    client_id INTEGER REFERENCES clients(id),
    montant_ht NUMERIC(15, 2) NOT NULL,
    montant_tva NUMERIC(15, 2) DEFAULT 0,
    montant_ttc NUMERIC(15, 2) NOT NULL,
    statut VARCHAR(20) DEFAULT 'IMPAYEE',
    description TEXT NOT NULL,
    ecriture_id INTEGER REFERENCES compta_ecritures(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_recus_date ON recus(date_emission);
CREATE INDEX IF NOT EXISTS idx_recus_dossier ON recus(dossier_id);
CREATE INDEX IF NOT EXISTS idx_recus_client ON recus(client_id);

CREATE INDEX IF NOT EXISTS idx_factures_date ON factures(date_emission);
CREATE INDEX IF NOT EXISTS idx_factures_dossier ON factures(dossier_id);
CREATE INDEX IF NOT EXISTS idx_factures_client ON factures(client_id);
CREATE INDEX IF NOT EXISTS idx_factures_statut ON factures(statut);

-- Update existing accounts with categories (if they exist)
UPDATE compta_comptes SET categorie = 'OFFICE' WHERE numero_compte LIKE '%-OFFICE';
UPDATE compta_comptes SET categorie = 'CLIENT' WHERE numero_compte LIKE '%-CLIENT';
UPDATE compta_comptes SET categorie = 'CLIENT' WHERE numero_compte = '467';

