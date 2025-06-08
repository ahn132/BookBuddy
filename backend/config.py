import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Pinecone configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "pcsk_CTqKQ_UeKv5mthuiwVvEBnQo5ma64qoLgZ81TYeJwwrbBPZbwRXaMDkU3GyQrraUWvAnw")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")  # Default to free tier
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "bookbuddy")

# Other configuration variables can be added here 