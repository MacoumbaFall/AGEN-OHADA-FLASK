---
description: Automated testing of Phase 2 (Clients & Dossiers) using the integrated browser
---

1. Start the Flask Application
// turbo
Run the Flask server in the background (if not already running):
`python run.py`

2. Open Browser and Login
- Open Browser to `http://127.0.0.1:5000/auth/login`
- Login with `admin` / `admin` (or create if needed, but it should exist from Phase 0)

3. Test Clients Module
- Navigate to "Clients"
- Click "Ajouter un client"
- Create a "Personne Physique":
    - Nom: "TestNom"
    - Prénom: "TestPrenom"
    - Email: "test@example.com"
- Submit
- Verify the client appears in the list or detail view.

4. Test Dossiers Module
- Navigate to "Dossiers"
- Click "Nouveau Dossier"
- details:
    - Numéro: "DOS-TEST-001"
    - Intitulé: "Vente Maison Test"
    - Type: "Vente"
- Submit
- Verify redirection to Dossier Detail.

5. Test Association (Phase 2 completion)
- On the Dossier Detail page, look for "Ajouter une partie".
- Select "TestNom TestPrenom" from the dropdown.
- Role: "Vendeur"
- Click "Ajouter".
- Verify the party is listed in "Parties".

6. Clean up (Optional)
- Delete the dossier.
- Delete the client.
