from waitress import serve
from app import create_app
from app.config import ProductionConfig
import os

# Create the application with production config
application = create_app(ProductionConfig)

if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting Waitress server on http://{host}:{port}")
    serve(application, host=host, port=port, threads=8)
