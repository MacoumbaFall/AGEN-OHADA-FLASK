import json
from datetime import date, datetime
from decimal import Decimal
from flask import request, has_request_context
from flask_login import current_user
from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from app.models import SecurityLog

def serialize_val(val):
    if val is None:
        return None
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (int, float, str, bool)):
        return val
    return str(val)

def register_audit_events(db):
    """
    Register SQLAlchemy event listeners to automatically track INSERT, UPDATE, DELETE.
    Will log modified fields and standard audit info directly into the SecurityLog table.
    """
    
    @event.listens_for(db.session, 'before_flush')
    def receive_before_flush(session, flush_context, instances):
        if not has_request_context():
            return
            
        # Get context info
        username = getattr(current_user, 'username', 'SYSTEM') if getattr(current_user, 'is_authenticated', False) else 'SYSTEM'
        ip = getattr(request, 'remote_addr', None)
        ua = getattr(request, 'user_agent', None)
        uastring = ua.string if ua else None

        logs = []
        
        # Process INSERTS (new objects)
        for obj in list(session.new):
            if isinstance(obj, SecurityLog): continue
            
            # Ensure the object has a __table__ mapped
            if not hasattr(obj, '__table__'): continue
            
            table_name = obj.__table__.name
            if table_name in ('security_logs', 'profile_permissions'): continue
            
            changes = {}
            for c in obj.__table__.columns:
                if c.key == 'password_hash': continue
                val = getattr(obj, c.key, None)
                if val is not None:
                    changes[c.key] = [None, serialize_val(val)]
                    
            if changes:
                # Primary key is often not set before flush for auto-increment IDs
                pk_val = getattr(obj, 'id', None) 
                # if not present, we get None
                
                log = SecurityLog(
                    event_type='CREATE',
                    username=username,
                    ip_address=ip,
                    user_agent=uastring,
                    target_resource=table_name,
                    target_id=str(pk_val) if pk_val else None,
                    details=f"Création d'un enregistrement dans {table_name}",
                    changes=changes
                )
                logs.append(log)

        # Process UPDATES (dirty objects)
        for obj in list(session.dirty):
            if isinstance(obj, SecurityLog): continue
            if not hasattr(obj, '__table__'): continue
            
            table_name = obj.__table__.name
            if table_name in ('security_logs', 'profile_permissions'): continue
            
            changes = {}
            for c in obj.__table__.columns:
                if c.key in ('password_hash', 'updated_at'): continue
                
                try:
                    hist = get_history(obj, c.key)
                    if hist.has_changes():
                        old = hist.deleted[0] if hist.deleted else None
                        new = hist.added[0] if hist.added else None
                        
                        s_old = serialize_val(old)
                        s_new = serialize_val(new)
                        
                        # Only log if it really changed
                        if s_old != s_new:
                            changes[c.key] = [s_old, s_new]
                except Exception:
                    pass
                    
            if changes:
                # Primary key is known for dirty objects
                pk_val = getattr(obj, 'id', getattr(obj, 'code', ''))
                
                log = SecurityLog(
                    event_type='UPDATE',
                    username=username,
                    ip_address=ip,
                    user_agent=uastring,
                    target_resource=table_name,
                    target_id=str(pk_val) if pk_val else None,
                    details=f"Modification d'un enregistrement dans {table_name}",
                    changes=changes
                )
                logs.append(log)

        # Process DELETES
        for obj in list(session.deleted):
            if isinstance(obj, SecurityLog): continue
            if not hasattr(obj, '__table__'): continue
            
            table_name = obj.__table__.name
            if table_name in ('security_logs', 'profile_permissions'): continue
            
            pk_val = getattr(obj, 'id', getattr(obj, 'code', ''))
            
            log = SecurityLog(
                event_type='DELETE',
                username=username,
                ip_address=ip,
                user_agent=uastring,
                target_resource=table_name,
                target_id=str(pk_val) if pk_val else None,
                details=f"Suppression d'un enregistrement dans {table_name}"
            )
            logs.append(log)

        if logs:
            session.add_all(logs)

