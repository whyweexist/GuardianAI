import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from web3 import Web3

# Import from project
import config
from modules.blockchain.web3_utils import get_contract, sign_transaction, get_transaction_receipt

class LicenseManager:
    """Handles the creation and management of programmable IP licenses"""
    
    def __init__(self):
        """Initialize the License Manager"""
        self.web3 = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER_URI))
        self.story_protocol = None
        self.initialize_story_protocol()
    
    def initialize_story_protocol(self):
        """Initialize connection to Story Protocol"""
        try:
            # Get Story Protocol contract
            self.story_protocol = get_contract(config.STORY_PROTOCOL_ADDRESS)
        except Exception as e:
            print(f"Error connecting to Story Protocol: {e}")
    
    def generate_license_terms(self, license_type, creator_percentage, duration, territory, additional_terms=None):
        """Generate license terms based on parameters
        
        Args:
            license_type: Type of license (open, commercial, derivative)
            creator_percentage: Percentage of revenue for the creator
            duration: Duration of the license
            territory: Geographic territory for the license
            additional_terms: Additional custom terms
            
        Returns:
            dict: License terms
        """
        # Calculate end date based on duration
        start_date = datetime.now()
        
        if duration == "1 month":
            end_date = start_date + timedelta(days=30)
        elif duration == "3 months":
            end_date = start_date + timedelta(days=90)
        elif duration == "6 months":
            end_date = start_date + timedelta(days=180)
        elif duration == "1 year":
            end_date = start_date + timedelta(days=365)
        else:  # Perpetual
            end_date = None
        
        # Generate license terms
        terms = {
            "licenseType": license_type,
            "revenueShare": {
                "creator": creator_percentage,
                "licensee": 100 - creator_percentage
            },
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat() if end_date else "perpetual",
            "territory": territory,
            "createdAt": datetime.now().isoformat(),
            "permissions": self._get_permissions_by_type(license_type)
        }
        
        # Add additional terms if provided
        if additional_terms:
            terms["additionalTerms"] = additional_terms
        
        return terms
    
    def _get_permissions_by_type(self, license_type):
        """Get permissions based on license type
        
        Args:
            license_type: Type of license (open, commercial, derivative)
            
        Returns:
            dict: Permissions
        """
        if license_type.lower() == "open":
            return {
                "reproduction": True,
                "distribution": True,
                "commercialUse": False,
                "modification": False,
                "sublicensing": False
            }
        elif license_type.lower() == "commercial":
            return {
                "reproduction": True,
                "distribution": True,
                "commercialUse": True,
                "modification": False,
                "sublicensing": False
            }
        elif license_type.lower() == "derivative":
            return {
                "reproduction": True,
                "distribution": True,
                "commercialUse": True,
                "modification": True,
                "sublicensing": True
            }
        else:
            # Default to most restrictive
            return {
                "reproduction": False,
                "distribution": False,
                "commercialUse": False,
                "modification": False,
                "sublicensing": False
            }
    
    async def generate_license_contract(self, token_id, licensee_address, license_terms):
        """Generate a license contract for an IP asset
        
        Args:
            token_id: Token ID of the IP asset
            licensee_address: Ethereum address of the licensee
            license_terms: License terms
            
        Returns:
            dict: Contract generation result
        """
        try:
            # Convert license terms to JSON
            license_json = json.dumps(license_terms)
            
            # Create temporary file for license terms
            temp_file = Path(config.TEMP_DIR) / f"license_{token_id}_{int(datetime.now().timestamp())}.json"
            with open(temp_file, 'w') as f:
                f.write(license_json)
            
            # In a real implementation, this would upload to IPFS
            # For the MVP, we'll simulate an IPFS hash
            license_uri = f"ipfs://QmSimulatedLicense{token_id}{int(datetime.now().timestamp())}"
            
            # Clean up temporary file
            os.remove(temp_file)
            
            if self.story_protocol:
                # Prepare transaction data for license creation
                creator_address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"  # Simulated creator address
                tx_data = self.story_protocol.functions.createLicense(
                    token_id,
                    licensee_address,
                    license_uri
                ).build_transaction({
                    'from': creator_address,
                    'nonce': self.web3.eth.get_transaction_count(creator_address),
                    'gas': 2000000,
                    'gasPrice': self.web3.eth.gas_price
                })
                
                # Sign and send transaction
                tx_hash = sign_transaction(tx_data)
                
                # Get transaction receipt
                receipt = await get_transaction_receipt(tx_hash.hex() if hasattr(tx_hash, 'hex') else tx_hash)
                
                return {
                    "success": True,
                    "license_id": int(datetime.now().timestamp()),  # Simulated license ID
                    "token_id": token_id,
                    "licensee": licensee_address,
                    "license_uri": license_uri,
                    "transaction_hash": tx_hash.hex() if hasattr(tx_hash, 'hex') else tx_hash,
                    "terms": license_terms
                }
            else:
                # Simulate successful contract generation for demo purposes
                return {
                    "success": True,
                    "license_id": int(datetime.now().timestamp()),  # Simulated license ID
                    "token_id": token_id,
                    "licensee": licensee_address,
                    "license_uri": license_uri,
                    "transaction_hash": f"0x{os.urandom(32).hex()}",
                    "terms": license_terms
                }
        except Exception as e:
            print(f"Error generating license contract: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_license_info(self, license_id):
        """Get information about a license
        
        Args:
            license_id: License ID
            
        Returns:
            dict: License information
        """
        try:
            # In a real implementation, this would query the blockchain
            # For the MVP, we'll simulate license information
            return {
                "license_id": license_id,
                "token_id": 12345,
                "licensor": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "licensee": "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0",
                "license_uri": f"ipfs://QmSimulatedLicense{license_id}",
                "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
                "status": "active",
                "terms": {
                    "licenseType": "commercial",
                    "revenueShare": {
                        "creator": 70,
                        "licensee": 30
                    },
                    "startDate": (datetime.now() - timedelta(days=7)).isoformat(),
                    "endDate": (datetime.now() + timedelta(days=358)).isoformat(),
                    "territory": ["Worldwide"],
                    "permissions": {
                        "reproduction": True,
                        "distribution": True,
                        "commercialUse": True,
                        "modification": False,
                        "sublicensing": False
                    }
                }
            }
        except Exception as e:
            print(f"Error getting license info: {e}")
            return {
                "error": str(e)
            }

# Create singleton instance
license_manager = LicenseManager()

async def setup_license_terms(token_id, license_type, creator_percentage, duration, territory, additional_terms=None):
    """Set up license terms for an IP asset
    
    Args:
        token_id: Token ID of the IP asset
        license_type: Type of license (open, commercial, derivative)
        creator_percentage: Percentage of revenue for the creator
        duration: Duration of the license
        territory: Geographic territory for the license
        additional_terms: Additional custom terms
        
    Returns:
        dict: License terms setup result
    """
    # Generate license terms
    terms = license_manager.generate_license_terms(
        license_type, creator_percentage, duration, territory, additional_terms
    )
    
    return {
        "success": True,
        "token_id": token_id,
        "terms": terms
    }

async def generate_license_offer(token_id, licensee_address, license_terms):
    """Generate a license offer for an IP asset
    
    Args:
        token_id: Token ID of the IP asset
        licensee_address: Ethereum address of the licensee
        license_terms: License terms
        
    Returns:
        dict: License offer result
    """
    return await license_manager.generate_license_contract(token_id, licensee_address, license_terms)

async def get_license_details(license_id):
    """Get details of a license
    
    Args:
        license_id: License ID
        
    Returns:
        dict: License details
    """
    return await license_manager.get_license_info(license_id)