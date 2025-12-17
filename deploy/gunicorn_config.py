import multiprocessing
import os

# Bind to the PORT environment variable (required by Render)
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120

# Logging
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"

# Process naming
proc_name = "agen-ohada"
