# Plan de Travail Détaillé - AGEN-OHADA-FLASK
**Application de Gestion d'Étude Notariale OHADA (Version Flask)**

Version: 1.0.0 | Date de création: 15/12/2025

---

## 📊 État du Projet (Re-fondation)

**Progression globale : ~55%**

| Phase | Statut | Progression |
|-------|--------|-------------|
| Phase 0 : Infrastructure | ✅ Terminé | 100% |
| Phase 1 : Authentification | ✅ Terminé | 100% |
| Phase 2 : Gestion Dossiers | ✅ Terminé | 100% |
| Phase 3 : Rédaction Actes | ✅ Terminé | 100% |
| Phase 4 : Formalités | ✅ Terminé | 100% |
| Phase 5 : Comptabilité | ✅ Terminé | 100% |
| Phase 6 : Tests & QA | 📋 À venir | 0% |
| Phase 7 : Déploiement | 📋 À venir | 0% |

**Stack Technique :** Flask, SQLAlchemy, PostgreSQL, TailwindCSS.

---

## Phase 0 : Configuration de l'Infrastructure - ✅ TERMINÉ

### Objectif
Mettre en place l'environnement de développement Flask complet, la base de données et le frontend build system.

### Tâches
1.  **Environnement Python & Flask**
    -   [x] Vérifier l'installation des dépendances (`requirements.txt`).
    -   [x] Configurer l'application factory (`create_app`).
    -   [x] Configurer les variables d'environnement (`.env`).

2.  **Base de Données (PostgreSQL + SQLAlchemy)**
    -   [x] Configurer la connexion DB URI.
    -   [x] Mettre en place `Flask-Migrate` pour les migrations.
    -   [x] Créer le script d'initialisation DB.

3.  **Frontend (TailwindCSS)**
    -   [x] Configurer TailwindCSS (CLI ou Node).
    -   [x] Créer les templates de base (`base.html`, `auth.html`).
    -   [x] Mettre en place le pipeline de build CSS.

### Livrables
-   ✅ Serveur de développement fonctionnel.
-   ✅ Connexion BDD établie (`agen_ohada`).
-   ✅ Admin user créé (`admin`).

---

## Phase 1 : Socle Technique et Authentification (MVP) - ✅ TERMINÉ

### Objectif
Implémenter le système d'utilisateurs et la sécurité de base.

### Tâches
1.  **Modèles Données (User)**
    -   [x] Modèle `User` avec hachage de mot de passe (Werkzeug/Bcrypt).
    -   [x] Rôles utilisateurs (Enum: Notaire, Clerc, Comptable).

2.  **Authentification (Flask-Login)**
    -   [x] Routes: Login, Logout, Register (si nécessaire).
    -   [x] Protection des routes (`@login_required`).
    -   [x] Gestion de session sécurisée.

3.  **Interface Utilisateur de Base**
    -   [x] Page de Connexion (Design moderne).
    -   [x] Layout Dashboard (Sidebar, Navbar).
    -   [x] Page d'Accueil (Dashboard vide).

### Livrables
-   ✅ Système d'authentification complet.
-   ✅ Structure de navigation en place.

---

## Phase 2 : Module Gestion des Dossiers - ✅ TERMINÉ

### Objectif
Portage du module central de gestion des dossiers et des clients.

### Tâches
1.  **Modèles de Données**
    -   [x] Modèle `Client` (Physique/Morale).
    -   [x] Modèle `Dossier` (Numérotation, Type, Statut).
    -   [x] Table d'association `DossierClient` (Rôles: Vendeur, Acheteur...).

2.  **CRUD et Logique Métier**
    -   [x] Formulaires (WTForms ou JSON API).
    -   [x] Liste des dossiers (Datatables ou liste paginée).
    -   [x] Fiche détail dossier.
    -   [x] Workflow des statuts (Changement d'état).

3.  **Interface Dossiers**
    -   [x] Vues agréables pour la liste et les détails.
    -   [x] Widgets de résumé pour le Dashboard.

### Livrables
-   ✅ Gestion complète du cycle de vie d'un dossier.
-   ✅ Annuaire clients fonctionnel.

---

## Phase 3 : Module Rédaction d'Actes - ✅ TERMINÉ

### Objectif
Moteur de génération de documents dynamiques.

### Tâches
1.  **Gestion des Modèles**
    -   [x] Modèle `Template` (Stockage HTML/Markdown/Jinja).
    -   [x] Interface de création/édition de templates.

2.  **Génération d'Actes**
    -   [x] Moteur de substitution de variables (Jinja2 sandbox).
    -   [x] Formulaire de "fusion" (choix dossier -> remplissage auto).
    -   [x] Éditeur WYSIWYG pour retouches manuelles.

3.  **Export**
    -   [x] Génération PDF (WeasyPrint ou wkhtmltopdf).

### Livrables
-   ✅ Système de rédaction d'actes automatisé.

---

## Phase 4 : Module Formalités - ✅ TERMINÉ

### Objectif
Suivi administratif et financier des actes.

### Tâches
1.  **Calculateur**
    -   [x] Moteur de règles pour les émoluments OHADA.
    -   [x] Simulation de frais.

2.  **Suivi**
    -   [x] Workflow des formalités (Dépôt, Retour, Paiement).
    -   [x] Calendrier/Rappels.
    -   [x] Interface de gestion complète (Liste, Création, Édition, Vue détaillée).
    -   [x] Filtrage et recherche avancée.
    -   [x] Statistiques et tableaux de bord.

### Livrables
-   ✅ Module de gestion des formalités complet.
-   ✅ Calculateur de frais OHADA intégré.
-   ✅ Suivi des statuts et délais.

---

## Phase 5 : Comptabilité Notariale - ✅ TERMINÉ (100%)

### Objectif
Gestion du Compte Office et Compte Client avec double-entry bookkeeping.

### Tâches
1.  **Architecture Comptable**
    -   [x] Modèles `Compte`, `Ecriture`, `Mouvement` (existants, améliorés).
    -   [x] Modèles `Recu` et `Facture` avec auto-numérotation.
    -   [x] Séparation stricte Office/Clients (champ `categorie`).
    -   [x] Méthodes helper (get_solde, is_balanced, etc.).

2.  **Service Layer (Logique Métier)**
    -   [x] Service de gestion des comptes.
    -   [x] Initialisation plan comptable par défaut (11 comptes).
    -   [x] Création d'écritures avec validation double-entry.
    -   [x] Génération de reçus avec écritures automatiques.
    -   [x] Génération de factures.
    -   [x] Calcul de soldes et balances.
    -   [x] Grand Livre (General Ledger).
    -   [x] Balance Générale (Trial Balance).

3.  **Formulaires**
    -   [x] CompteForm, EcritureForm, RecuForm, FactureForm.
    -   [x] RecetteForm, DepenseForm (formulaires simplifiés).

4.  **Routes**
    -   [x] Dashboard avec vue d'ensemble financière.
    -   [x] CRUD Comptes (index, create).
    -   [x] CRUD Reçus (index, create, view).
    -   [x] CRUD Factures (index, create, view).
    -   [x] Rapports (Balance, Grand Livre).

5.  **Migration Base de Données**
    -   [x] Script SQL de migration.
    -   [x] Script Python d'application.
    -   [x] Initialisation des comptes par défaut.

6.  **Templates (Interface Utilisateur)**
    -   [x] `dashboard.html` - Tableau de bord financier.
    -   [x] `comptes/index.html` - Plan comptable.
    -   [x] `recus/index.html` - Liste des reçus.
    -   [x] `recus/form.html` - Formulaire reçu.
    -   [x] `recus/view.html` - Détail reçu (imprimable).
    -   [x] `reports/balance.html` - Balance générale.

7.  **Intégration**
    -   [x] Blueprint enregistré dans l'application.
    -   [x] Lien de navigation ajouté au menu principal.
    -   [x] Tests navigateur complets.

### Livrables
-   ✅ Backend comptable 100% fonctionnel.
-   ✅ Double-entry bookkeeping implémenté et testé.
-   ✅ Reçus et factures avec auto-numérotation.
-   ✅ Rapports financiers (Balance, Grand Livre).
-   ✅ Interface utilisateur complète et moderne.
-   ✅ Navigation intégrée au menu principal.
-   ✅ Tous les templates créés et testés.

### Tests Effectués
-   ✅ Migration base de données réussie.
-   ✅ 11 comptes par défaut créés.
-   ✅ Création de reçu (REC-000001) - 50,000 FCFA.
-   ✅ Création de facture (FACT-000001) - 100,000 FCFA.
-   ✅ Calcul de solde correct (50,000 FCFA).
-   ✅ Balance générale équilibrée (Débit = Crédit).
-   ✅ Grand livre avec 2 mouvements.
-   ✅ Validation double-entry bookkeeping.
-   ✅ Dashboard affiche correctement les statistiques.
-   ✅ Formulaire de reçu fonctionnel.
-   ✅ Plan comptable avec séparation Office/Client.
-   ✅ Balance générale avec totaux équilibrés.
-   ✅ Vue détaillée de reçu imprimable.

---

## Phase 6 : Tests & Qualité
233: 
234: ### Objectif
235: Stabilisation et fiabilisation.
236: 
237: ### Tâches
### Tâches
-   [x] Mise en place framework de test (Pytest, Fixtures).
-   [x] Tests unitaires (Pytest) - Models & Calculator.
-   [x] Tests d'intégration (Parcours utilisateur) - Clients, Dossiers, Actes, Formalites, Compta.
-   [x] Review UX/UI (Polissage Tailwind) - Dashboard, Navigation Pro, Flash Messages.

---

## Phase 7 : Déploiement

### Objectif
Passage en production.

### Tâches
-   [x] Configuration Gunicorn/Nginx (`deploy/` folder).
-   [x] Sécurisation (HTTPS, Headers) - via `deploy/README.md` & `config.py` (ProductionConfig).
-   [x] Backup S3/Local (`scripts/backup.py`).

## Conclusion
Le projet est prêt pour le déploiement en production. Suivre les instructions dans `deploy/README.md`.

---

## Calendrier Prévisionnel (Estimatif)

| Phase | Durée Est. |
|-------|------------|
| Phase 0 | 1-2 jours |
| Phase 1 | 3-4 jours |
| Phase 2 | 5-7 jours |
| Phase 3 | 5-7 jours |
| Phase 4 | 4-5 jours |
| Phase 5 | 7-10 jours |
| Total | ~30-40 jours |
