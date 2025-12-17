# Guide de Déploiement - AGEN-OHADA

Ce guide détaille les étapes pour déployer l'application AGEN-OHADA sur un serveur Linux (Ubuntu 22.04 recommandé).

## 1. Prérequis Serveur

Mettez à jour le système et installez les dépendances :

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx git -y
```

## 2. Configuration Base de Données

Créez l'utilisateur et la base de données PostgreSQL :

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE agen_ohada;
CREATE USER agen_ohada_user WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE agen_ohada TO agen_ohada_user;
\q
```

## 3. Installation de l'Application

Clonez le repository et installez les dépendances :

```bash
# Clone
git clone https://github.com/votre-user/AGEN-OHADA-flask.git /var/www/agen-ohada
cd /var/www/agen-ohada

# Venv
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt
pip install gunicorn
```

## 4. Configuration Environnement

Créez le fichier `.env` de production :

```bash
cp .env.example .env
nano .env
```

Contenu recommandé :
```ini
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire
DATABASE_URL=postgresql+psycopg://agen_ohada_user:votre_mot_de_passe_securise@localhost:5432/agen_ohada
```

## 5. Initialisation

Appliquez les migrations et créez le premier utilisateur :

```bash
flask db upgrade
python init_db.py # Ou script personnalisé pour créer l'admin
```

## 6. Configuration Gunicorn & Nginx

### Systemd Service (Gunicorn)

Créez `/etc/systemd/system/agen-ohada.service` :

```ini
[Unit]
Description=Gunicorn instance directly serving AGEN-OHADA
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/agen-ohada
Environment="PATH=/var/www/agen-ohada/venv/bin"
ExecStart=/var/www/agen-ohada/venv/bin/gunicorn --config deploy/gunicorn_config.py wsgi:application

[Install]
WantedBy=multi-user.target
```

Activez le service :
```bash
sudo systemctl start agen-ohada
sudo systemctl enable agen-ohada
```

### Nginx

Copiez la configuration et activez-la :

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/agen-ohada
sudo ln -s /etc/nginx/sites-available/agen-ohada /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Sécurisation HTTPS (Certbot)

Installez Certbot et configurez le SSL :

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

Certbot modifiera automatiquement la configuration Nginx pour rediriger HTTP vers HTTPS.

## 8. Maintenance

### Backup
Un script de backup est disponible dans `scripts/backup.py`. Configurez un cronjob pour l'exécuter quotidiennement.

```bash
0 3 * * * /var/www/agen-ohada/venv/bin/python /var/www/agen-ohada/scripts/backup.py
```

### Mises à jour
```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart agen-ohada
```
