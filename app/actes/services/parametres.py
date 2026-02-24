"""
ParametreService — Service d'accès aux paramètres configurables de l'étude.

Stratégie de cache :
  - Les paramètres sont chargés depuis la DB une seule fois par process
    et mis en cache dans un dict Python (_cache).
  - Le cache est invalidé dès qu'un paramètre est modifié via `set()`.
  - Un fallback sur les valeurs par défaut (DEFAULTS) est toujours disponible
    si la DB n'est pas encore initialisée (premier démarrage).
"""

from decimal import Decimal
from typing import Any

# ---------------------------------------------------------------------------
# Valeurs par défaut — utilisées au premier démarrage (avant seed DB)
# et comme référence documentaire de tous les paramètres du système.
# ---------------------------------------------------------------------------
DEFAULTS: dict[str, dict] = {
    # ── FISCAL ──────────────────────────────────────────────────────────────
    'taux_tva': {
        'valeur': '0.18',
        'type_valeur': 'decimal',
        'groupe': 'FISCAL',
        'libelle': 'Taux TVA',
        'description': 'Taux de TVA applicable sur les honoraires notariaux (ex: 0.18 pour 18%)'
    },
    'taux_cf_proportionnel': {
        'valeur': '0.01',
        'type_valeur': 'decimal',
        'groupe': 'FISCAL',
        'libelle': 'Taux Conservation Foncière (proportionnel)',
        'description': 'Taux proportionnel de la taxe de Conservation Foncière (ex: 0.01 pour 1%)'
    },
    'frais_cf_fixe_standard': {
        'valeur': '6500',
        'type_valeur': 'decimal',
        'groupe': 'FISCAL',
        'libelle': 'Frais fixes CF (standard)',
        'description': 'Frais fixes de Conservation Foncière pour un titre standard'
    },
    'frais_cf_fixe_double': {
        'valeur': '14000',
        'type_valeur': 'decimal',
        'groupe': 'FISCAL',
        'libelle': 'Frais fixes CF (double — échange)',
        'description': 'Frais fixes de Conservation Foncière pour un acte d\'échange (2 titres)'
    },

    # ── DROITS DE MUTATION ──────────────────────────────────────────────────
    'seuil_mutation_moyen': {
        'valeur': '1500000',
        'type_valeur': 'decimal',
        'groupe': 'MUTATION',
        'libelle': 'Seuil mutation — tranche moyenne',
        'description': 'Seuil (en FCFA) au-delà duquel les droits de mutation passent au palier moyen'
    },
    'seuil_mutation_haut': {
        'valeur': '2500000',
        'type_valeur': 'decimal',
        'groupe': 'MUTATION',
        'libelle': 'Seuil mutation — tranche haute',
        'description': 'Seuil (en FCFA) au-delà duquel les droits de mutation passent au palier haut'
    },
    'frais_mutation_bas': {
        'valeur': '5000',
        'type_valeur': 'decimal',
        'groupe': 'MUTATION',
        'libelle': 'Droits de mutation — palier bas',
        'description': 'Montant fixe des droits de mutation pour les biens de faible valeur'
    },
    'frais_mutation_moyen': {
        'valeur': '10000',
        'type_valeur': 'decimal',
        'groupe': 'MUTATION',
        'libelle': 'Droits de mutation — palier moyen',
        'description': 'Montant fixe des droits de mutation pour les biens de valeur intermédiaire'
    },
    'frais_mutation_haut': {
        'valeur': '20000',
        'type_valeur': 'decimal',
        'groupe': 'MUTATION',
        'libelle': 'Droits de mutation — palier haut',
        'description': 'Montant fixe des droits de mutation pour les biens de valeur élevée'
    },

    # ── DÉBOURS ─────────────────────────────────────────────────────────────
    'frais_expeditions_base': {
        'valeur': '50000',
        'type_valeur': 'decimal',
        'groupe': 'DEBOURS',
        'libelle': 'Frais d\'expéditions (base)',
        'description': 'Frais d\'expéditions standard par acte'
    },
    'frais_publicite_base': {
        'valeur': '55000',
        'type_valeur': 'decimal',
        'groupe': 'DEBOURS',
        'libelle': 'Frais de publicité légale (base)',
        'description': 'Frais de publicité légale pour une modification de société standard'
    },
    'frais_divers_base': {
        'valeur': '50000',
        'type_valeur': 'decimal',
        'groupe': 'DEBOURS',
        'libelle': 'Frais divers (base)',
        'description': 'Frais divers standard inclus dans les débours'
    },
    'frais_morcellement': {
        'valeur': '22500',
        'type_valeur': 'decimal',
        'groupe': 'DEBOURS',
        'libelle': 'Frais de morcellement (par parcelle)',
        'description': 'Frais de géomètre/cadastre par parcelle lors d\'un morcellement'
    },

    # ── FACTURATION ─────────────────────────────────────────────────────────
    'facture_mention_legale': {
        'valeur': 'TVA applicable selon la réglementation OHADA. En cas de retard de paiement, une pénalité sera appliquée.',
        'type_valeur': 'string',
        'groupe': 'FACTURATION',
        'libelle': 'Mentions légales des factures',
        'description': 'Texte apparaissant en bas de toutes les factures générées'
    },
    'facture_coordonnees_bancaires': {
        'valeur': 'Banque: XXX, RIB: XXX, IBAN: XXX',
        'type_valeur': 'string',
        'groupe': 'FACTURATION',
        'libelle': 'Coordonnées bancaires',
        'description': 'Informations pour les virements bancaires'
    },
    'facture_delai_paiement_jours': {
        'valeur': '30',
        'type_valeur': 'int',
        'groupe': 'FACTURATION',
        'libelle': 'Délai de paiement (jours)',
        'description': 'Nombre de jours par défaut avant échéance de la facture'
    },

    # ── BARÈMES HONORAIRES (SEUILS) ─────────────────────────────────────────
    'seuil_bareme_tranche1': {
        'valeur': '20000000',
        'type_valeur': 'decimal',
        'groupe': 'BAREMES',
        'libelle': 'Seuil 1 — Honoraires Notariaux',
        'description': 'Limite de la tranche 1 (ex: de 0 à 20 Millions)'
    },
    'seuil_bareme_tranche2': {
        'valeur': '60000000',
        'type_valeur': 'decimal',
        'groupe': 'BAREMES',
        'libelle': 'Seuil 2 — Honoraires Notariaux',
        'description': 'Taille de la tranche 2 (ex: de 20 à 80 Millions)'
    },
    'seuil_bareme_tranche3': {
        'valeur': '220000000',
        'type_valeur': 'decimal',
        'groupe': 'BAREMES',
        'libelle': 'Seuil 3 — Honoraires Notariaux',
        'description': 'Taille de la tranche 3 (ex: de 80 à 300 Millions)'
    },

    # ── IDENTITÉ DE L'ÉTUDE ─────────────────────────────────────────────────
    'etude_nom': {
        'valeur': 'Étude Notariale',
        'type_valeur': 'string',
        'groupe': 'ETUDE',
        'libelle': 'Nom de l\'étude',
        'description': 'Nom officiel de l\'étude notariale (apparaît sur les documents générés)'
    },
    'etude_notaire': {
        'valeur': 'Maître ...',
        'type_valeur': 'string',
        'groupe': 'ETUDE',
        'libelle': 'Nom du Notaire',
        'description': 'Nom complet du notaire titulaire'
    },
    'etude_adresse': {
        'valeur': '',
        'type_valeur': 'string',
        'groupe': 'ETUDE',
        'libelle': 'Adresse de l\'étude',
        'description': 'Adresse postale complète'
    },
    'etude_telephone': {
        'valeur': '',
        'type_valeur': 'string',
        'groupe': 'ETUDE',
        'libelle': 'Téléphone de l\'étude',
        'description': 'Numéro de téléphone principal'
    },
    'etude_email': {
        'valeur': '',
        'type_valeur': 'string',
        'groupe': 'ETUDE',
        'libelle': 'E-mail de l\'étude',
        'description': 'Adresse e-mail de contact'
    },
}


class ParametreService:
    """
    Accès centralisé aux paramètres de l'étude avec cache in-process.

    Usage :
        from app.actes.services.parametres import ParametreService
        tva = ParametreService.get_decimal('taux_tva')  # → Decimal('0.18')
        nom = ParametreService.get_str('etude_nom')     # → 'Étude Dupont'

    Reset du cache (après modification) :
        ParametreService.invalidate_cache()
    """

    _cache: dict[str, Any] = {}
    _loaded: bool = False

    @classmethod
    def _load(cls) -> None:
        """Charge tous les paramètres depuis la DB dans le cache."""
        try:
            from app import db
            from app.models import ParametreEtude
            rows = db.session.execute(db.select(ParametreEtude)).scalars().all()
            cls._cache = {row.cle: row.valeur_typee for row in rows}
            cls._loaded = True
        except Exception:
            # DB non disponible (premier démarrage, tests) → fallback sur DEFAULTS
            cls._cache = {}
            cls._loaded = False

    @classmethod
    def invalidate_cache(cls) -> None:
        """Force le rechargement depuis la DB au prochain accès."""
        cls._cache = {}
        cls._loaded = False

    @classmethod
    def get(cls, cle: str, defaut: Any = None) -> Any:
        """
        Retourne la valeur typée d'un paramètre.
        Priorité : Cache DB → DEFAULTS → defaut fourni.
        """
        if not cls._loaded:
            cls._load()

        if cle in cls._cache:
            return cls._cache[cle]

        # Fallback : valeur par défaut dans le code
        if cle in DEFAULTS:
            raw = DEFAULTS[cle]
            type_v = raw.get('type_valeur', 'string')
            val = raw['valeur']
            if type_v == 'decimal':
                return Decimal(val)
            elif type_v == 'int':
                return int(val)
            elif type_v == 'bool':
                return val.lower() in ('true', '1', 'oui')
            return val

        return defaut

    @classmethod
    def get_decimal(cls, cle: str, defaut: Decimal = Decimal('0')) -> Decimal:
        """Raccourci typé pour les valeurs décimales (taux, montants)."""
        val = cls.get(cle, defaut)
        return Decimal(str(val)) if not isinstance(val, Decimal) else val

    @classmethod
    def get_int(cls, cle: str, defaut: int = 0) -> int:
        return int(cls.get(cle, defaut))

    @classmethod
    def get_str(cls, cle: str, defaut: str = '') -> str:
        return str(cls.get(cle, defaut))

    @classmethod
    def set(cls, cle: str, valeur: str, user_id: int = None) -> None:
        """
        Met à jour un paramètre en DB et invalide le cache.
        Crée le paramètre s'il n'existe pas encore.
        """
        from app import db
        from app.models import ParametreEtude
        from datetime import datetime

        param = db.session.scalar(db.select(ParametreEtude).where(ParametreEtude.cle == cle))
        if param:
            param.valeur = str(valeur)
            param.updated_by = user_id
            param.updated_at = datetime.utcnow()
        else:
            meta = DEFAULTS.get(cle, {})
            param = ParametreEtude(
                cle=cle,
                valeur=str(valeur),
                type_valeur=meta.get('type_valeur', 'string'),
                groupe=meta.get('groupe', 'FISCAL'),
                libelle=meta.get('libelle', cle),
                description=meta.get('description'),
                updated_by=user_id,
            )
            db.session.add(param)

        db.session.commit()
        cls.invalidate_cache()

    @classmethod
    def seed_defaults(cls) -> int:
        """
        Initialise la DB avec toutes les valeurs par défaut si elles n'existent pas.
        Appelé au setup initial de l'étude. Retourne le nombre de paramètres créés.
        """
        from app import db
        from app.models import ParametreEtude

        created = 0
        for cle, meta in DEFAULTS.items():
            existing = db.session.scalar(db.select(ParametreEtude).where(ParametreEtude.cle == cle))
            if not existing:
                param = ParametreEtude(
                    cle=cle,
                    valeur=meta['valeur'],
                    type_valeur=meta.get('type_valeur', 'string'),
                    groupe=meta.get('groupe', 'FISCAL'),
                    libelle=meta.get('libelle', cle),
                    description=meta.get('description'),
                )
                db.session.add(param)
                created += 1

        if created:
            db.session.commit()
            cls.invalidate_cache()

        return created
