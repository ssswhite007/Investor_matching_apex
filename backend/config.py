import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 26214400))  # 25MB default
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Airtable configuration
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', 'appZCSJhvllkpX1gV')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'Fund')
    
    @staticmethod
    def init_app(app):
        # Create upload directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
