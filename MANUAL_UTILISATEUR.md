# Manuel Utilisateur - AGEN-OHADA

Bienvenue dans le guide d'utilisation de **AGEN-OHADA**, votre solution complète de gestion d'étude notariale.

---

## 🧭 Navigation de l'Application

L'interface de l'application a été repensée pour être accessible sur ordinateur et sur mobile. Les fonctionnalités sont réparties en deux menus principaux : **Gestion** et **Administration**.

### 💼 Menu "Gestion"
Ce menu centralise toutes les opérations métier quotidiennes de l'étude :
*   **Accueil** : Le tableau de bord avec vos statistiques et accès rapides.
*   **Clients** : Base de données de vos contacts (KYC, informations légales, pièces d'identité).
*   **Dossiers** : Centralisation des affaires (parties prenantes, statut d'avancement).
*   **Formalités** : Suivi post-signature et calculateur de frais OHADA.
*   **Actes** (Sous-menu) :
    *   *Gérer les types d'actes* : Création et paramétrage des actes possibles.
    *   *Gérer les modèles d'acte* : Envoi de modèles Word (.docx) avec publipostage ou éditeur Markdown.
    *   *Signer les actes* : Validation et signature cryptographique par le Notaire.
    *   *Répertoire Notarial* : Registre officiel des actes.
*   **Comptabilité** : Suivi des encaissements (reçus), facturations, comptes clients et caisse de l'office.
*   **Archives** : Accès aux dossiers clôturés en lecture seule.

### ⚙️ Menu "Administration" (Administrateurs uniquement)
*   **Utilisateurs** : Création des comptes clercs/notaires et gestion des permissions.
*   **Paramètres** : Configuration globale de l'étude (nom, adresse, logo, etc.).

---

## 1. Tableau de Bord
Le point d'entrée de votre application affiche les indicateurs clés en temps réel :
*   Le nombre total de clients et de dossiers actifs.
*   Les formalités en cours.
*   Les raccourcis pour créer rapidement un client ou une formalité.

---

## 2. Gestion des Clients (KYC)
La base commune pour toute l'étude :
*   **Création** : Enregistrez une personne physique ou morale.
*   **KYC (Know Your Customer)** : Suivez l'état du dossier client (pièces manquantes, profession, nationalité).
*   **Liaison** : Un client peut être rattaché à plusieurs dossiers en tant qu'acheteur, vendeur, etc.

---

## 3. Gestion des Dossiers
Le cœur de métier. Un dossier regroupe :
*   Les informations de base (titre, type, date d'ouverture).
*   **Les Parties** : Ajoutez des clients existants et assignez-leur un rôle (Vendeur, Créancier, etc.).
*   Tous les documents et formalités rattachés se font depuis ce point central.

---

## 4. Rédaction et Signature des Actes
Le processus de gestion d'un acte suit un flux de travail rigoureux garantissant la sécurité juridique des documents.

### 🔄 Cycle de vie de l'acte
1.  **Brouillon (Draft)** : L'acte est généré par le clerc ou le notaire. Il peut être modifié librement via l'éditeur ou en remplaçant le fichier Word.
2.  **Finalisation** : Le Notaire vérifie l'acte et le "Finalise". Cette action verrouille le document : il ne peut plus être modifié, garantissant que la version signée sera identique à la version révisée.
3.  **Signature (Électronique)** : Le Notaire appose sa validation numérique finale. L'acte passe au statut "SIGNÉ" et devient immuable.

### 🖊️ Les deux modes de signature
L'application AGEN-OHADA gère la dualité entre la validation numérique et le support papier officiel.

#### A. Signature Électronique (Sécurité Numérique)
Elle est effectuée par le Notaire dans le menu "Signer les actes" ou directement depuis la vue d'un acte finalisé :
*   **Intégrité** : Le système calcule une empreinte numérique unique (Hash SHA-256) basée sur le contenu de l'acte. Si le contenu changeait, la signature deviendrait invalide.
*   **Authentification** : Un jeton de signature infalsifiable est stocké, incluant le nom d'utilisateur du notaire et l'horodatage précis.
*   **Reconnaissance** : Un acte signé est identifiable par son badge **vert "SIGNE"**. Toutes les fonctions d'édition sont alors désactivées.

#### B. Signature Manuelle (Support Physique)
Pour la formalisation physique avec les clients :
*   **Page de Signatures** : Cliquez sur le bouton "Page Signatures" pour générer une page optimisée pour l'impression.
*   **Formalisme** : Cette page liste automatiquement tous les intervenants (Vendeur, Acheteur, Bailleur, etc.) avec des zones dédiées pour :
    *   Les signatures manuscrites des parties.
    *   Le sceau et la signature physique du Notaire.
*   **Archivage** : Une fois signée physiquement, cette page est jointe à l'original (la minute) pour l'archivage définitif.

---

## 5. Suivi des Formalités
Évitez les retards et pénalités :
*   **Calculateur OHADA** : Estimez les frais d'enregistrement sur la base des barèmes en vigueur.
*   **Suivi chronologique** : Enregistrez la date de dépôt, la date prévue de retour et suivez le statut avec les différentes administrations (Domaines, Impôts, RCCM).

---

## 6. Comptabilité
Gérez la vie financière de l'étude sans logiciel tiers tiers :
*   **Double Caisse** : Suivi distinct des honoraires de l'étude et des fonds détenus pour le compte des clients (frais de mutation, dépôts).
*   **Reçus et Factures** : Édition et impression de pièces comptables normées.
*   **Rapports** : Visualisez l'état des comptes à tout instant.

---

## 7. Archivage et Répertoire
Une fois un dossier totalement traité :
*   **Clôture** : Le dossier passe dans la section "Archives". Les données ne peuvent plus être modifiées par erreur.
*   **Répertoire Annuel** : Chaque acte signé se voit attribuer un numéro de répertoire de façon séquentielle par année. La liste complète est consultable et exportable par les administrateurs.

---

## 💡 Astuce : Variables Dynamiques (.docx)
Dans vos modèles Word, utilisez ces codes exacts pour injecter automatiquement les données du dossier :

| Catégorie | Tag / Balise | Ce qui sera écrit |
|-----------|----------|-------------|
| **Dossier** | `{{ dossier.numero_dossier }}` | Numéro (ex: DOS-2026-001) |
| | `{{ dossier.intitule }}` | Objet de l'affaire |
| | `{{ dossier.date_ouverture }}` | Date d'ouverture |
| **Client ** | `{{ client.nom }}` | Nom de famille / Raison sociale |
| | `{{ client.prenom }}` | Prénom du client |
| | `{{ client.adresse }}` | Adresse complète |

*Note: Vous pouvez utiliser des rôles spécifiques selon les parties de votre dossier (ex: `{{ vendeur.nom }}`, `{{ acheteur.prenom }}`).*

---

Besoin d'aide technique supplémentaire ? 
Contactez l'administrateur système de votre étude.
