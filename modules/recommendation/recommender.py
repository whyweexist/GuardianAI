import asyncio
from datetime import datetime

# Import from project
from modules.licensing.license_manager import generate_license_offer, setup_license_terms
from modules.blockchain.web3_utils import get_token_metadata

class RecommendationEngine:
    """Generates licensing recommendations based on infringement detection"""
    
    def __init__(self):
        """Initialize the recommendation engine"""
        pass
    
    async def analyze_infringement(self, infringement_data):
        """Analyze infringement data and determine appropriate action
        
        Args:
            infringement_data: Infringement detection results
            
        Returns:
            dict: Recommended action
        """
        # Check if there are any potential infringements
        if not infringement_data.get("potential_infringements", []):
            return {
                "recommendation": "no_action",
                "reason": "No potential infringements detected"
            }
        
        # Get the highest similarity infringement
        infringements = infringement_data["potential_infringements"]
        highest_similarity = max(infringements, key=lambda x: x["similarity"])
        
        # Determine recommendation based on similarity score
        if highest_similarity["similarity"] >= 0.9:
            return {
                "recommendation": "takedown",
                "reason": f"High similarity ({highest_similarity['similarity']:.2f}) indicates likely infringement",
                "infringement": highest_similarity
            }
        elif highest_similarity["similarity"] >= 0.75:
            return {
                "recommendation": "license_offer",
                "reason": f"Moderate similarity ({highest_similarity['similarity']:.2f}) suggests potential for licensing",
                "infringement": highest_similarity
            }
        else:
            return {
                "recommendation": "monitor",
                "reason": f"Low similarity ({highest_similarity['similarity']:.2f}) suggests monitoring but no immediate action",
                "infringement": highest_similarity
            }
    
    async def generate_license_recommendation(self, token_id, infringement_data):
        """Generate a license recommendation based on infringement data
        
        Args:
            token_id: Token ID of the IP asset
            infringement_data: Infringement detection results
            
        Returns:
            dict: License recommendation
        """
        # Get token metadata
        metadata = await get_token_metadata(token_id)
        
        # Analyze infringement
        analysis = await self.analyze_infringement(infringement_data)
        
        # If recommendation is not for licensing, return analysis
        if analysis["recommendation"] != "license_offer":
            return analysis
        
        # Generate license terms based on asset type
        asset_type = metadata.get("type", "Logo")
        
        if asset_type.lower() in ["logo", "design", "image"]:
            # Visual assets typically have higher commercial value
            license_type = "commercial"
            creator_percentage = 70
            duration = "1 year"
        else:  # Text, name, etc.
            license_type = "commercial"
            creator_percentage = 60
            duration = "1 year"
        
        # Set up license terms
        license_terms = await setup_license_terms(
            token_id,
            license_type,
            creator_percentage,
            duration,
            ["Worldwide"],
            {"generatedFromInfringement": True}
        )
        
        # Return recommendation with license terms
        return {
            "recommendation": "license_offer",
            "reason": analysis["reason"],
            "infringement": analysis["infringement"],
            "license_terms": license_terms["terms"],
            "token_id": token_id,
            "metadata": metadata
        }
    
    async def generate_takedown_notice(self, token_id, infringement_data):
        """Generate a takedown notice template based on infringement data
        
        Args:
            token_id: Token ID of the IP asset
            infringement_data: Infringement detection results
            
        Returns:
            dict: Takedown notice template
        """
        # Get token metadata
        metadata = await get_token_metadata(token_id)
        
        # Analyze infringement
        analysis = await self.analyze_infringement(infringement_data)
        
        # If recommendation is not for takedown, return analysis
        if analysis["recommendation"] != "takedown":
            return analysis
        
        # Get infringement details
        infringement = analysis["infringement"]
        
        # Generate takedown notice template
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        takedown_template = f"""
[Your Company Name]
[Your Address]
[City, State ZIP]
[Your Email]
[Your Phone]

{current_date}

[Recipient Name]
[Recipient Address]
[City, State ZIP]

Re: Intellectual Property Infringement Notice

To Whom It May Concern:

I am writing to notify you that your website/business is infringing on my intellectual property rights. I own the {metadata.get('type', 'trademark')} to {metadata.get('name', 'Asset')}, which appears on your website/business at {infringement.get('source', '[URL/Location]')}.

The infringing content can be found at: {infringement.get('url', '[URL]')}

Under intellectual property law, I am requesting the immediate removal of the infringing material.

I have a good faith belief that the use of the material in the manner complained of is not authorized by me, the intellectual property owner.

Please respond within 10 business days to confirm you have removed the infringing content.

Sincerely,
[Your Name]
        """
        
        # Return recommendation with takedown notice
        return {
            "recommendation": "takedown",
            "reason": analysis["reason"],
            "infringement": analysis["infringement"],
            "takedown_notice": takedown_template,
            "token_id": token_id,
            "metadata": metadata
        }

# Create singleton instance
recommendation_engine = RecommendationEngine()

async def get_recommendations(token_id, infringement_data):
    """Get recommendations based on infringement data
    
    Args:
        token_id: Token ID of the IP asset
        infringement_data: Infringement detection results
        
    Returns:
        dict: Recommendations
    """
    # Analyze infringement
    analysis = await recommendation_engine.analyze_infringement(infringement_data)
    
    # Generate specific recommendations based on analysis
    if analysis["recommendation"] == "license_offer":
        license_recommendation = await recommendation_engine.generate_license_recommendation(token_id, infringement_data)
        return {
            "type": "license_offer",
            "data": license_recommendation
        }
    elif analysis["recommendation"] == "takedown":
        takedown_recommendation = await recommendation_engine.generate_takedown_notice(token_id, infringement_data)
        return {
            "type": "takedown",
            "data": takedown_recommendation
        }
    else:
        return {
            "type": "no_action",
            "data": analysis
        }