---
description: Automated testing of Phase 3 (Template Management)
---

1. Start the Flask Application
// turbo
Run the Flask server in the background (if not already running):
`python run.py`

2. Open Browser and Login
- Open Browser to `http://127.0.0.1:5000/auth/login`
- Login with `admin` / `admin`

3. Navigate to Templates
- Click "Modèles" in the top navigation.
- Verify you are at `/actes/templates`.

4. Create New Template
- Click "Nouveau Modèle".
- Fill Form:
    - Nom: "Contrat de Vente Test"
    - Type: "Vente" (Select 'Vente Immobilière')
    - Description: "Test template for phase 3."
    - Contenu: "<h1>Vente</h1><p>Vendeur: {{ vendeur }}</p>"
- Click "Enregistrer".

5. Verify List
- Verify "Contrat de Vente Test" is in the table.

6. Edit Template
- Click "Modifier".
- Change Nom to "Contrat de Vente Test UPDATED".
- Click "Enregistrer".
- Verify the name is updated in the list.

7. Cleanup
- Click "Supprimer" for the template.
- Confirm.
- Verify list is empty (or template is gone).
