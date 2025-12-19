from app import create_app, db
from app.models import Template

app = create_app()

def add_example_template():
    with app.app_context():
        # Check if it already exists
        existing = db.session.execute(db.select(Template).filter_by(nom="Acte de Vente Immobilière (Exemple)")).scalar_one_or_none()
        if existing:
            print("Template already exists.")
            return

        contenu = """<style>
    @page {
        size: A4;
        margin: 2.5cm;
    }
    body {
        font-family: 'Times New Roman', serif;
        line-height: 1.6;
        color: #1a1a1a;
    }
    .header {
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 2px solid #000;
        padding-bottom: 10px;
    }
    .title {
        text-align: center;
        text-decoration: underline;
        font-weight: bold;
        font-size: 18pt;
        margin-bottom: 40px;
    }
    .mention {
        font-style: italic;
        font-size: 10pt;
        margin-bottom: 20px;
    }
    .section-title {
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 25px;
        margin-bottom: 10px;
        text-decoration: underline;
    }
    p {
        text-align: justify;
        margin-bottom: 15px;
    }
    .signature-block {
        margin-top: 50px;
        display: flex;
        justify-content: space-between;
    }
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-size: 8pt;
        color: #666;
    }
</style>

<div class="header">
    <strong>RÉPUBLIQUE DU CAMEROUN</strong><br>
    <em>Paix - Travail - Patrie</em><br>
    <br>
    <strong>ÉTUDE DE MAÎTRE NOTAIRE</strong><br>
    BP 1234, Douala<br>
    Tél: +237 670 00 00 00
</div>

<div class="title">ACTE DE VENTE IMMOBILIÈRE</div>

<p class="mention">Dossier N° {{ dossier.numero_dossier }} - Référence: {{ dossier.intitule }}</p>

<p>L'AN DEUX MILLE VINGT-CINQ,<br>
Le {{ date }},</p>

<p>PAR-DEVANT <strong>Maître NOTAIRE</strong>, Notaire à la résidence de DOUALA, soussigné,</p>

<div class="section-title">ONT COMPARU :</div>

<p><strong>1°/ M/Mme {{ vendeur.nom }} {{ vendeur.prenom }}</strong>, né(e) le ..., demeurant à {{ vendeur.adresse }}, titulaire de la CNI n° ..., agissant en qualité de <strong>VENDEUR</strong> d'une part,</p>

<p><strong>2°/ M/Mme {{ acheteur.nom }} {{ acheteur.prenom }}</strong>, né(e) le ..., demeurant à {{ acheteur.adresse }}, titulaire de la CNI n° ..., agissant en qualité de <strong>ACQUÉREUR</strong> d'autre part,</p>

<div class="section-title">OBJET DE LA VENTE</div>

<p>Le VENDEUR vend par les présentes, en s'obligeant à toutes les garanties ordinaires et de droit en pareille matière, à l'ACQUÉREUR qui accepte, l'immeuble situé à ..., consistant en ..., d'une superficie de ...</p>

<div class="section-title">PRIX DE VENTE</div>

<p>La présente vente est consentie et acceptée moyennant le prix principal de <strong>[MONTANT EN CHIFFRES]</strong> Francs CFA.</p>

<div class="section-title">DONT ACTE</div>

<p>Fait et passé à DOUALA, en l'Étude de Maître Notaire, les jour, mois et an ci-dessus.</p>
<p>Et après lecture faite, les parties ont signé avec le Notaire.</p>

<div class="signature-block">
    <div style="float: left; width: 45%;">
        <strong>Le VENDEUR</strong><br><br><br>
        _________________
    </div>
    <div style="float: right; width: 45%; text-align: right;">
        <strong>L'ACQUÉREUR</strong><br><br><br>
        _________________
    </div>
    <div style="clear: both;"></div>
</div>

<div style="margin-top: 40px; text-align: center;">
    <strong>Le NOTAIRE</strong><br><br><br>
    (Sceau et Signature)
</div>

<div class="footer">
    Document généré via AGEN-OHADA - Page 1/1
</div>"""

        template = Template(
            nom="Acte de Vente Immobilière (Exemple)",
            type_acte="VENTE",
            description="Exemple complet illustrant l'injection de variables (Vendeur, Acheteur) et le formatage CSS pour PDF.",
            contenu=contenu
        )
        db.session.add(template)
        db.session.commit()
        print("Template 'Acte de Vente Immobilière (Exemple)' created successfully.")

if __name__ == "__main__":
    add_example_template()
