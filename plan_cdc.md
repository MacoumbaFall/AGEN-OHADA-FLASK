# Cahier des Charges - AGEN-OHADA (Version Flask)

## 1. Introduction
### 1.1 Contexte du Projet
- Solution moderne de gestion notariale pour les études en zone OHADA.
- Remplace les processus manuels par une automatisation sécurisée.

### 1.2 Objectifs
- **Productivité :** Réduction du temps de rédaction des actes.
- **Conformité :** Respect strict des normes comptables et juridiques OHADA.
- **Sécurité :** Traçabilité totale des opérations.

## 2. Description Fonctionnelle
### 2.1 CRM & Dossiers
- **Gestion Clients :** Distinction Personnes Physiques/Morales, historique complet.
- **Suivi Dossiers :** Numérotation dynamique, gestion des parties prenantes par rôle.

### 2.2 Moteur de Rédaction (Deed Engine)
- **Templates :** Utilisation de Markdown pour la structure et Jinja2 pour le dynamisme.
- **Éditeur EasyMDE :** Interface WYSIWYG avec aide à l'insertion de variables et prévisualisation temps réel.
- **Génération PDF :** Export haute qualité via `xhtml2pdf`.

### 2.3 Comptabilité Notariale
- **Double-Entry :** Système de comptabilité en partie double.
- **Sécurisation :** Séparation stricte entre Comptes Office et Comptes Client.
- **Automatisation :** Génération automatique d'écritures lors de l'émission de reçus.

### 2.4 Formalités
- **Workflow :** Suivi étape par étape (Dépôt, Enregistrement, Retour).
- **Calculateur :** Moteur d'estimation des frais basé sur les barèmes légaux.

## 3. Architecture Technique
- **Framework :** Flask (Python 3.10+)
- **Base de données :** PostgreSQL (SQLAlchemy ORM)
- **Frontend :** Tailwind CSS, Alpine.js, EasyMDE.
- **Déploiement :** Compatible Gunicorn/Nginx, Dockerized.

## 4. Livrables
- Code source complet.
- Documentation technique et API.
- Manuel Utilisateur et Manuel de Tests.
- Plan de sauvegarde et guides de déploiement.
