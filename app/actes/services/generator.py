from datetime import datetime
from io import BytesIO
import os
import shutil
from pathlib import Path
from docxtpl import DocxTemplate
from jinja2 import Template as JinjaTemplate
import markdown2
from flask import current_app, url_for
from app import db
from app.models import Acte

class ActGeneratorService:
    @staticmethod
    def generate_act(dossier, template, context, save_mode=False, user=None):
        """
        Generates an Act document (DOCX or HTML) from a template.
        
        Args:
            dossier: Dossier model instance
            template: Template model instance
            context: Dictionary of context variables
            save_mode: Boolean, if True saves as Draft Acte in DB
            user: Current user (required if save_mode is True)
            
        Returns:
            dict: {
                'type': 'docx' | 'html',
                'content': BytesIO (docx) | str (html),
                'acte_id': int (if saved),
                'preview_url': str (if docx preview),
                'download_url': str (if saved)
            }
        """
        result = {'type': 'unknown'}

        if template.is_docx:
            result['type'] = 'docx'
            # Resolve path
            template_path = os.path.join(current_app.static_folder, 'templates_docx', template.file_path)
            
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template file '{template.file_path}' not found")

            # Render DOCX
            doc = DocxTemplate(template_path)
            doc.render(context)
            
            output = BytesIO()
            doc.save(output)
            output.seek(0)
            result['content'] = output

            if save_mode:
                # Create Acte Record
                acte = Acte(
                    dossier_id=dossier.id,
                    type_acte=template.type_acte.nom,
                    type_acte_id=template.type_acte_id,
                    statut='BROUILLON',
                    version=1
                    # cree_par_id=user.id if user else None # If model supports it
                )
                db.session.add(acte)
                db.session.commit()
                
                # Save physical file
                gen_filename = f"acte_{acte.id}.docx"
                gen_folder = os.path.join(current_app.root_path, 'static', 'generated_actes')
                os.makedirs(gen_folder, exist_ok=True)
                
                with open(os.path.join(gen_folder, gen_filename), 'wb') as f:
                    f.write(output.getvalue())
                
                result['acte_id'] = acte.id
                result['download_url'] = url_for('actes.download_docx', id=acte.id)
                
            else:
                # Preview Mode (Temp File)
                temp_folder = os.path.join(current_app.root_path, 'static', 'temp_previews')
                os.makedirs(temp_folder, exist_ok=True)
                
                # Cleanup (Optimistic)
                ActGeneratorService._cleanup_temp_files(temp_folder)
                
                ts_str = datetime.utcnow().strftime('%H%M%S')
                uid = user.id if user else 'guest'
                temp_filename = f"preview_{uid}_{ts_str}.docx"
                
                with open(os.path.join(temp_folder, temp_filename), 'wb') as f:
                    f.write(output.getvalue())
                    
                result['preview_url'] = url_for('static', filename=f'temp_previews/{temp_filename}')

        else:
            # Markdown/HTML Logic
            result['type'] = 'html'
            jinja_template = JinjaTemplate(template.contenu)
            rendered_markdown = jinja_template.render(context)
            html_content = markdown2.markdown(rendered_markdown, extras=["tables", "fenced-code-blocks"])
            result['content'] = html_content
            
            if save_mode:
                acte = Acte(
                    dossier_id=dossier.id,
                    type_acte=template.type_acte.nom,
                    type_acte_id=template.type_acte_id,
                    contenu_html=html_content,
                    statut='BROUILLON',
                    version=1
                )
                db.session.add(acte)
                db.session.commit()
                result['acte_id'] = acte.id
                
        return result

    @staticmethod
    def _cleanup_temp_files(folder_path, age_seconds=3600):
        """Removes files older than age_seconds"""
        import time
        try:
            now_ts = time.time()
            for f in os.listdir(folder_path):
                f_path = os.path.join(folder_path, f)
                if os.path.isfile(f_path) and os.stat(f_path).st_mtime < now_ts - age_seconds:
                    os.remove(f_path)
        except Exception:
            pass  # Non-critical background task
