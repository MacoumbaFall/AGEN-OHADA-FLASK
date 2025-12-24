# Manuel Utilisateur - AGEN-OHADA

Bienvenue dans le guide d'utilisation de **AGEN-OHADA**, votre solution de gestion d'étude notariale.

## Table des Matières
1. [Accès et Connexion](#1-accès-et-connexion)
2. [Tableau de Bord](#2-tableau-de-bord)
3. [Gestion des Clients](#3-gestion-des-clients)
4. [Gestion des Dossiers](#4-gestion-des-dossiers)
5. [Rédaction d'Actes](#5-rédaction-dactes)
6. [Suivi des Formalités](#6-suivi-des-formalités)
7. [Comptabilité](#7-comptabilité)

---

## 1. Accès et Connexion

Pour accéder à l'application, ouvrez votre navigateur web et rendez-vous sur l'adresse fournie par votre administrateur (ex: `http://localhost:5000` ou `https://notaire.votre-domaine.com`).

*   **Identifiant** : Votre nom d'utilisateur (ex: `admin`).
*   **Mot de passe** : Votre mot de passe sécurisé.

> En cas d'oubli de mot de passe, contactez l'administrateur système.

---

## 2. Tableau de Bord

Une fois connecté, vous arrivez sur le **Tableau de Bord**. C'est votre centre de commande.
*   **Indicateurs clés** : Visualisez en un coup d'œil le nombre de dossiers actifs, les formalités en attente, et les soldes de trésorerie.
*   **Actions Rapides** : Des boutons vous permettent de créer instantanément un *Nouveau Dossier*, un *Nouveau Client* ou une *Nouvelle Formalité*.
*   **Menu Latéral / Navigation** : Utilisez la barre de navigation (en haut ou sur le côté mobile) pour accéder aux différents modules.

---

## 3. Gestion des Clients

Ce module vous permet de gérer votre carnet d'adresses.
*   **Liste des clients** : Recherche rapide par nom, téléphone ou email.
*   **Nouveau Client** : Cliquez sur "Nouveau Client". Vous pouvez choisir entre :
    *   **Personne Physique** : Nom, Prénom, Date de naissance, etc.
    *   **Personne Morale** : Raison sociale, Forme juridique, RCCM, etc.
*   **Fiche Client** : Consultez l'historique complet d'un client (dossiers associés, factures, coordonnées).

---

## 4. Gestion des Dossiers

Le cœur de votre activité. Un dossier regroupe tous les éléments d'une affaire (Clients, Actes, Formalités, Factures).
*   **Créer un Dossier** : Donnez un nom au dossier et sélectionnez un type (ex: Vente Immobilière). Le numéro de dossier est généré automatiquement (ex: `DOS-2025-001`).
*   **Ajouter des Parties** : Dans l'onglet "Parties", associez des clients existants au dossier en leur attribuant un rôle (Vendeur, Acheteur, etc.).
*   **Suivi** : Changez le statut du dossier (Ouvert, En Cours, En Attente, Clôturé) pour suivre son avancement.

---

## 5. Rédaction d'Actes

Générez vos documents juridiques automatiquement à partir de modèles prédéfinis.

*   **Modèles (Templates)** : Accédez à la bibliothèque via le menu "Modèles". Vous pouvez créer vos propres documents en utilisant :
    *   **Markdown** pour le formatage (gras, listes, tableaux).
    *   **Jinja2** pour les variables dynamiques (ex: `{{ client.nom }}`).
*   **Éditeur Intelligent** : L'éditeur intègre une aide sur le côté droit. Cliquez sur une variable (ex: "Nom du Client") pour l'insérer à l'endroit du curseur.
*   **Enregistrement** : Le bouton "Enregistrer" synchronise automatiquement votre saisie. En cas d'erreur de saisie ou de base de données, un message d'alerte rouge s'affichera pour vous guider.
*   **Générer un Acte** :
    1.  Utilisez le bouton **"Générer un Acte"** dans la barre de navigation ou via un Dossier.
    2.  Sélectionnez le Dossier concerné et le Modèle à utiliser.
    3.  Cliquez sur **"Prévisualiser"** pour voir le résultat avec les données réelles.
    4.  Si tout est correct, cliquez sur **"Valider et Sauvegarder"**.
*   **Téléchargement** : Une fois l'acte sauvegardé, vous pouvez le télécharger au format **PDF** prêt pour l'impression.

---

## 6. Suivi des Formalités

Ne ratez plus aucune échéance administrative.
*   **Enregistrer une Formalité** : Pour chaque dossier, notez les démarches à effectuer (Enregistrement, Cadastre, Journal Officiel).
*   **Calculateur de Frais** : L'outil estime automatiquement les coûts basés sur les barèmes OHADA (bientôt disponible pour tous les types).
*   **Suivi des Statuts** : Marquez les formalités comme "Dépôt effectué", "Retourné", ou "Terminé".
*   **Alertes** : Les formalités en retard apparaissent en évidence sur votre tableau de bord.

---

## 7. Comptabilité

Gestion financière rigoureuse séparant les fonds de l'office et les fonds des clients.
*   **Plan Comptable** : Liste des comptes (Banque, Caisse, Clients, Honoraires...). Distinction stricte entre "Compte Office" et "Compte Client".
*   **Reçus** : Émettez un reçu pour tout encaissement. L'écriture comptable est générée automatiquement.
*   **Factures** : Créez des factures d'honoraires et de frais.
*   **Rapports** :
    *   **Balance Générale** : État des débits et crédits par compte.
    *   **Grand Livre** : Historique détaillé de toutes les opérations.
    *   **Journal** : Liste chronologique des écritures.

---

## Besoin d'aide technique ?
Pour toute question technique, bug ou demande d'amélioration, veuillez contacter le support technique ou consulter le guide de déploiement pour les administrateurs.
