from app import create_app
from app.config import ProductionConfig
import os

# Logger initialization could go here
app = create_app(ProductionConfig)
application = app

if __name__ == "__main__":
    print("Running application directly...")
    application.run()
