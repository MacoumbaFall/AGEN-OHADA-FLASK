from app import create_app
from app.config import ProductionConfig

application = create_app(ProductionConfig)

if __name__ == "__main__":
    application.run()
