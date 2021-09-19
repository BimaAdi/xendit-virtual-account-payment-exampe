from dotenv import load_dotenv
load_dotenv()
import os

DATABASE_CONNECTION = os.environ.get('DATABASE_CONNECTION', None)
XENDIT_API = os.environ.get('XENDIT_API', None)
