---
description: Test automatisé de la gestion des dossiers et parties (Phase 3)
---
// turbo-all

1. **Vérification Serveur**
   - Assurez-vous que le serveur Flask tourne sur le port 5000.
   - Commande : `python run.py` (ou `flask run`)

2. **Test Navigateur (Scénario)**
   - Login (admin/admin ou user existant).
   - Navigation vers `/dossiers`.
   - Création d'un dossier "Dossier Test Turbo".
   - Ajout d'une partie (Client) à ce dossier.
   - Vérification visuelle.
   - Suppression de la partie.
