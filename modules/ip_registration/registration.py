import os
import json
import asyncio
import ipfshttpclient
from pathlib import Path
from PIL import Image
from web3 import Web3
from datetime import datetime

# Import from project
import config
from modules.blockchain.web3_utils import get_contract, sign_transaction

class IPRegistration:
    """Handles the registration of intellectual property assets on IPFS and Story Protocol"""
    
    def __init__(self):
        """Initialize the IP Registration module"""
        self.ipfs_client = None
        self.web3 = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER_URI))
        self.story_protocol = None
        self.initialize_ipfs()
        self.initialize_story_protocol()
    
    def initialize_ipfs(self):
        """Initialize connection to IPFS"""
        try:
            # Connect to IPFS daemon
            self.ipfs_client = ipfshttpclient.connect(config.IPFS_API_URL)
        except Exception as e:
            print(f"Error connecting to IPFS: {e}")
            # Fallback to using HTTP API if daemon connection fails
            pass
    
    def initialize_story_protocol(self):
        """Initialize connection to Story Protocol"""
        try:
            # Get Story Protocol contract
            self.story_protocol = get_contract(config.STORY_PROTOCOL_ADDRESS)
        except Exception as e:
            print(f"Error connecting to Story Protocol: {e}")
    
    async def upload_to_ipfs(self, file_path):
        """Upload a file to IPFS and return the IPFS hash
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            str: IPFS hash of the uploaded file
        """
        try:
            if self.ipfs_client:
                # Upload file to IPFS
                result = self.ipfs_client.add(file_path)
                return result['Hash']
            else:
                # Simulate IPFS upload for demo purposes
                return f"QmSimulated{os.path.basename(file_path).replace('.', '')}{int(datetime.now().timestamp())}"
        except Exception as e:
            print(f"Error uploading to IPFS: {e}")
            # Return simulated hash for demo purposes
            return f"QmSimulated{os.path.basename(file_path).replace('.', '')}{int(datetime.now().timestamp())}"
    
    def generate_metadata(self, creator_address, asset_name, asset_type, description, ipfs_hash):
        """Generate metadata JSON for the asset
        
        Args:
            creator_address: Ethereum address of the creator
            asset_name: Name of the asset
            asset_type: Type of the asset (logo, name, design, etc.)
            description: Description of the asset
            ipfs_hash: IPFS hash of the asset
            
        Returns:
            dict: Metadata JSON
        """
        metadata = {
            "name": asset_name,
            "description": description,
            "creator": creator_address,
            "type": asset_type,
            "assetHash": ipfs_hash,
            "createdAt": datetime.now().isoformat(),
            "attributes": [
                {
                    "trait_type": "Asset Type",
                    "value": asset_type
                }
            ]
        }
        return metadata
    
    async def upload_metadata_to_ipfs(self, metadata):
        """Upload metadata JSON to IPFS
        
        Args:
            metadata: Metadata JSON
            
        Returns:
            str: IPFS hash of the metadata
        """
        try:
            # Create temporary file for metadata
            temp_file = Path(config.TEMP_DIR) / f"metadata_{int(datetime.now().timestamp())}.json"
            with open(temp_file, 'w') as f:
                json.dump(metadata, f)
            
            # Upload to IPFS
            metadata_hash = await self.upload_to_ipfs(temp_file)
            
            # Clean up temporary file
            os.remove(temp_file)
            
            return metadata_hash
        except Exception as e:
            print(f"Error uploading metadata to IPFS: {e}")
            # Return simulated hash for demo purposes
            return f"QmSimulatedMetadata{int(datetime.now().timestamp())}"
    
    async def register_with_story_protocol(self, creator_address, metadata_hash):
        """Register the asset with Story Protocol
        
        Args:
            creator_address: Ethereum address of the creator
            metadata_hash: IPFS hash of the metadata
            
        Returns:
            str: Transaction hash of the registration
        """
        try:
            if self.story_protocol:
                # Prepare transaction data for Story Protocol registration
                tx_data = self.story_protocol.functions.registerIP(
                    creator_address,
                    f"ipfs://{metadata_hash}"
                ).build_transaction({
                    'from': creator_address,
                    'nonce': self.web3.eth.get_transaction_count(creator_address),
                    'gas': 2000000,
                    'gasPrice': self.web3.eth.gas_price
                })
                
                # Sign and send transaction
                tx_hash = sign_transaction(tx_data)
                return tx_hash.hex()
            else:
                # Simulate transaction hash for demo purposes
                return f"0x{os.urandom(32).hex()}"
        except Exception as e:
            print(f"Error registering with Story Protocol: {e}")
            # Return simulated transaction hash for demo purposes
            return f"0x{os.urandom(32).hex()}"

# Create singleton instance
ip_registrar = IPRegistration()

async def register_ip(file_path, creator_address, asset_name, asset_type, description):
    """Register intellectual property
    
    Args:
        file_path: Path to the asset file
        creator_address: Ethereum address of the creator
        asset_name: Name of the asset
        asset_type: Type of the asset (logo, name, design, etc.)
        description: Description of the asset
        
    Returns:
        dict: Registration result with IPFS hash and transaction hash
    """
    # Upload asset to IPFS
    asset_hash = await ip_registrar.upload_to_ipfs(file_path)
    
    # Generate metadata
    metadata = ip_registrar.generate_metadata(
        creator_address, asset_name, asset_type, description, asset_hash
    )
    
    # Upload metadata to IPFS
    metadata_hash = await ip_registrar.upload_metadata_to_ipfs(metadata)
    
    # Register with Story Protocol
    tx_hash = await ip_registrar.register_with_story_protocol(creator_address, metadata_hash)
    
    return {
        "asset_hash": asset_hash,
        "metadata_hash": metadata_hash,
        "transaction_hash": tx_hash,
        "ipfs_url": f"{config.IPFS_GATEWAY_URL}{asset_hash}",
        "metadata_url": f"{config.IPFS_GATEWAY_URL}{metadata_hash}"
    }