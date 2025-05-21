import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum

# Import from project
import config
from modules.blockchain.web3_utils import get_contract, sign_transaction, get_transaction_receipt

class DisputeStatus(Enum):
    """Enum for dispute status"""
    PENDING = "pending"
    ARBITRATION = "arbitration"
    SETTLEMENT = "settlement"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class ArbitrationMethod(Enum):
    """Enum for arbitration methods"""
    DAO_VOTING = "dao_voting"
    SINGLE_ARBITER = "single_arbiter"
    EXPERT_PANEL = "expert_panel"

class DisputeHandler:
    """Handles dispute resolution for IP infringements"""
    
    def __init__(self):
        """Initialize the dispute handler"""
        self.disputes = {}  # In-memory store for disputes (would be a database in production)
    
    async def create_dispute(self, creator_address, token_id, infringement_data, respondent_address=None):
        """Create a new dispute
        
        Args:
            creator_address: Ethereum address of the IP creator
            token_id: Token ID of the IP asset
            infringement_data: Infringement detection results
            respondent_address: Ethereum address of the respondent (if known)
            
        Returns:
            dict: Dispute creation result
        """
        # Generate dispute ID
        dispute_id = f"dispute_{token_id}_{int(datetime.now().timestamp())}"
        
        # Create dispute record
        dispute = {
            "dispute_id": dispute_id,
            "creator_address": creator_address,
            "token_id": token_id,
            "respondent_address": respondent_address,
            "infringement_data": infringement_data,
            "status": DisputeStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolution": None,
            "arbitration_method": None,
            "arbitration_data": None,
            "settlement_offer": None,
            "freeze_status": False,
            "history": [
                {
                    "action": "dispute_created",
                    "timestamp": datetime.now().isoformat(),
                    "actor": creator_address,
                    "details": "Dispute created based on infringement detection"
                }
            ]
        }
        
        # Store dispute
        self.disputes[dispute_id] = dispute
        
        # In a production environment, this would also create an on-chain record
        # and potentially freeze the asset until resolution
        
        return {
            "success": True,
            "dispute_id": dispute_id,
            "status": dispute["status"],
            "created_at": dispute["created_at"]
        }
    
    async def get_dispute(self, dispute_id):
        """Get dispute details
        
        Args:
            dispute_id: Dispute ID
            
        Returns:
            dict: Dispute details
        """
        if dispute_id in self.disputes:
            return self.disputes[dispute_id]
        else:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
    
    async def update_dispute_status(self, dispute_id, status, actor_address, details=None):
        """Update dispute status
        
        Args:
            dispute_id: Dispute ID
            status: New status
            actor_address: Address of the actor making the change
            details: Additional details
            
        Returns:
            dict: Update result
        """
        if dispute_id not in self.disputes:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
        
        # Update status
        self.disputes[dispute_id]["status"] = status.value if isinstance(status, DisputeStatus) else status
        self.disputes[dispute_id]["updated_at"] = datetime.now().isoformat()
        
        # Add to history
        self.disputes[dispute_id]["history"].append({
            "action": "status_updated",
            "timestamp": datetime.now().isoformat(),
            "actor": actor_address,
            "details": details or f"Status updated to {status}"
        })
        
        return {
            "success": True,
            "dispute_id": dispute_id,
            "status": self.disputes[dispute_id]["status"],
            "updated_at": self.disputes[dispute_id]["updated_at"]
        }
    
    async def freeze_asset(self, dispute_id, actor_address):
        """Freeze an asset during dispute
        
        Args:
            dispute_id: Dispute ID
            actor_address: Address of the actor making the change
            
        Returns:
            dict: Freeze result
        """
        if dispute_id not in self.disputes:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
        
        # Update freeze status
        self.disputes[dispute_id]["freeze_status"] = True
        self.disputes[dispute_id]["updated_at"] = datetime.now().isoformat()
        
        # Add to history
        self.disputes[dispute_id]["history"].append({
            "action": "asset_frozen",
            "timestamp": datetime.now().isoformat(),
            "actor": actor_address,
            "details": "Asset frozen during dispute resolution"
        })
        
        # In a production environment, this would call a smart contract function
        # to freeze the asset on-chain
        
        return {
            "success": True,
            "dispute_id": dispute_id,
            "freeze_status": True,
            "updated_at": self.disputes[dispute_id]["updated_at"]
        }
    
    async def unfreeze_asset(self, dispute_id, actor_address):
        """Unfreeze an asset after dispute resolution
        
        Args:
            dispute_id: Dispute ID
            actor_address: Address of the actor making the change
            
        Returns:
            dict: Unfreeze result
        """
        if dispute_id not in self.disputes:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
        
        # Update freeze status
        self.disputes[dispute_id]["freeze_status"] = False
        self.disputes[dispute_id]["updated_at"] = datetime.now().isoformat()
        
        # Add to history
        self.disputes[dispute_id]["history"].append({
            "action": "asset_unfrozen",
            "timestamp": datetime.now().isoformat(),
            "actor": actor_address,
            "details": "Asset unfrozen after dispute resolution"
        })
        
        # In a production environment, this would call a smart contract function
        # to unfreeze the asset on-chain
        
        return {
            "success": True,
            "dispute_id": dispute_id,
            "freeze_status": False,
            "updated_at": self.disputes[dispute_id]["updated_at"]
        }
    
    async def initiate_arbitration(self, dispute_id, method, actor_address, arbitration_data=None):
        """Initiate arbitration for a dispute
        
        Args:
            dispute_id: Dispute ID
            method: Arbitration method
            actor_address: Address of the actor making the change
            arbitration_data: Additional arbitration data
            
        Returns:
            dict: Arbitration initiation result
        """
        if dispute_id not in self.disputes:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
        
        # Update arbitration data
        self.disputes[dispute_id]["arbitration_method"] = method.value if isinstance(method, ArbitrationMethod) else method
        self.disputes[dispute_id]["arbitration_data"] = arbitration_data or {}
        self.disputes[dispute_id]["status"] = DisputeStatus.ARBITRATION.value
        self.disputes[dispute_id]["updated_at"] = datetime.now().isoformat()
        
        # Set arbitration period
        arbitration_period = timedelta(days=config.ARBITRATION_PERIOD_DAYS)
        self.disputes[dispute_id]["arbitration_data"]["start_date"] = datetime.now().isoformat()
        self.disputes[dispute_id]["arbitration_data"]["end_date"] = (datetime.now() + arbitration_period).isoformat()
        
        # Add to history
        self.disputes[dispute_id]["history"].append({
            "action": "arbitration_initiated",
            "timestamp": datetime.now().isoformat(),
            "actor": actor_address,
            "details": f"Arbitration initiated using {method} method"
        })
        
        # In a production environment, this would initiate the appropriate
        # on-chain arbitration process based on the method
        
        return {
            "success": True,
            "dispute_id": dispute_id,
            "arbitration_method": self.disputes[dispute_id]["arbitration_method"],
            "arbitration_data": self.disputes[dispute_id]["arbitration_data"],
            "status": self.disputes[dispute_id]["status"],
            "updated_at": self.disputes[dispute_id]["updated_at"]
        }
    
    async def propose_settlement(self, dispute_id, proposer_address, settlement_terms):
        """Propose a settlement for a dispute
        
        Args:
            dispute_id: Dispute ID
            proposer_address: Address of the settlement proposer
            settlement_terms: Settlement terms
            
        Returns:
            dict: Settlement proposal result
        """
        if dispute_id not in self.disputes:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
        
        # Update settlement data
        self.disputes[dispute_id]["settlement_offer"] = {
            "proposer": proposer_address,
            "terms": settlement_terms,
            "proposed_at": datetime.now().isoformat(),
            "status": "pending"
        }
        self.disputes[dispute_id]["status"] = DisputeStatus.SETTLEMENT.value
        self.disputes[dispute_id]["updated_at"] = datetime.now().isoformat()
        
        # Add to history
        self.disputes[dispute_id]["history"].append({
            "action": "settlement_proposed",
            "timestamp": datetime.now().isoformat(),
            "actor": proposer_address,
            "details": "Settlement proposed"
        })
        
        return {
            "success": True,
            "dispute_id": dispute_id,
            "settlement_offer": self.disputes[dispute_id]["settlement_offer"],
            "status": self.disputes[dispute_id]["status"],
            "updated_at": self.disputes[dispute_id]["updated_at"]
        }
    
    async def respond_to_settlement(self, dispute_id, responder_address, accepted):
        """Respond to a settlement proposal
        
        Args:
            dispute_id: Dispute ID
            responder_address: Address of the responder
            accepted: Whether the settlement was accepted
            
        Returns:
            dict: Settlement response result
        """
        if dispute_id not in self.disputes:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
        
        if not self.disputes[dispute_id].get("settlement_offer"):
            return {
                "success": False,
                "error": "No settlement offer found for this dispute"
            }
        
        # Update settlement status
        self.disputes[dispute_id]["settlement_offer"]["status"] = "accepted" if accepted else "rejected"
        self.disputes[dispute_id]["settlement_offer"]["responded_at"] = datetime.now().isoformat()
        self.disputes[dispute_id]["settlement_offer"]["responder"] = responder_address
        
        # Update dispute status if accepted
        if accepted:
            self.disputes[dispute_id]["status"] = DisputeStatus.RESOLVED.value
            self.disputes[dispute_id]["resolution"] = {
                "type": "settlement",
                "terms": self.disputes[dispute_id]["settlement_offer"]["terms"],
                "resolved_at": datetime.now().isoformat()
            }
        else:
            # If rejected, go back to arbitration or pending
            if self.disputes[dispute_id].get("arbitration_method"):
                self.disputes[dispute_id]["status"] = DisputeStatus.ARBITRATION.value
            else:
                self.disputes[dispute_id]["status"] = DisputeStatus.PENDING.value
        
        self.disputes[dispute_id]["updated_at"] = datetime.now().isoformat()
        
        # Add to history
        self.disputes[dispute_id]["history"].append({
            "action": "settlement_response",
            "timestamp": datetime.now().isoformat(),
            "actor": responder_address,
            "details": f"Settlement {'accepted' if accepted else 'rejected'}"
        })
        
        return {
            "success": True,
            "dispute_id": dispute_id,
            "settlement_status": self.disputes[dispute_id]["settlement_offer"]["status"],
            "dispute_status": self.disputes[dispute_id]["status"],
            "updated_at": self.disputes[dispute_id]["updated_at"]
        }
    
    async def resolve_dispute(self, dispute_id, resolver_address, resolution_type, resolution_details):
        """Resolve a dispute
        
        Args:
            dispute_id: Dispute ID
            resolver_address: Address of the resolver
            resolution_type: Type of resolution (arbitration, settlement, etc.)
            resolution_details: Resolution details
            
        Returns:
            dict: Dispute resolution result
        """
        if dispute_id not in self.disputes:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
        
        # Update resolution data
        self.disputes[dispute_id]["resolution"] = {
            "type": resolution_type,
            "details": resolution_details,
            "resolver": resolver_address,
            "resolved_at": datetime.now().isoformat()
        }
        self.disputes[dispute_id]["status"] = DisputeStatus.RESOLVED.value
        self.disputes[dispute_id]["updated_at"] = datetime.now().isoformat()
        
        # Add to history
        self.disputes[dispute_id]["history"].append({
            "action": "dispute_resolved",
            "timestamp": datetime.now().isoformat(),
            "actor": resolver_address,
            "details": f"Dispute resolved via {resolution_type}"
        })
        
        # Unfreeze asset if it was frozen
        if self.disputes[dispute_id]["freeze_status"]:
            await self.unfreeze_asset(dispute_id, resolver_address)
        
        return {
            "success": True,
            "dispute_id": dispute_id,
            "resolution": self.disputes[dispute_id]["resolution"],
            "status": self.disputes[dispute_id]["status"],
            "updated_at": self.disputes[dispute_id]["updated_at"]
        }
    
    async def get_active_disputes(self, address=None):
        """Get active disputes
        
        Args:
            address: Filter by address (creator or respondent)
            
        Returns:
            list: Active disputes
        """
        active_disputes = []
        
        for dispute_id, dispute in self.disputes.items():
            if dispute["status"] != DisputeStatus.RESOLVED.value:
                if address is None or dispute["creator_address"] == address or dispute["respondent_address"] == address:
                    active_disputes.append(dispute)
        
        return active_disputes
    
    async def get_dispute_history(self, dispute_id):
        """Get dispute history
        
        Args:
            dispute_id: Dispute ID
            
        Returns:
            list: Dispute history
        """
        if dispute_id not in self.disputes:
            return {
                "success": False,
                "error": f"Dispute {dispute_id} not found"
            }
        
        return self.disputes[dispute_id]["history"]

# Create singleton instance
dispute_handler = DisputeHandler()

async def handle_dispute(action, **kwargs):
    """Handle dispute actions
    
    Args:
        action: Action to perform
        **kwargs: Action-specific arguments
        
    Returns:
        dict: Action result
    """
    if action == "create":
        return await dispute_handler.create_dispute(
            kwargs["creator_address"],
            kwargs["token_id"],
            kwargs["infringement_data"],
            kwargs.get("respondent_address")
        )
    elif action == "get":
        return await dispute_handler.get_dispute(kwargs["dispute_id"])
    elif action == "update_status":
        return await dispute_handler.update_dispute_status(
            kwargs["dispute_id"],
            kwargs["status"],
            kwargs["actor_address"],
            kwargs.get("details")
        )
    elif action == "freeze":
        return await dispute_handler.freeze_asset(
            kwargs["dispute_id"],
            kwargs["actor_address"]
        )
    elif action == "unfreeze":
        return await dispute_handler.unfreeze_asset(
            kwargs["dispute_id"],
            kwargs["actor_address"]
        )
    elif action == "arbitrate":
        return await dispute_handler.initiate_arbitration(
            kwargs["dispute_id"],
            kwargs["method"],
            kwargs["actor_address"],
            kwargs.get("arbitration_data")
        )
    elif action == "propose_settlement":
        return await dispute_handler.propose_settlement(
            kwargs["dispute_id"],
            kwargs["proposer_address"],
            kwargs["settlement_terms"]
        )
    elif action == "respond_to_settlement":
        return await dispute_handler.respond_to_settlement(
            kwargs["dispute_id"],
            kwargs["responder_address"],
            kwargs["accepted"]
        )
    elif action == "resolve":
        return await dispute_handler.resolve_dispute(
            kwargs["dispute_id"],
            kwargs["resolver_address"],
            kwargs["resolution_type"],
            kwargs["resolution_details"]
        )
    elif action == "get_active":
        return await dispute_handler.get_active_disputes(kwargs.get("address"))
    elif action == "get_history":
        return await dispute_handler.get_dispute_history(kwargs["dispute_id"])
    else:
        return {
            "success": False,
            "error": f"Unknown action: {action}"
        }