from datetime import datetime
from pathlib import Path
import shutil
import os
from sqlalchemy import func, select, extract
from flask import current_app
from app import db
from app.models import Dossier, Acte

class ArchiveService:
    @staticmethod
    def archive_dossier(dossier_id: int, user_id: int):
        """
        Archive completely a dossier and its signed acts.
        Returns a summary dict or raises Exception.
        """
        dossier = db.session.get(Dossier, dossier_id)
        if not dossier:
            raise ValueError("Dossier introuvable")
            
        if dossier.statut == 'ARCHIVE':
            raise ValueError("Dossier déjà archivé")

        # Validation Logic
        drafts = [a for a in dossier.actes if a.statut == 'BROUILLON']
        if drafts:
            raise ValueError(f"Archivage impossible : il reste {len(drafts)} acte(s) en brouillon.")

        signed_acts = [a for a in dossier.actes if a.statut == 'SIGNE']
        if not signed_acts:
            raise ValueError("Aucun acte signé à archiver dans ce dossier.")

        # Prepare Archive Vault
        archive_root = Path(current_app.static_folder) / 'archives'
        if not archive_root.exists():
            archive_root.mkdir(parents=True, exist_ok=True)
            
        dossier_archive_path = archive_root / str(dossier.id)
        dossier_archive_path.mkdir(parents=True, exist_ok=True)

        # Repertoire Numbering Strategy
        # Get max reagent number for current year
        year = datetime.utcnow().year
        max_rep = db.session.scalar(
            select(func.max(Acte.numero_repertoire)).filter(
                extract('year', Acte.date_archivage) == year
            )
        ) or 0

        archived_count = 0
        
        try:
            for acte in signed_acts:
                # 1. Move File
                filename = f"acte_{acte.id}.docx"
                src_path = Path(current_app.static_folder) / 'generated_actes' / filename
                dest_path = dossier_archive_path / filename

                if src_path.exists():
                    shutil.move(str(src_path), str(dest_path))
                
                # We could also look for PDF if implemented later
                
                # 2. Assign Repertoire Number
                max_rep += 1
                acte.numero_repertoire = max_rep
                acte.date_archivage = datetime.utcnow()
                acte.archive_par_id = user_id
                acte.statut = 'ARCHIVE'
                
                archived_count += 1

            # 3. Close Dossier
            dossier.statut = 'ARCHIVE'
            db.session.commit()
            
            return {
                "success": True,
                "archived_count": archived_count,
                "start_repertoire": max_rep - archived_count + 1,
                "end_repertoire": max_rep
            }
            
        except Exception as e:
            db.session.rollback()
            # If partial file moves occurred, manual cleanup might be needed 
            # (In a real production system we'd use a transactional file system or object storage)
            raise e
