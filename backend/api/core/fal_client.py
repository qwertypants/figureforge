"""
fal.ai client for image generation
Handles API calls to fal.ai for generating images
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from django.conf import settings


class FalAIClient:
    """Client for interacting with fal.ai API"""
    
    def __init__(self):
        self.api_key = settings.FAL_API_KEY
        self.base_url = "https://api.fal.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a request to the fal.ai API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"fal.ai API request failed: {str(e)}")
    
    def generate_image(self, prompt: str, model_id: str = "flux/dev", 
                      parameters: Optional[Dict] = None) -> Dict:
        """Generate an image using fal.ai"""
        
        # Default parameters
        default_params = {
            "prompt": prompt,
            "image_size": "square",
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "num_images": 1,
            "enable_safety_checker": True,
            "output_format": "png"
        }
        
        # Merge with provided parameters
        if parameters:
            default_params.update(parameters)
        
        # Submit generation request
        endpoint = f"/models/{model_id}/generate"
        result = self._make_request("POST", endpoint, default_params)
        
        # fal.ai returns results immediately or a request_id for polling
        if "images" in result:
            return result
        elif "request_id" in result:
            # Poll for results
            return self._poll_for_results(result["request_id"])
        else:
            raise Exception("Unexpected response from fal.ai")
    
    def _poll_for_results(self, request_id: str, max_attempts: int = 60, 
                         interval: int = 2) -> Dict:
        """Poll for generation results"""
        endpoint = f"/requests/{request_id}"
        
        for attempt in range(max_attempts):
            result = self._make_request("GET", endpoint)
            
            if result.get("status") == "completed":
                return result.get("result", {})
            elif result.get("status") == "failed":
                raise Exception(f"Generation failed: {result.get('error', 'Unknown error')}")
            
            time.sleep(interval)
        
        raise Exception("Generation timed out")
    
    def get_model_info(self, model_id: str = "flux/dev") -> Dict:
        """Get information about a model"""
        endpoint = f"/models/{model_id}"
        return self._make_request("GET", endpoint)


class ImageGenerator:
    """High-level interface for image generation"""
    
    def __init__(self):
        self.client = FalAIClient()
        
        # Model configurations
        self.models = {
            "flux_dev": {
                "id": "flux/dev",
                "name": "FLUX.1 Dev",
                "cost_cents": 25,  # Cost per image in cents
                "parameters": {
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5
                }
            },
            "flux_schnell": {
                "id": "flux/schnell", 
                "name": "FLUX.1 Schnell",
                "cost_cents": 10,
                "parameters": {
                    "num_inference_steps": 4
                }
            },
            "stable_diffusion": {
                "id": "stable-diffusion-v3-medium",
                "name": "Stable Diffusion 3",
                "cost_cents": 15,
                "parameters": {
                    "num_inference_steps": 28,
                    "guidance_scale": 7.0
                }
            }
        }
    
    def generate_from_filters(self, filters: Dict[str, Any], 
                            model_key: str = "flux_dev") -> List[Dict]:
        """Generate images based on filter parameters"""
        
        # Get model configuration
        model_config = self.models.get(model_key, self.models["flux_dev"])
        
        # Build prompt from filters
        prompt = self._build_prompt(filters)
        
        # Prepare parameters
        parameters = {
            **model_config["parameters"],
            "seed": filters.get("seed"),
            "image_size": self._get_image_size(filters.get("aspect_ratio", "square")),
            "num_images": 1  # We generate one at a time for better control
        }
        
        # Remove None values
        parameters = {k: v for k, v in parameters.items() if v is not None}
        
        try:
            # Generate image
            result = self.client.generate_image(
                prompt=prompt,
                model_id=model_config["id"],
                parameters=parameters
            )
            
            # Process results
            images = []
            for image_data in result.get("images", []):
                images.append({
                    "url": image_data.get("url"),
                    "seed": result.get("seed", image_data.get("seed")),
                    "prompt": prompt,
                    "model_id": model_config["id"],
                    "model_name": model_config["name"],
                    "cost_cents": model_config["cost_cents"],
                    "parameters": parameters
                })
            
            return images
            
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    def _build_prompt(self, filters: Dict[str, Any]) -> str:
        """Build a prompt from filter parameters"""
        prompt_parts = []
        
        # Base description
        base = filters.get("base_prompt", "A human figure reference")
        prompt_parts.append(base)
        
        # Body type
        if filters.get("body_type"):
            prompt_parts.append(f"{filters['body_type']} body type")
        
        # Pose
        if filters.get("pose"):
            prompt_parts.append(f"in {filters['pose']} pose")
        
        # Clothing
        if filters.get("clothing"):
            prompt_parts.append(f"wearing {filters['clothing']}")
        
        # Lighting
        if filters.get("lighting"):
            prompt_parts.append(f"with {filters['lighting']} lighting")
        
        # Background
        if filters.get("background"):
            prompt_parts.append(f"{filters['background']} background")
        else:
            prompt_parts.append("simple neutral background")
        
        # Style modifiers
        style_parts = [
            "professional reference photo",
            "full body visible",
            "clear details",
            "suitable for figure drawing practice"
        ]
        
        # Combine all parts
        full_prompt = ", ".join(prompt_parts) + ". " + ", ".join(style_parts)
        
        # Add negative prompt guidance
        full_prompt += " --no nsfw, nude, explicit, inappropriate"
        
        return full_prompt
    
    def _get_image_size(self, aspect_ratio: str) -> str:
        """Convert aspect ratio to fal.ai image size parameter"""
        size_map = {
            "square": "square",
            "portrait": "portrait_4_3", 
            "landscape": "landscape_4_3",
            "wide": "landscape_16_9",
            "tall": "portrait_16_9"
        }
        return size_map.get(aspect_ratio, "square")
    
    def estimate_cost(self, batch_size: int, model_key: str = "flux_dev") -> int:
        """Estimate cost in cents for a batch of images"""
        model_config = self.models.get(model_key, self.models["flux_dev"])
        return batch_size * model_config["cost_cents"]
    
    def generate_batch(self, filters: Dict[str, Any], batch_size: int,
                      model_key: str = "flux_dev") -> List[Dict]:
        """Generate a batch of images with variations"""
        images = []
        
        # Generate each image with a different seed if not specified
        base_seed = filters.get("seed")
        
        for i in range(batch_size):
            # Vary the seed for each image
            if base_seed is not None:
                filters["seed"] = base_seed + i
            
            try:
                batch_images = self.generate_from_filters(filters, model_key)
                images.extend(batch_images)
            except Exception as e:
                # Log error but continue with other images
                print(f"Failed to generate image {i+1}: {str(e)}")
        
        return images
