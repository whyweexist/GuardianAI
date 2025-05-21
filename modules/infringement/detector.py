import os
import asyncio
import torch
import numpy as np
import cv2
import pytesseract
from PIL import Image
from pathlib import Path
from datetime import datetime
from scipy.spatial.distance import cosine

# Import CLIP for image similarity
try:
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    print("CLIP not available. Using simulated similarity for demo.")
    CLIP_AVAILABLE = False

# Import from project
import config
from modules.blockchain.web3_utils import get_token_metadata

class InfringementDetector:
    """AI-powered infringement detection using CLIP and OCR"""
    
    def __init__(self):
        """Initialize the infringement detector"""
        self.clip_model = None
        self.clip_preprocess = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.initialize_clip()
    
    def initialize_clip(self):
        """Initialize CLIP model for image similarity"""
        if CLIP_AVAILABLE:
            try:
                self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
                print(f"CLIP model loaded on {self.device}")
            except Exception as e:
                print(f"Error loading CLIP model: {e}")
    
    async def detect_image_similarity(self, original_image_path, comparison_image_path):
        """Detect similarity between two images using CLIP
        
        Args:
            original_image_path: Path to the original image
            comparison_image_path: Path to the comparison image
            
        Returns:
            float: Similarity score (0-1)
        """
        if self.clip_model and self.clip_preprocess:
            try:
                # Load and preprocess images
                original_image = self.clip_preprocess(Image.open(original_image_path)).unsqueeze(0).to(self.device)
                comparison_image = self.clip_preprocess(Image.open(comparison_image_path)).unsqueeze(0).to(self.device)
                
                # Get image features
                with torch.no_grad():
                    original_features = self.clip_model.encode_image(original_image)
                    comparison_features = self.clip_model.encode_image(comparison_image)
                
                # Calculate cosine similarity
                similarity = 1 - cosine(original_features.cpu().numpy().flatten(), 
                                       comparison_features.cpu().numpy().flatten())
                
                return float(similarity)
            except Exception as e:
                print(f"Error detecting image similarity: {e}")
                # Return simulated similarity for demo purposes
                return np.random.uniform(0.6, 0.95)
        else:
            # Simulate similarity for demo purposes
            return np.random.uniform(0.6, 0.95)
    
    async def extract_text_from_image(self, image_path):
        """Extract text from image using OCR
        
        Args:
            image_path: Path to the image
            
        Returns:
            str: Extracted text
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing to improve OCR accuracy
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(gray)
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            # Return empty string for demo purposes
            return ""
    
    async def calculate_text_similarity(self, text1, text2):
        """Calculate similarity between two text strings
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            float: Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    async def crawl_web_for_similar_images(self, image_path, search_terms=None):
        """Simulate web crawling for similar images
        
        Args:
            image_path: Path to the image to search for
            search_terms: Additional search terms
            
        Returns:
            list: List of potential matches
        """
        # In a real implementation, this would use a web crawler or API
        # For the MVP, we'll simulate results
        await asyncio.sleep(2)  # Simulate API call delay
        
        # Generate simulated results
        num_results = np.random.randint(1, 5)
        results = []
        
        for i in range(num_results):
            similarity = np.random.uniform(0.6, 0.95)
            results.append({
                "url": f"https://example{i}.com/image{i}.jpg",
                "similarity": similarity,
                "source": f"example{i}.com",
                "detected_at": datetime.now().isoformat()
            })
        
        return results
    
    async def check_infringement(self, asset_path, asset_type, token_id=None, threshold=None):
        """Check for potential infringements of an IP asset
        
        Args:
            asset_path: Path to the asset file
            asset_type: Type of the asset (logo, name, design, etc.)
            token_id: Token ID of the registered asset
            threshold: Similarity threshold (0-1)
            
        Returns:
            dict: Infringement check results
        """
        if threshold is None:
            threshold = config.SIMILARITY_THRESHOLD
        
        results = {
            "asset_path": asset_path,
            "asset_type": asset_type,
            "token_id": token_id,
            "threshold": threshold,
            "potential_infringements": [],
            "check_completed": datetime.now().isoformat()
        }
        
        # Get metadata if token_id is provided
        metadata = None
        if token_id:
            metadata = await get_token_metadata(token_id)
            results["metadata"] = metadata
        
        # Check based on asset type
        if asset_type.lower() in ["logo", "design", "image"]:
            # Image-based detection using CLIP
            web_results = await self.crawl_web_for_similar_images(asset_path)
            
            # Process results
            for result in web_results:
                if result["similarity"] >= threshold:
                    results["potential_infringements"].append({
                        "type": "image_similarity",
                        "url": result["url"],
                        "source": result["source"],
                        "similarity": result["similarity"],
                        "detected_at": result["detected_at"],
                        "exceeds_threshold": result["similarity"] >= threshold
                    })
        
        elif asset_type.lower() in ["name", "text"]:
            # Text-based detection using OCR
            # In a real implementation, this would search databases and the web
            # For the MVP, we'll simulate results
            await asyncio.sleep(1)  # Simulate search delay
            
            # Extract text if it's an image containing text
            if os.path.exists(asset_path):
                extracted_text = await self.extract_text_from_image(asset_path)
                results["extracted_text"] = extracted_text
                
                # Simulate finding similar text
                num_results = np.random.randint(1, 3)
                for i in range(num_results):
                    similarity = np.random.uniform(0.6, 0.95)
                    if similarity >= threshold:
                        results["potential_infringements"].append({
                            "type": "text_similarity",
                            "url": f"https://example{i}.com/page{i}",
                            "source": f"example{i}.com",
                            "similarity": similarity,
                            "detected_at": datetime.now().isoformat(),
                            "exceeds_threshold": similarity >= threshold
                        })
        
        return results

# Create singleton instance
infringement_detector = InfringementDetector()

async def check_infringement(asset_path, asset_type, token_id=None, threshold=None):
    """Check for potential infringements of an IP asset
    
    Args:
        asset_path: Path to the asset file
        asset_type: Type of the asset (logo, name, design, etc.)
        token_id: Token ID of the registered asset
        threshold: Similarity threshold (0-1)
        
    Returns:
        dict: Infringement check results
    """
    return await infringement_detector.check_infringement(asset_path, asset_type, token_id, threshold)