---
description: Automated testing of the Full Phase 3 Flow (Create, Generate, Save, PDF) in browser
---

1. Start the Flask Application
// turbo
Run the Flask server in the background (if not already running):
`python run.py`

2. Open Browser and Login
- Open Browser to `http://127.0.0.1:5000/auth/login`
- Login with `admin` / `admin`

3. Generate and Save Act
- Go to `/actes/generate`.
- Select Dossier: "DOS-GEN-01" (assumed from previous test).
- Select Template: "TemplateGenTest".
- Click "Prévisualiser l'Acte".
- Wait for preview (Wait 2s).
- **Click "Valider et Sauvegarder"** (The new button).

4. Verify Saved Act View
- Verify redirection to Act Detail page (`/actes/view/<id>`).
- Check if content (e.g., "ACTE", "Vendeur:") is visible.

5. Test PDF Download
- Click "Télécharger PDF".
- This will likely trigger a download. In a headless/automated browser, this might just check the link or status code.
- Since we can't easily valid download via screenshot, capturing the button existence is enough for now, or check for "PDF" text.

6. Conclusion
- Capture final screenshot of the Act View page.
