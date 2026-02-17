import os
from pathlib import Path
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth

# Cargar variables de entorno desde .env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuración de Google OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/auth/google/callback')

# Verificar que las credenciales estén configuradas
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("\n⚠️  ADVERTENCIA: Las credenciales de Google OAuth no están configuradas.")
    print("   Por favor, edita el archivo .env con tus credenciales de Google.")
    print("   Consulta GOOGLE_OAUTH_SETUP.md para más información.\n")

# Inicializar OAuth
oauth = OAuth()

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
