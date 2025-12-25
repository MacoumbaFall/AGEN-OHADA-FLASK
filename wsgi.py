from app import create_app
from app.config import ProductionConfig
import os

print("--- Starting Application in Production Mode ---")
print(f"DATABASE_URL is set: {bool(os.environ.get('DATABASE_URL'))}")

app = create_app(ProductionConfig)
application = app

if __name__ == "__main__":
    print("Running application directly...")
    application.run()
