# Manuel de Tests - AGEN-OHADA

Ce document détaille les procédures de test pour vérifier le bon fonctionnement de l'application **AGEN-OHADA**. Il couvre les tests automatisés et les tests manuels.

## 1. Tests Automatisés (Backend)

L'application utilise `pytest` pour les tests unitaires et fonctionnels.

### Prérequis
- Python installé
- Dépendances installées : `pip install -r requirements.txt`
- Base de données de test configurée (par défaut en mémoire pour les tests unitaires)

### Exécution des tests
Pour lancer l'intégralité des tests :
```powershell
pytest
```

Pour lancer les tests par module :
```powershell
pytest tests/functional/test_auth.py
pytest tests/functional/test_clients.py
pytest tests/functional/test_dossiers.py
pytest tests/functional/test_actes.py
pytest tests/functional/test_comptabilite.py
pytest tests/functional/test_formalites.py
```

---

## 2. Tests Manuels (Interface Utilisateur)

### 2.1 Authentification
1.  **Connexion** : Se connecter avec l'utilisateur `admin` / `admin123`.
2.  **Déconnexion** : Cliquer sur "Se déconnecter" et vérifier le retour à la page de login.
3.  **Accès refusé** : Tenter d'accéder à `/comptabilite` avec un compte n'ayant pas le rôle `COMPTABLE` ou `NOTAIRE`.

### 2.2 Gestion des Clients
1.  **Création** : Créer un client Morgan (Physique) et un client Société X (Morale).
2.  **Validation** : Vérifier que les champs obligatoires bloquent l'enregistrement s'ils sont vides.
3.  **Recherche** : Tenter une recherche par nom dans la liste des clients.

### 2.3 Gestion des Dossiers
1.  **Ouverture** : Créer un dossier avec un intitulé "Vente villa".
2.  **Attribution** : Associer un client comme "Vendeur" et un autre comme "Acheteur".
3.  **Statut** : Passer le dossier de "OUVERT" à "EN COURS".

### 2.4 Rédaction d'Actes & Modèles
1.  **Modèle** : Créer un nouveau modèle (ex: "Acte de Vente").
2.  **Synchronisation (Critique)** : Vérifier qu'en cliquant sur "Enregistrer", le texte saisi dans l'éditeur EasyMDE est bien sauvegardé (pas de message d'erreur).
3.  **Génération** : Dans un dossier, générer l'acte à partir du modèle.
4.  **PDF** : Télécharger l'acte généré en PDF et vérifier le contenu.

### 2.5 Comptabilité
1.  **Reçu** : Émettre un reçu pour un client dans un dossier.
2.  **Écriture** : Vérifier dans le "Grand Livre" que l'écriture correspondante a été générée (Débit Banque / Crédit Compte Client).
3.  **Facture** : Créer une facture d'honoraires et vérifier le calcul automatique de la TVA (si applicable).

### 2.6 Formalités
1.  **Ajout** : Ajouter une formalité "Enregistrement" dans un dossier.
2.  **Statut** : Marquer la formalité comme "Dépôt effectué" et vérifier la date de dépôt.

---

## 3. Rapport d'Anomalie
Si un test échoue, veuillez noter :
- L'URL de la page.
- Les étapes pour reproduire le bug.
- Le message d'erreur (Flash message en haut de page ou log dans le terminal).
- La capture d'écran si possible.
