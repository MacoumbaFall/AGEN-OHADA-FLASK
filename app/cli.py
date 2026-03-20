import click
from flask.cli import with_appcontext
from app import db
from app.models import User

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(username, email, password):
    """Create an admin user."""
    if db.session.scalar(db.select(User).where(User.username == username)):
        print(f'User {username} already exists.')
        return
    
    user = User(username=username, email=email, role='ADMIN')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f'Admin user {username} created successfully.')


@click.command('seed-parametres')
@with_appcontext
def seed_parametres():
    """Initialise les param\u00e8tres de l'\u00e9tude avec les valeurs par d\u00e9faut."""
    from app.actes.services.parametres import ParametreService
    created = ParametreService.seed_defaults()
    if created:
        print(f'{created} param\u00e8tre(s) cr\u00e9\u00e9(s) avec succ\u00e8s.')
    else:
        print('Tous les param\u00e8tres sont d\u00e9j\u00e0 pr\u00e9sents en base. Aucun changement.')

@click.command('seed-profiles')
@with_appcontext
def seed_profiles():
    """Initialise les permissions et les profils prédéfinis."""
    from app.models import Profile, Permission
    
    # 1. Définir les permissions disponibles
    permissions_data = [
        # Administration
        {'code': 'ADMIN', 'nom': 'Accès administrateur total', 'description': 'Donne un accès complet au système, configuration, et gestion des utilisateurs.'},
        # Actes
        {'code': 'MANAGE_ACTES', 'nom': 'Gérer les actes', 'description': 'Créer, modifier, et gérer le cycle de vie des actes (sauf signature et répertoire).'},
        {'code': 'SIGNER_ACTES', 'nom': 'Signer les actes', 'description': 'Pouvoir de finaliser, signer électroniquement et générer l\'acte (Réservé au Notaire).'},
        {'code': 'MANEGE_REPERTOIRE', 'nom': 'Gérer le répertoire', 'description': 'Ajouter et consulter les actes dans le répertoire notarial.'},
        {'code': 'MANAGE_TEMPLATES', 'nom': 'Gérer les modèles d\'actes', 'description': 'Créer et modifier les modèles Word (.docx) et paramètres de modèles.'},
        # Dossiers & Clients
        {'code': 'MANAGE_DOSSIERS', 'nom': 'Gérer les dossiers', 'description': 'Créer, modifier et clôturer des dossiers.'},
        {'code': 'MANAGE_CLIENTS', 'nom': 'Gérer les clients', 'description': 'Créer et gérer les informations et KYC des clients.'},
        # Formalités
        {'code': 'MANAGE_FORMALITES', 'nom': 'Gérer les formalités', 'description': 'Suivi des formalités, de leur statut et paiement.'},
        # Comptabilité
        {'code': 'MANAGE_COMPTA', 'nom': 'Gérer la comptabilité', 'description': 'Ajouter des écritures comptables, factures, reçus et accéder aux rapports financiers.'},
        # Consultation
        {'code': 'VIEW_REPORTS', 'nom': 'Consulter les rapports', 'description': 'Accès en lecture aux analyses, rapports et statistiques du tableau de bord.'},
    ]

    # Insérer/Mettre à jour les permissions
    perms_map = {}
    for p_data in permissions_data:
        perm = db.session.scalar(db.select(Permission).where(Permission.code == p_data['code']))
        if not perm:
            perm = Permission(**p_data)
            db.session.add(perm)
        else:
            perm.nom = p_data['nom']
            perm.description = p_data['description']
        perms_map[p_data['code']] = perm
    
    db.session.commit()
    print("Permissions initialisées.")

    # 2. Définir les profils prédéfinis
    profiles_data = [
        {
            'code': 'ADMIN', 
            'nom': 'Administrateur', 
            'description': 'Accès total au système (DSI / Admin technique).',
            'permissions': ['ADMIN']
        },
        {
            'code': 'NOTAIRE', 
            'nom': 'Notaire', 
            'description': 'Officiers publics, gestion totale des actes, signature et comptabilité.',
            'permissions': ['MANAGE_ACTES', 'SIGNER_ACTES', 'MANEGE_REPERTOIRE', 'MANAGE_TEMPLATES', 'MANAGE_DOSSIERS', 'MANAGE_CLIENTS', 'MANAGE_FORMALITES', 'MANAGE_COMPTA', 'VIEW_REPORTS']
        },
        {
            'code': 'CLERC', 
            'nom': 'Clerc de Notaire', 
            'description': 'Préparation des actes, gestion des dossiers et contact client.',
            'permissions': ['MANAGE_ACTES', 'MANEGE_REPERTOIRE', 'MANAGE_DOSSIERS', 'MANAGE_CLIENTS', 'MANAGE_FORMALITES']
        },
        {
            'code': 'COMPTABLE', 
            'nom': 'Comptable', 
            'description': 'Gestion financière, facturation et reçus.',
            'permissions': ['MANAGE_COMPTA', 'VIEW_REPORTS', 'MANAGE_CLIENTS']
        },
        {
            'code': 'SECRETAIRE', 
            'nom': 'Secrétaire / Accueil', 
            'description': 'Saisie des clients, KYC et formalités basiques.',
            'permissions': ['MANAGE_CLIENTS', 'MANAGE_FORMALITES']
        }
    ]

    # Insérer/Mettre à jour les profils
    for prof_data in profiles_data:
        profile = db.session.scalar(db.select(Profile).where(Profile.code == prof_data['code']))
        
        # Trouver les objets permissions correspondants
        prof_perms = [perms_map[pcode] for pcode in prof_data['permissions'] if pcode in perms_map]
        
        if not profile:
            profile = Profile(
                code=prof_data['code'],
                nom=prof_data['nom'],
                description=prof_data['description'],
                is_predefined=True
            )
            profile.permissions = prof_perms
            db.session.add(profile)
        else:
            profile.nom = prof_data['nom']
            profile.description = prof_data['description']
            profile.is_predefined = True
            # Ne pas écraser les permissions si ce n'est pas nécessaire, ou on les remplace:
            profile.permissions = prof_perms
            
    db.session.commit()
    print("Profils prédéfinis initialisés avec succès.")



def register(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(seed_parametres)
    app.cli.add_command(seed_profiles)
