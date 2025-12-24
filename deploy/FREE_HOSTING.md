# Hébergement Gratuit - Guide pour Render.com

Pour héberger AGEN-OHADA gratuitement sur le cloud, nous recommandons **Render.com**. C'est une plateforme robuste qui supporte nativement Python et PostgreSQL.

> **Note** : Les offres gratuites ont des limitations (mise en veille après inactivité, limites de base de données). C'est idéal pour la démonstration ou le développement, mais pour une vraie étude notariale, un hébergement payant (VPS ou Render Pro) est conseillé (~7$/mois).

## Prérequis

1.  Avoir le code sur un dépôt **GitHub** (public ou privé).
2.  Créer un compte sur [dashboard.render.com](https://dashboard.render.com/).

## Étape 1 : Préparation du Projet

Assurez-vous que les fichiers suivants existent à la racine du projet (déjà créés par l'assistant) :
*   `requirements.txt`
*   `wsgi.py`

## Étape 2 : Configuration sur Render

### 1. Créer la Base de Données (PostgreSQL)
1.  Dans le dashboard Render, cliquez sur **New +** > **PostgreSQL**.
2.  **Name**: `dir
`.
3.  **Database**: `agen_ohada`.
4.  **User**: `kobe` (ou autre).
5.  **Region**: Choisissez `Frankfurt` (Europe) pour la rapidité.
6.  **Instance Type**: Free.
7.  Cliquez sur **Create Database**.
8.  *Important* : Une fois créée, copiez l'**Internal Database URL** (pour usage interne) ou l'**External Database URL** (si vous voulez vous y connecter depuis votre PC).

### 2. Créer le Service Web
1.  Cliquez sur **New +** > **Web Service**.
2.  Connectez votre dépôt GitHub.
3.  **Name**: `agen-ohada-app`.
4.  **Region**: `Frankfurt` (Même que la DB).
5.  **Branch**: `main` (ou master).
6.  **Runtime**: `Python 3`.
7.  **Build Command**: `pip install -r requirements.txt`.
8.  **Start Command**: `gunicorn wsgi:application`.
9.  **Instance Type**: Free.

### 3. Variables d'Environnement
Dans la section **Environment Variables** (avant de cliquer sur Deploy) :

| Clé | Valeur |
|-----|--------|
| `python --version` | `3.10.0` (ou votre version) |
| `SECRET_KEY` | (Générez une longue chaîne aléatoire) |
| `DATABASE_URL` | (Collez l'**Internal Database URL** copié à l'étape 1) |
| `FLASK_APP` | `wsgi.py` |
| `FLASK_ENV` | `production` |

Cliquez sur **Create Web Service**.

## Étape 3 : Initialisation

Render va déployer l'application. Au premier démarrage, il faut créer les tables.

1.  Allez dans l'onglet **Shell** de votre Web Service sur Render.
2.  Exécutez :
    ```bash
    flask db upgrade
    python init_db.py
    ```

C'est fini ! Votre application est accessible via l'URL fournie par Render (ex: `https://agen-ohada-app.onrender.com`).

---

## Limitations de l'offre Gratuite
*   **Cold Start** : Le site mettra ~50 secondes à démarrer si personne ne l'a visité depuis 15 minutes.
*   **Base de données** : Expire après 90 jours (nécessite une mise à jour ou un passage au plan payant).
