# Cahier des Charges - AGEN-OHADA (Version Flask)

## 1. Introduction
### 1.1 Contexte du Projet
- Solution moderne de gestion notariale pour les études en zone OHADA.
- Remplace les processus manuels par une automatisation sécurisée.

### 1.2 Objectifs
- **Productivité :** Réduction du temps de rédaction des actes.
- **Conformité :** Respect strict des normes comptables et juridiques OHADA.
- **Sécurité :** Traçabilité totale des opérations et archivage immuable.

## 2. Description Fonctionnelle
### 2.1 CRM & Dossiers
- **Gestion Clients :** Distinction Personnes Physiques/Morales, historique complet.
- **Suivi Dossiers :** Numérotation dynamique, gestion des parties prenantes par rôle.
- **Archivage :** Verrouillage des dossiers clôturés et transfert sécurisé des documents.

### 2.2 Moteur de Rédaction (Deed Engine)
- **Modèles Hybrides :** 
    - **Markdown/Jinja2** pour la structure simple.
    - **Microsoft Word (.docx)** pour les templates complexes avec fusion de champs dynamique via `docxtpl`.
- **Validation & Signature :** Workflow de révision par le Notaire avant finalisation et signature électronique (hashage).
- **Répertoire Notarial :** Attribution automatique d'un numéro de répertoire annuel unique lors de l'archivage.

### 2.3 Comptabilité Notariale
- **Double-Entry :** Système de comptabilité en partie double.
- **Sécurisation :** Séparation stricte entre Comptes Office et Comptes Client.
- **Automatisation :** Génération automatique d'écritures lors de l'émission de reçus et factures.

### 2.4 Formalités et Aide
- **Workflow Formalités :** Suivi étape par étape (Dépôt, Enregistrement, Retour).
- **Calculateur :** Moteur d'estimation des frais basé sur les barèmes légaux OHADA.
- **Aide en Ligne :** Manuel utilisateur interactif intégré directement dans l'application.

## 3. Architecture Technique
- **Framework :** Flask (Python 3.12+)
- **Base de données :** PostgreSQL (SQLAlchemy ORM)
- **Génération Documents :** `docxtpl` (Word), `WeasyPrint` / `xhtml2pdf` (PDF).
- **Frontend :** Tailwind CSS, Alpine.js, EasyMDE.
- **Déploiement :** PaaS (Koyeb), Dockerized (Python 3.12-slim-bookworm).

## 4. Livrables
- Code source complet (Git).
- Documentation technique et API.
- Manuel Utilisateur (v1.1.0) et Manuel de Tests.
- Plan de sauvegarde et rapports de migration production.
