import os
from dotenv import load_dotenv
from app import create_app

# Carregar variáveis de ambiente do arquivo .env se existir
load_dotenv()

config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
