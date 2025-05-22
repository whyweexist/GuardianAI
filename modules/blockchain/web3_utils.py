import os
import json
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
from web3.exceptions import ContractLogicError

# Import from project
import config

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER_URI))

# Add middleware for POA chains like Polygon
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

def connect_wallet(provider="metamask"):
    """Connect to a Web3 wallet
    
    Args:
        provider: Wallet provider (metamask, walletconnect, etc.)
        
    Returns:
        dict: Connection result with account address
    """
    try:
        # In a real implementation, this would integrate with the browser's
        # Web3 provider or WalletConnect. For the MVP, we'll simulate this.
        if provider == "metamask":
            # Simulate successful connection
            return {
                "success": True,
                "account": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "chain_id": config.CHAIN_ID,
                "provider": provider
            }
        else:
            return {
                "success": False,
                "error": f"Provider {provider} not supported"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_account_info(address):
    """Get account information
    
    Args:
        address: Ethereum address
        
    Returns:
        dict: Account information
    """
    try:
        balance = web3.eth.get_balance(address)
        return {
            "address": address,
            "balance": web3.from_wei(balance, "ether"),
            "chain_id": web3.eth.chain_id,
            "network": get_network_name(web3.eth.chain_id)
        }
    except Exception as e:
        return {
            "error": str(e)
        }

def get_network_name(chain_id):
    """Get network name from chain ID
    
    Args:
        chain_id: Ethereum chain ID
        
    Returns:
        str: Network name
    """
    networks = {
        1: "Ethereum Mainnet",
        5: "Goerli Testnet",
        137: "Polygon Mainnet",
        80001: "Mumbai Testnet"
    }
    return networks.get(chain_id, f"Unknown Network ({chain_id})")

def get_contract(address, abi_path=None):
    """Get contract instance
    
    Args:
        address: Contract address
        abi_path: Path to ABI JSON file
        
    Returns:
        Contract: Web3 contract instance
    """
    try:
        if abi_path:
            with open(abi_path, 'r') as f:
                abi = json.load(f)
        else:
            # For the MVP, we'll use a simplified ABI for Story Protocol
            # In a production environment, you would load the actual ABI from a file
            abi = [
                {
                    "inputs": [
                        {"internalType": "address", "name": "creator", "type": "address"},
                        {"internalType": "string", "name": "metadataURI", "type": "string"}
                    ],
                    "name": "registerIP",
                    "outputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                        {"internalType": "address", "name": "licensee", "type": "address"},
                        {"internalType": "string", "name": "licenseURI", "type": "string"}
                    ],
                    "name": "createLicense",
                    "outputs": [{"internalType": "uint256", "name": "licenseId", "type": "uint256"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
        
        return web3.eth.contract(address=address, abi=abi)
    except Exception as e:
        print(f"Error getting contract: {e}")
        return None

def sign_transaction(tx_data, private_key=None):
    """Sign and send a transaction
    
    Args:
        tx_data: Transaction data
        private_key: Private key for signing
        
    Returns:
        HexBytes: Transaction hash
    """
    try:
        if private_key:
            # Sign transaction with provided private key
            signed_tx = web3.eth.account.sign_transaction(tx_data, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return tx_hash
        else:
            # In a real implementation, this would use the connected wallet
            # For the MVP, we'll simulate a transaction hash
            return Web3.to_hex(os.urandom(32))
    except Exception as e:
        print(f"Error signing transaction: {e}")
        return None

async def get_transaction_receipt(tx_hash, timeout=120):
    """Get transaction receipt with timeout
    
    Args:
        tx_hash: Transaction hash
        timeout: Timeout in seconds
        
    Returns:
        dict: Transaction receipt
    """
    try:
        # In a real implementation, this would wait for the transaction to be mined
        # For the MVP, we'll simulate a successful transaction
        return {
            "status": 1,  # 1 = success, 0 = failure
            "transactionHash": tx_hash,
            "blockNumber": 12345678,
            "gasUsed": 2000000
        }
    except Exception as e:
        print(f"Error getting transaction receipt: {e}")
        return None

async def get_token_metadata(token_id):
    """Get token metadata from Story Protocol
    
    Args:
        token_id: Token ID
        
    Returns:
        dict: Token metadata
    """
    try:
        # In a real implementation, this would call the tokenURI function
        # and fetch the metadata from IPFS
        # For the MVP, we'll simulate metadata
        return {
            "name": f"Asset #{token_id}",
            "description": "A registered intellectual property asset",
            "creator": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            "type": "Logo",
            "assetHash": f"QmSimulated{token_id}",
            "createdAt": "2025-06-15T12:00:00Z"
        }
    except Exception as e:
        print(f"Error getting token metadata: {e}")
        return None