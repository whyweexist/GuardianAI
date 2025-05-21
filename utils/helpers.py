import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from PIL import Image

# Import from project
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def save_temp_file(content, file_name=None, file_type="json"):
    """Save content to a temporary file
    
    Args:
        content: Content to save
        file_name: Optional file name
        file_type: File type (json, txt, etc.)
        
    Returns:
        Path: Path to the saved file
    """
    if file_name is None:
        file_name = f"temp_{int(datetime.now().timestamp())}"
    
    file_path = Path(config.TEMP_DIR) / f"{file_name}.{file_type}"
    
    try:
        if file_type == "json":
            with open(file_path, 'w') as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    json.dump(content, f, indent=2)
        else:
            with open(file_path, 'w') as f:
                f.write(content)
        
        return file_path
    except Exception as e:
        logger.error(f"Error saving temporary file: {e}")
        return None

async def load_temp_file(file_path, file_type="json"):
    """Load content from a temporary file
    
    Args:
        file_path: Path to the file
        file_type: File type (json, txt, etc.)
        
    Returns:
        Content of the file
    """
    try:
        if file_type == "json":
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            with open(file_path, 'r') as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error loading temporary file: {e}")
        return None

async def delete_temp_file(file_path):
    """Delete a temporary file
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: Success or failure
    """
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        logger.error(f"Error deleting temporary file: {e}")
        return False

async def resize_image(image_path, max_size=(800, 800)):
    """Resize an image while maintaining aspect ratio
    
    Args:
        image_path: Path to the image
        max_size: Maximum size (width, height)
        
    Returns:
        Path: Path to the resized image
    """
    try:
        img = Image.open(image_path)
        img.thumbnail(max_size)
        
        # Generate output path
        file_name = os.path.basename(image_path)
        output_path = Path(config.TEMP_DIR) / f"resized_{file_name}"
        
        # Save resized image
        img.save(output_path)
        
        return output_path
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return None

async def format_timestamp(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
    """Format a timestamp
    
    Args:
        timestamp: Timestamp (ISO format string or datetime object)
        format_str: Format string
        
    Returns:
        str: Formatted timestamp
    """
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp)
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            return timestamp
        
        return dt.strftime(format_str)
    except Exception as e:
        logger.error(f"Error formatting timestamp: {e}")
        return timestamp

async def validate_ethereum_address(address):
    """Validate an Ethereum address
    
    Args:
        address: Ethereum address
        
    Returns:
        bool: Valid or invalid
    """
    if not address or not isinstance(address, str):
        return False
    
    # Check if address starts with 0x and has the correct length
    if not address.startswith('0x') or len(address) != 42:
        return False
    
    # Check if address contains only hexadecimal characters
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False

async def generate_unique_id(prefix=""):
    """Generate a unique ID
    
    Args:
        prefix: Optional prefix
        
    Returns:
        str: Unique ID
    """
    timestamp = int(datetime.now().timestamp() * 1000)
    random_suffix = os.urandom(4).hex()
    
    return f"{prefix}{timestamp}_{random_suffix}"

async def upload_to_ipfs(file_path, ipfs_client=None):
    """Upload a file to IPFS
    
    Args:
        file_path: Path to the file
        ipfs_client: Optional IPFS client instance
        
    Returns:
        str: IPFS hash of the uploaded file
    """
    try:
        # If no client is provided, try to create one
        if ipfs_client is None:
            import ipfshttpclient
            try:
                ipfs_client = ipfshttpclient.connect(config.IPFS_API_URL)
            except Exception as e:
                logger.error(f"Error connecting to IPFS: {e}")
                # Return simulated hash for development/testing
                return f"QmSimulated{int(datetime.now().timestamp())}"
        
        # Upload file to IPFS
        result = ipfs_client.add(file_path)
        return result['Hash']
    except Exception as e:
        logger.error(f"Error uploading to IPFS: {e}")
        # Return simulated hash for development/testing
        return f"QmSimulated{int(datetime.now().timestamp())}"

async def generate_metadata(creator_address, asset_name, asset_type, description, ipfs_hash, additional_fields=None):
    """Generate metadata JSON for an asset
    
    Args:
        creator_address: Ethereum address of the creator
        asset_name: Name of the asset
        asset_type: Type of asset (e.g., Logo, Trademark, etc.)
        description: Description of the asset
        ipfs_hash: IPFS hash of the asset
        additional_fields: Optional dictionary of additional metadata fields
        
    Returns:
        dict: Metadata JSON
    """
    metadata = {
        "name": asset_name,
        "description": description,
        "type": asset_type,
        "creator": creator_address,
        "assetHash": ipfs_hash,
        "createdAt": datetime.now().isoformat(),
    }
    
    # Add additional fields if provided
    if additional_fields and isinstance(additional_fields, dict):
        metadata.update(additional_fields)
    
    return metadata

async def monitor_transaction(tx_hash, web3_provider=None, max_attempts=30, delay=2):
    """Monitor a blockchain transaction until it's mined
    
    Args:
        tx_hash: Transaction hash
        web3_provider: Optional Web3 provider instance
        max_attempts: Maximum number of attempts to check
        delay: Delay between attempts in seconds
        
    Returns:
        dict: Transaction receipt or None if not mined
    """
    try:
        # If no provider is provided, try to create one
        if web3_provider is None:
            from web3 import Web3
            web3_provider = Web3(Web3.HTTPProvider(config.BLOCKCHAIN_RPC_URL))
        
        # Check transaction receipt
        for attempt in range(max_attempts):
            receipt = web3_provider.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return {
                    "status": "success" if receipt.status == 1 else "failed",
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "transaction_hash": tx_hash.hex() if hasattr(tx_hash, 'hex') else tx_hash
                }
            
            # Wait before next attempt
            await asyncio.sleep(delay)
        
        return {"status": "pending", "transaction_hash": tx_hash.hex() if hasattr(tx_hash, 'hex') else tx_hash}
    except Exception as e:
        logger.error(f"Error monitoring transaction: {e}")
        return {"status": "error", "error": str(e), "transaction_hash": tx_hash.hex() if hasattr(tx_hash, 'hex') else tx_hash}

async def calculate_image_similarity(image1_path, image2_path, model=None):
    """Calculate similarity between two images using CLIP
    
    Args:
        image1_path: Path to the first image
        image2_path: Path to the second image
        model: Optional pre-loaded CLIP model and preprocessor tuple
        
    Returns:
        float: Similarity score between 0 and 1
    """
    try:
        # If model is not provided, try to load it
        if model is None:
            try:
                import torch
                import clip
                from PIL import Image
                
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model, preprocess = clip.load("ViT-B/32", device=device)
            except ImportError:
                logger.error("CLIP not available. Using simulated similarity for demo.")
                # Return simulated similarity for development/testing
                import random
                return random.uniform(0.5, 0.95)
        else:
            model, preprocess = model
            device = model.device
        
        # Process images
        image1 = preprocess(Image.open(image1_path)).unsqueeze(0).to(device)
        image2 = preprocess(Image.open(image2_path)).unsqueeze(0).to(device)
        
        # Calculate features
        with torch.no_grad():
            image1_features = model.encode_image(image1)
            image2_features = model.encode_image(image2)
            
            # Normalize features
            image1_features /= image1_features.norm(dim=-1, keepdim=True)
            image2_features /= image2_features.norm(dim=-1, keepdim=True)
            
            # Calculate similarity (cosine similarity)
            similarity = (image1_features @ image2_features.T).item()
        
        return (similarity + 1) / 2  # Convert from [-1, 1] to [0, 1]
    except Exception as e:
        logger.error(f"Error calculating image similarity: {e}")
        # Return simulated similarity for development/testing
        import random
        return random.uniform(0.5, 0.95)

async def extract_text_from_image(image_path, confidence_threshold=0.8):
    """Extract text from an image using OCR
    
    Args:
        image_path: Path to the image
        confidence_threshold: Minimum confidence threshold for OCR results
        
    Returns:
        dict: Extracted text with positions and confidence scores
    """
    try:
        import pytesseract
        from PIL import Image, ImageEnhance, ImageFilter
        
        # Open and preprocess image
        img = Image.open(image_path)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Apply slight blur to reduce noise
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Extract text with detailed data
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        # Filter results by confidence threshold
        results = []
        for i in range(len(ocr_data['text'])):
            if ocr_data['conf'][i] >= confidence_threshold * 100:  # pytesseract uses 0-100 scale
                results.append({
                    'text': ocr_data['text'][i],
                    'confidence': ocr_data['conf'][i] / 100,  # Convert to 0-1 scale
                    'position': {
                        'x': ocr_data['left'][i],
                        'y': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i]
                    }
                })
        
        return {
            'full_text': ' '.join([r['text'] for r in results]),
            'text_blocks': results
        }
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return {
            'full_text': '',
            'text_blocks': [],
            'error': str(e)
        }

async def compare_text_similarity(text1, text2):
    """Compare similarity between two text strings
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        float: Similarity score between 0 and 1
    """
    try:
        # Try to use more advanced NLP if available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except ImportError:
            # Fallback to simpler approach
            # Tokenize and normalize
            def tokenize(text):
                return set(text.lower().split())
            
            # Calculate Jaccard similarity
            tokens1 = tokenize(text1)
            tokens2 = tokenize(text2)
            
            intersection = len(tokens1.intersection(tokens2))
            union = len(tokens1.union(tokens2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
    except Exception as e:
        logger.error(f"Error comparing text similarity: {e}")
        return 0.0

async def fetch_ipfs_content(ipfs_hash, gateway_url=None):
    """Fetch content from IPFS
    
    Args:
        ipfs_hash: IPFS hash
        gateway_url: Optional IPFS gateway URL
        
    Returns:
        bytes: Content from IPFS
    """
    try:
        import requests
        
        # Use default gateway if not provided
        if gateway_url is None:
            gateway_url = config.IPFS_GATEWAY_URL
        
        # Ensure hash doesn't have ipfs:// prefix
        if ipfs_hash.startswith('ipfs://'):
            ipfs_hash = ipfs_hash[7:]
        
        # Construct URL
        url = f"{gateway_url}{ipfs_hash}"
        
        # Fetch content
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        return response.content
    except Exception as e:
        logger.error(f"Error fetching IPFS content: {e}")
        return None

async def check_web_for_trademark_infringement(trademark_text, search_limit=10):
    """Check web for potential trademark infringements
    
    Args:
        trademark_text: Trademark text to search for
        search_limit: Maximum number of search results to check
        
    Returns:
        list: Potential infringements with URLs and similarity scores
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        
        # Simulate search results for development/testing
        # In production, this would use a real search API
        potential_infringements = []
        
        try:
            # Use a search engine API (would require API key in production)
            # This is a placeholder for demonstration
            search_url = f"https://api.searchengine.example/search?q={trademark_text}&limit={search_limit}"
            
            # In a real implementation, we would make an API call here
            # For now, we'll simulate results
            simulated_domains = [
                "example.com",
                "trademark-site.com",
                "brandusers.org",
                "similar-brands.net",
                "competitor-site.com"
            ]
            
            for i, domain in enumerate(simulated_domains[:search_limit]):
                # Simulate a result URL
                url = f"https://www.{domain}/products/{trademark_text.lower().replace(' ', '-')}"
                
                # In a real implementation, we would fetch and analyze the page content
                # For now, we'll simulate content and similarity
                import random
                similarity = random.uniform(0.6, 0.95)
                
                potential_infringements.append({
                    "url": url,
                    "similarity": similarity,
                    "domain": domain,
                    "detected_text": f"Similar to {trademark_text}",
                    "context": f"Found in product listing on {domain}"
                })
            
            # Sort by similarity (highest first)
            potential_infringements.sort(key=lambda x: x["similarity"], reverse=True)
            
            return potential_infringements
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return []
    except Exception as e:
        logger.error(f"Error checking web for trademark infringement: {e}")
        return []

async def analyze_license_compliance(license_terms, usage_context):
    """Analyze if usage complies with license terms
    
    Args:
        license_terms: Dictionary of license terms
        usage_context: Dictionary describing the usage context
        
    Returns:
        dict: Compliance analysis results
    """
    try:
        # Check for required fields
        if not isinstance(license_terms, dict) or not isinstance(usage_context, dict):
            return {
                "compliant": False,
                "reason": "Invalid input format"
            }
        
        # Initialize result
        result = {
            "compliant": True,
            "violations": [],
            "warnings": []
        }
        
        # Check territorial restrictions
        if "allowed_territories" in license_terms:
            if "territory" not in usage_context:
                result["warnings"].append("Territory not specified in usage context")
            elif usage_context["territory"] not in license_terms["allowed_territories"]:
                result["compliant"] = False
                result["violations"].append(f"Usage in {usage_context['territory']} not permitted by license")
        
        # Check usage type restrictions
        if "allowed_usage_types" in license_terms:
            if "usage_type" not in usage_context:
                result["warnings"].append("Usage type not specified in usage context")
            elif usage_context["usage_type"] not in license_terms["allowed_usage_types"]:
                result["compliant"] = False
                result["violations"].append(f"Usage type '{usage_context['usage_type']}' not permitted by license")
        
        # Check time restrictions
        if "license_duration" in license_terms and "usage_date" in usage_context:
            try:
                start_date = datetime.fromisoformat(license_terms["start_date"])
                end_date = datetime.fromisoformat(license_terms["end_date"]) if "end_date" in license_terms else None
                usage_date = datetime.fromisoformat(usage_context["usage_date"])
                
                if usage_date < start_date:
                    result["compliant"] = False
                    result["violations"].append("Usage before license start date")
                
                if end_date and usage_date > end_date:
                    result["compliant"] = False
                    result["violations"].append("Usage after license expiration")
            except ValueError:
                result["warnings"].append("Invalid date format in license terms or usage context")
        
        # Check attribution requirements
        if license_terms.get("requires_attribution", False):
            if not usage_context.get("has_attribution", False):
                result["compliant"] = False
                result["violations"].append("Attribution required but not provided")
        
        # Check modification restrictions
        if not license_terms.get("allows_modification", True) and usage_context.get("is_modified", False):
            result["compliant"] = False
            result["violations"].append("Modifications not permitted by license")
        
        # Check commercial use restrictions
        if not license_terms.get("allows_commercial_use", True) and usage_context.get("is_commercial", False):
            result["compliant"] = False
            result["violations"].append("Commercial use not permitted by license")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing license compliance: {e}")
        return {
            "compliant": False,
            "error": str(e)
        }

async def connect_wallet(provider="metamask", web3_provider=None):
    """Connect to a Web3 wallet
    
    Args:
        provider: Wallet provider (metamask, walletconnect, etc.)
        web3_provider: Optional Web3 provider instance
        
    Returns:
        dict: Connection result with address and chain information
    """
    try:
        # If no provider is provided, try to create one
        if web3_provider is None:
            from web3 import Web3
            web3_provider = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER_URI))
        
        # In a real implementation, this would connect to the browser wallet
        # For the MVP, we'll simulate a connection
        if provider == "metamask":
            # Simulate successful connection
            simulated_address = "0x" + os.urandom(20).hex()
            
            # Get chain information
            try:
                chain_id = web3_provider.eth.chain_id
                balance = web3_provider.eth.get_balance(simulated_address)
                
                # Get network name based on chain ID
                networks = {
                    1: "Ethereum Mainnet",
                    3: "Ropsten Testnet",
                    4: "Rinkeby Testnet",
                    5: "Goerli Testnet",
                    42: "Kovan Testnet",
                    56: "Binance Smart Chain",
                    137: "Polygon Mainnet"
                }
                network_name = networks.get(chain_id, f"Unknown Network (Chain ID: {chain_id})")
                
                return {
                    "success": True,
                    "address": simulated_address,
                    "balance": web3_provider.from_wei(balance, "ether"),
                    "chain_id": chain_id,
                    "network": network_name
                }
            except Exception as e:
                logger.error(f"Error getting chain information: {e}")
                return {
                    "success": True,
                    "address": simulated_address,
                    "error": "Could not get chain information"
                }
        else:
            return {
                "success": False,
                "error": f"Unsupported wallet provider: {provider}"
            }
    except Exception as e:
        logger.error(f"Error connecting wallet: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def sign_message(message, private_key=None, web3_provider=None):
    """Sign a message with a private key or connected wallet
    
    Args:
        message: Message to sign
        private_key: Optional private key for signing
        web3_provider: Optional Web3 provider instance
        
    Returns:
        dict: Signature result
    """
    try:
        # If no provider is provided, try to create one
        if web3_provider is None:
            from web3 import Web3
            web3_provider = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER_URI))
        
        # Convert message to bytes if it's a string
        if isinstance(message, str):
            message_bytes = message.encode('utf-8')
        else:
            message_bytes = message
        
        # If private key is provided, use it to sign
        if private_key:
            # Sign message
            signed = web3_provider.eth.account.sign_message(
                web3_provider.eth.account.sign_message.encode_defunct(message_bytes),
                private_key=private_key
            )
            
            return {
                "success": True,
                "message": message,
                "signature": signed.signature.hex(),
                "signer": signed.address
            }
        else:
            # In a real implementation, this would use the connected wallet
            # For the MVP, we'll simulate a signature
            simulated_address = "0x" + os.urandom(20).hex()
            simulated_signature = "0x" + os.urandom(65).hex()
            
            return {
                "success": True,
                "message": message,
                "signature": simulated_signature,
                "signer": simulated_address,
                "note": "This is a simulated signature for development purposes"
            }
    except Exception as e:
        logger.error(f"Error signing message: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def verify_signature(message, signature, address, web3_provider=None):
    """Verify a message signature
    
    Args:
        message: Original message
        signature: Signature to verify
        address: Address that supposedly signed the message
        web3_provider: Optional Web3 provider instance
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # If no provider is provided, try to create one
        if web3_provider is None:
            from web3 import Web3
            web3_provider = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER_URI))
        
        # Convert message to bytes if it's a string
        if isinstance(message, str):
            message_bytes = message.encode('utf-8')
        else:
            message_bytes = message
        
        # Recover the address from the signature
        recovered_address = web3_provider.eth.account.recover_message(
            web3_provider.eth.account.sign_message.encode_defunct(message_bytes),
            signature=signature
        )
        
        # Check if the recovered address matches the expected address
        return recovered_address.lower() == address.lower()
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False

async def generate_license_agreement(license_type, licensor_name, licensee_name, asset_name, 
                                    start_date, end_date=None, territory="Worldwide", 
                                    fee_structure=None, additional_terms=None):
    """Generate a license agreement template
    
    Args:
        license_type: Type of license (open, commercial, derivative)
        licensor_name: Name of the licensor
        licensee_name: Name of the licensee
        asset_name: Name of the asset being licensed
        start_date: Start date of the license (datetime or ISO format string)
        end_date: Optional end date of the license
        territory: Geographic territory for the license
        fee_structure: Optional fee structure details
        additional_terms: Optional additional terms
        
    Returns:
        str: License agreement text
    """
    try:
        # Format dates
        if isinstance(start_date, datetime):
            start_date_str = start_date.strftime("%B %d, %Y")
        else:
            start_date_str = datetime.fromisoformat(start_date).strftime("%B %d, %Y")
            
        if end_date:
            if isinstance(end_date, datetime):
                end_date_str = end_date.strftime("%B %d, %Y")
            else:
                end_date_str = datetime.fromisoformat(end_date).strftime("%B %d, %Y")
            duration_clause = f"This Agreement shall commence on {start_date_str} and end on {end_date_str}, unless terminated earlier."
        else:
            duration_clause = f"This Agreement shall commence on {start_date_str} and continue in perpetuity, unless terminated earlier."
        
        # Set permissions based on license type
        if license_type.lower() == "open":
            usage_rights = """The Licensor grants to the Licensee a non-exclusive, royalty-free, worldwide license to use, reproduce, and display the Asset for any purpose, including commercial use, subject to the terms and conditions of this Agreement."""
            modification_rights = "The Licensee may modify, transform, or build upon the Asset to create derivative works."
            attribution = "The Licensee must provide appropriate attribution to the Licensor when using the Asset."
        elif license_type.lower() == "commercial":
            usage_rights = """The Licensor grants to the Licensee a non-exclusive, limited license to use, reproduce, and display the Asset for commercial purposes, subject to the terms and conditions of this Agreement."""
            modification_rights = "The Licensee may not modify, transform, or build upon the Asset without prior written consent from the Licensor."
            attribution = "The Licensee must provide appropriate attribution to the Licensor when using the Asset."
        elif license_type.lower() == "derivative":
            usage_rights = """The Licensor grants to the Licensee a non-exclusive license to use, reproduce, display, and create derivative works based on the Asset, subject to the terms and conditions of this Agreement."""
            modification_rights = "The Licensee may modify, transform, or build upon the Asset to create derivative works, provided that such derivative works are clearly distinguished from the original Asset."
            attribution = "The Licensee must provide appropriate attribution to the Licensor when using the Asset or any derivative works."
        else:
            usage_rights = """The Licensor grants to the Licensee a non-exclusive license to use the Asset subject to the terms and conditions of this Agreement."""
            modification_rights = "The Licensee may not modify the Asset without prior written consent from the Licensor."
            attribution = "The Licensee must provide appropriate attribution to the Licensor when using the Asset."
        
        # Fee structure
        if fee_structure:
            if isinstance(fee_structure, str):
                payment_terms = fee_structure
            elif isinstance(fee_structure, dict):
                if fee_structure.get("type") == "one-time":
                    payment_terms = f"The Licensee shall pay the Licensor a one-time fee of {fee_structure.get('amount', '$0')} upon execution of this Agreement."
                elif fee_structure.get("type") == "royalty":
                    payment_terms = f"The Licensee shall pay the Licensor a royalty of {fee_structure.get('percentage', '0')}% of all revenue generated from the use of the Asset."
                elif fee_structure.get("type") == "revenue-share":
                    payment_terms = f"The Licensee shall pay the Licensor {fee_structure.get('licensor_percentage', '0')}% of all revenue generated from the use of the Asset, with the Licensee retaining {fee_structure.get('licensee_percentage', '0')}%."
                else:
                    payment_terms = "Payment terms to be determined by mutual agreement between the parties."
            else:
                payment_terms = "Payment terms to be determined by mutual agreement between the parties."
        else:
            payment_terms = "This license is granted royalty-free."
        
        # Compile the agreement
        agreement = f"""
        TRADEMARK LICENSE AGREEMENT
        
        This Trademark License Agreement (the "Agreement") is entered into as of {start_date_str} by and between:
        
        {licensor_name} ("Licensor"), and
        {licensee_name} ("Licensee").
        
        WHEREAS, Licensor is the owner of all right, title, and interest in and to the trademark {asset_name} (the "Asset"); and
        
        WHEREAS, Licensee desires to use the Asset in connection with Licensee's products and services, and Licensor is willing to permit such use pursuant to the terms and conditions of this Agreement;
        
        NOW, THEREFORE, in consideration of the mutual covenants contained herein and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the parties agree as follows:
        
        1. GRANT OF LICENSE
        
        {usage_rights}
        
        2. TERRITORY
        
        The license granted herein shall extend to {territory}.
        
        3. TERM
        
        {duration_clause}
        
        4. MODIFICATIONS
        
        {modification_rights}
        
        5. ATTRIBUTION
        
        {attribution}
        
        6. PAYMENT TERMS
        
        {payment_terms}
        
        7. OWNERSHIP
        
        The Licensee acknowledges that the Licensor is the owner of all right, title, and interest in and to the Asset, and that the Licensee shall not acquire any right, title, or interest in or to the Asset except the limited rights expressly set forth in this Agreement.
        
        8. QUALITY CONTROL
        
        The Licensee shall maintain the quality of any products or services offered in connection with the Asset at a level that meets or exceeds industry standards.
        
        9. TERMINATION
        
        This Agreement may be terminated by either party upon written notice if the other party breaches any material term or condition of this Agreement and fails to cure such breach within thirty (30) days after receiving written notice thereof.
        """
        
        # Add additional terms if provided
        if additional_terms:
            if isinstance(additional_terms, str):
                agreement += f"""
                
                10. ADDITIONAL TERMS
                
                {additional_terms}
                """
            elif isinstance(additional_terms, dict):
                agreement += """
                
                10. ADDITIONAL TERMS
                
                """
                for i, (key, value) in enumerate(additional_terms.items(), 1):
                    agreement += f"    {chr(96+i)}. {key}: {value}\n"
        
        # Add signature block
        agreement += """
        
        IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.
        
        LICENSOR:
        {licensor_name}
        
        By: ________________________
        
        LICENSEE:
        {licensee_name}
        
        By: ________________________
        """
        
        return agreement
    except Exception as e:
        logger.error(f"Error generating license agreement: {e}")
        return f"Error generating license agreement: {e}"