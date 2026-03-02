# Documentation Technique - AGEN-OHADA-FLASK
**Version : 1.1.0-stable** | **Dernière mise à jour : 02/03/2026**

---

## 🏗️ 1. Architecture du Système

L'application est construite sur une architecture **Flask Modulaire (Blueprints)** suivant le pattern "Factory".

- **Backend** : Python 3.12+ / Flask 3.x
- **Base de Données** : PostgreSQL (Production/Cloud) ou SQLite (Développement/Standalone) via SQLAlchemy 2.x
- **Migration** : Alembic (via Flask-Migrate) pour le versioning du schéma.
- **Frontend** : Templates Jinja2 enrichis avec TailwindCSS (via CDN ou build local).
- **Génération Document** : 
    - PDF : `xhtml2pdf` et `xhtml2pdf` (HTML vers PDF).
    - Word : `docxtpl` (Substitution de variables dans `.docx`).

### Structure des dossiers
```bash
/app
  /actes         # Module rédaction et barèmes (Logic métier complexe)
  /auth          # Authentification et Sécurité
  /clients       # Base de données Clients
  /comptabilite  # Moteur comptable OHADA (Double entrée)
  /dossiers      # Gestion des dossiers (Module central)
  /formalites    # Suivi administratif
  /models.py     # Définition des tables (SQLAlchemy)
  /static        # Fichiers statiques et archives générées
/scripts         # Utilitaires de maintenance et audit
/tests           # Suite de tests unitaires et fonctionnels
```

---

## 🚀 2. Modes de Déploiement

### A. Mode Standalone (Poste de travail local)
Idéal pour un usage individuel ou hors-ligne (ex: Ordinateur portable du Notaire).

1. **Prérequis** : Python 3.12 installé sur Windows/Mac.
2. **Installation** :
   ```powershell
   git clone [repository_url]
   cd AGEN-OHADA-FLASK
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configuration** : Modifier `.env` pour utiliser SQLite :
   ```env
   DATABASE_URL=sqlite:///instance/app.db
   ```
4. **Lancement Rapide** (via Waitress pour Windows) :
   ```powershell
   python run.py
   ```

### B. Mode Serveur Réseau Local (Windows Server)
Recommandé pour une utilisation multi-utilisateurs au sein de l'étude sur un réseau local (LAN).

1. **Prérequis Serveur** :
   - Installation de **PostgreSQL for Windows** (recommandé pour la gestion multi-utilisateurs simultanés).
   - Installation de **Python 3.12**.

2. **Configuration Réseau & Sécurité** :
   - Créer une règle dans le **Pare-feu Windows** (Firewall) pour autoriser le port TCP choisi (ex: 8000).
   - Configurer le fichier `.env` avec l'IP fixe du serveur :
     ```env
     DATABASE_URL=postgresql://user:password@localhost/agen_ohada
     ```

3. **Déploiement en tant que Service Windows (NSSM)** :
   Pour que l'application démarre automatiquement avec le serveur :
   - Télécharger **NSSM** (Non-Sucking Service Manager).
   - Installer le service :
     ```powershell
     nssm install AGEN_OHADA "C:\Chemin\Vers\venv\Scripts\python.exe" "C:\Chemin\Vers\run.py"
     ```
   - L'application sera accessible via `http://[IP_SERVEUR]:8000` depuis tous les postes de l'étude.

### C. Mode Serveur Cloud (Déploiement Koyeb/Heroku)
Mode recommandé pour un accès distant sécurisé.

1. **Infrastructure** :
   - Service App : Koyeb / Heroku / DigitalOcean (Docker ou Git-push).
   - Service DB : Neon.tech (PostgreSQL Serverless).
2. **Variables d'environnement critiques** :
   - `SECRET_KEY` : Hash unique pour sécuriser les sessions.
   - `DATABASE_URL` : URL de connexion PostgreSQL.
   - `FLASK_ENV` : `production`.
3. **Persistance des fichiers** :
   > [!IMPORTANT]
   > Sur les plateformes Cloud (Koyeb/Heroku), le système de fichiers est éphémère. Il est **crucial** de configurer un stockage externe (AWS S3 ou Cloudinary) pour les documents archivés si le volume devient important, ou utiliser des volumes persistants Koyeb.

### D. Packaging pour Installation Client (PyInstaller)
Pour livrer l'application sous forme d'un exécutable `.exe` sans installer Python sur le poste client.

1. **Procédure** :
   ```powershell
   pip install pyinstaller
   pyinstaller --onefile --add-data "app/templates;app/templates" --add-data "app/static;app/static" run.py
   ```
2. **Livrable** : Un dossier `dist/` contenant l'exécutable autonome.

---

## 🛠️ 3. Recommandations de Maintenance

### 🧹 Audit des données (Crucial)
Il est fortement recommandé d'exécuter périodiquement le script d'audit pour vérifier l'équilibre comptable.
```powershell
$env:PYTHONPATH='.'; python scripts/audit_integrity.py
```

### 💾 Procédure de Sauvegarde (Backup)
1. **Base de Données** :
   - Cloud : Activer les "Point-in-time recovery" sur Neon.
   - Local : Copier le fichier `.db` ou faire un `pg_dump`.
2. **Fichiers Actes** :
   - Sauvegarder le répertoire `app/static/archives/` et `app/static/generated_actes/`. Ce sont les originaux numériques.

### 🔄 Mises à jour du Schéma
En cas de modification des modèles Python, pour mettre à jour la base de données client :
```powershell
flask db migrate -m "Description du changement"
flask db upgrade
```

---

## 🔒 4. Sécurité & Robustesse

- **Verrouillage de Compte** : Désigne un mécanisme automatique qui bloque un utilisateur après 5 tentatives. Seul un Admin peut déverrouiller via `Users > Unlock`.
- **Logs de Sécurité** : Consultables dans le menu "Administration > Logs de sécurité". Indispensable pour l'audit en cas de litige financier.
- **Rate Limiting** : Protège les formulaires critiques contre les attaques par force brute (5 tentatives/min max).

---

## 📖 5. Support Technique

En cas d'erreur `500 Internal Server Error`, vérifier les logs :
- **Koyeb** : `koyeb service logs [service-name]`
- **Local** : Consulter la console Python où tourne `run.py`.

---
*Documentation générée par Antigravity pour l'Étude Notariale.*
