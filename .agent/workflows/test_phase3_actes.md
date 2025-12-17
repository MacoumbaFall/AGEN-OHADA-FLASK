---
description: Automated testing of the Act creation (Phase 3) via browser
---

1. Start the Flask Application
// turbo
Run the Flask server in the background (if not already running):
`python run.py`

2. Open Browser and Login
- Open Browser to `http://127.0.0.1:5000/auth/login`
- Login with `admin` / `admin`

3. Ensure Prerequisites
- Create a Client "Client Acte Test" (if needed).
- Create a Dossier "DOS-ACTE-001" (if needed).
- Add "Client Acte Test" to "DOS-ACTE-001" as "Vendeur".
- Create a Template "Test Acte Vente":
    - Contenu: "<h1>ACTE DE VENTE</h1><p>Entre le Vendeur <strong>{{ vendeur.nom }} {{ vendeur.prenom }}</strong> et l'Acheteur...</p>"

4. Navigate to Generation Page
- Go to "Modèles".
- Click "Générer un Acte" (or go to `/actes/generate`).

5. Generate Act
- Select Dossier: "DOS-ACTE-001".
- Select Modèle: "Test Acte Vente".
- Click "Prévisualiser l'Acte".

6. Verify Preview
- Check if the preview shows: "Entre le Vendeur Client Acte Test" (with the name substituted).
