import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# IPFS configuration
IPFS_API_URL = os.getenv("IPFS_API_URL", "https://ipfs.infura.io:5001")
IPFS_GATEWAY_URL = os.getenv("IPFS_GATEWAY_URL", "https://ipfs.io/ipfs/")

# Blockchain configuration
WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI", "https://mainnet.infura.io/v3/your-infura-key")
STORY_PROTOCOL_ADDRESS = os.getenv("STORY_PROTOCOL_ADDRESS", "0x1234567890123456789012345678901234567890")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1"))

# AI configuration
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))  # 75% similarity threshold
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.8"))

# Application settings
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# DAO/Dispute settings
ARBITRATION_PERIOD_DAYS = int(os.getenv("ARBITRATION_PERIOD_DAYS", "7"))
DAO_VOTING_THRESHOLD = float(os.getenv("DAO_VOTING_THRESHOLD", "0.66"))  # 66% majority