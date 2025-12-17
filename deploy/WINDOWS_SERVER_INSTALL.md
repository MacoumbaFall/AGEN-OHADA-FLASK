# Guide d'Installation Serveur Windows (On-Premises) - AGEN-OHADA

Ce guide détaille les étapes pour installer AGEN-OHADA sur un serveur Windows (Windows Server 2019/2022 ou Windows 10/11 Pro).

## Prérequis

Assurez-vous d'avoir les droits administrateur sur la machine.

1.  **Python 3.10+** : [Télécharger ici](https://www.python.org/downloads/windows/).
    *   *Important* : Cochez "Add Python to PATH" lors de l'installation.
2.  **PostgreSQL** : [Télécharger ici](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
    *   Notez le mot de passe du superutilisateur `postgres` défini lors de l'installation.
3.  **Git** : [Télécharger ici](https://git-scm.com/download/win).
4.  **Visual C++ Redistributable** : Souvent nécessaire pour certaines librairies Python.

---

## 1. Installation de l'Application

Ouvrez PowerShell en tant qu'administrateur et naviguez vers le dossier d'installation souhaité (ex: `C:\inetpub` ou `C:\Apps`).

```powershell
# Création du dossier
New-Item -ItemType Directory -Force -Path "C:\Apps"
cd C:\Apps

# Cloner le dépôt
git clone https://github.com/votre-user/AGEN-OHADA-flask.git
cd AGEN-OHADA-flask

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances + Waitress (Serveur Web pour Windows)
pip install -r requirements.txt
pip install waitress
```

### Alternative : Installation Offline (Sans Internet)

Si le serveur n'a pas accès à Internet :

1.  **Sur un PC connecté** :
    *   Téléchargez le projet en ZIP (depuis GitHub > Code > Download ZIP).
    *   Téléchargez les librairies Python :
        ```bash
        mkdir packages
        pip download -r requirements.txt -d packages
        pip download waitress -d packages
        ```
2.  **Sur le Serveur** :
    *   Copiez le dossier `AGEN-OHADA-flask` et le dossier `packages` via clé USB.
    *   Créez l'environnement virtuel (comme étape ci-dessus).
    *   Installez depuis le dossier local :
        ```bash
        pip install --no-index --find-links=packages -r requirements.txt
        pip install --no-index --find-links=packages waitress
        ```

---

## 2. Configuration de la Base de Données

Ouvrez **pgAdmin** (installé avec PostgreSQL) ou utilisez la ligne de commande psql.

1.  Créez la base de données `agen_ohada`.
2.  Créez un utilisateur dédié.

**Via ligne de commande (PowerShell) :**
```powershell
# Adaptez le chemin vers psql si nécessaire, souvent : "C:\Program Files\PostgreSQL\15\bin\psql.exe"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

Dans l'invite SQL :
```sql
CREATE DATABASE agen_ohada;
CREATE USER agen_ohada_user WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE agen_ohada TO agen_ohada_user;
\q
```

---

## 3. Configuration de l'Application

Créez le fichier `.env` à la racine `C:\Apps\AGEN-OHADA-flask\.env`.

```ini
FLASK_APP=deploy/waitress_server.py
FLASK_ENV=production
# Générez une clé aléatoire
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire
# Lien de connexion DB
DATABASE_URL=postgresql+psycopg://agen_ohada_user:votre_mot_de_passe_securise@localhost:5432/agen_ohada
```

Initialisez la base de données :

```powershell
# Assurez-vous que venv est activé
$env:FLASK_APP = "app"
flask db upgrade
python init_db.py
```

---

## 4. Test Rapide

Lancez le serveur manuellement pour tester :

```powershell
python deploy/waitress_server.py
```

Ouvrez votre navigateur sur `http://localhost:8080`. Si l'application s'affiche, tout fonctionne. Arrêtez le serveur avec `Ctrl+C`.

---

## 5. Installation en tant que Service Windows (Lancement Automatique)

Pour que l'application tourne en arrière-plan et redémarre avec le serveur, nous utiliserons **NSSM** (Non-Sucking Service Manager).

1.  Téléchargez NSSM : [nssm.cc/download](https://nssm.cc/download).
2.  Extrayez `nssm.exe` (version win64) dans `C:\Apps\nssm\`.
3.  Ajoutez `C:\Apps\nssm\` au PATH système (optionnel mais pratique).

Installez le service :

```powershell
cd C:\Apps\nssm
.\nssm.exe install AGEN-OHADA
```

Une fenêtre s'ouvre. Configurez les onglets :

**Application**
*   **Path**: `C:\Apps\AGEN-OHADA-flask\venv\Scripts\python.exe`
*   **Startup directory**: `C:\Apps\AGEN-OHADA-flask`
*   **Arguments**: `deploy/waitress_server.py`

**Environment** (Optionnel si tout est dans .env, mais recommandé)
*   Ajoutez les variables d'environnement si nécessaire.

**I/O**
*   **Output (stdout)**: `C:\Apps\AGEN-OHADA-flask\logs\service_output.log`
*   **Error (stderr)**: `C:\Apps\AGEN-OHADA-flask\logs\service_error.log`
*(Créez le dossier `logs` avant)*

Cliquez sur **Install service**.

Démarrez le service :
```powershell
Start-Service AGEN-OHADA
```

L'application est maintenant accessible sur le port 8080 et démarrera automatiquement avec Windows.

---

## 6. (Optionnel) Accès Réseau et Pare-feu

Si vous souhaitez accéder à l'application depuis d'autres PC du réseau :

1.  Ouvrez le **Pare-feu Windows Defender avec fonctions avancées de sécurité**.
2.  Règles de trafic entrant > Nouvelle règle.
3.  Type : Port.
4.  TCP / Ports locaux spécifiques : `8080`.
5.  Autoriser la connexion.
6.  Nom : `AGEN-OHADA Web`.

L'application sera accessible via `http://IP-DU-SERVEUR:8080` (ex: `http://192.168.1.50:8080`).

---

## 7. Sauvegardes

Créez une tâche planifiée Windows pour exécuter le script de backup.

1.  Ouvrez le **Planificateur de tâches**.
2.  Créer une tâche de base > "Backup AGEN OHADA".
3.  Déclencheur : Tous les jours à 23h00.
4.  Action : Démarrer un programme.
    *   Program/script : `C:\Apps\AGEN-OHADA-flask\venv\Scripts\python.exe`
    *   Arguments : `scripts/backup.py`
    *   Start in : `C:\Apps\AGEN-OHADA-flask`
