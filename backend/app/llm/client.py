"""LLM client wrapper for Gemini API."""
import os
from typing import Optional, Dict, Any, AsyncGenerator
from ..config import get_settings
import json


class LLMClient:
    """Interface for LLM interactions."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM client."""
        self.settings = get_settings()
        self.api_key = api_key or self.settings.google_api_key
        self.model = None
        
        # Only initialize if API key is provided
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.settings.model_name)
                self.model_pro = genai.GenerativeModel(self.settings.model_name_pro)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")
                self.model = None
    
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[Dict] = None,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        Generate text from prompt.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction for the model
            response_schema: JSON schema for structured output
            stream: Whether to stream the response
        """
        if not self.model:
            # Fallback for testing without API key
            return self._fallback_response(prompt)
        
        try:
            # Configure generation
            config = {
                "temperature": self.settings.temperature,
                "max_output_tokens": self.settings.max_tokens,
            }
            
            if response_schema:
                config["response_mime_type"] = "application/json"
                config["response_schema"] = response_schema
            
            # Build full prompt
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            if stream:
                return self._generate_stream(full_prompt, config)
            else:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=config
                )
                return response.text
                
        except Exception as e:
            print(f"LLM generation error: {e}")
            return self._fallback_response(prompt)
    
    async def _generate_stream(self, prompt: str, config: Dict) -> AsyncGenerator[str, None]:
        """Stream generation response."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=config,
                stream=True
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"Stream error: {e}")
            yield self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when LLM is unavailable."""
        if "extract" in prompt.lower() and "profile" in prompt.lower():
            # Return empty JSON for profile extraction
            return json.dumps({
                "name": "Sample Event",
                "event_type": "wedding",
                "message": "Please fill in event details"
            })
        elif "ideas" in prompt.lower():
            return json.dumps({
                "themes": [
                    {
                        "title": "Classic Elegance",
                        "description": "A timeless theme with sophisticated decor and traditional elements.",
                        "cost_level": "medium"
                    }
                ]
            })
        else:
            return "LLM is currently unavailable. Using template-based planning."


# Fake client for testing
class FakeLLMClient(LLMClient):
    """Fake LLM client for testing."""
    
    def __init__(self):
        """Initialize fake client without API key."""
        self.settings = get_settings()
        self.model = None  # No real model
    
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[Dict] = None,
        stream: bool = False
    ) -> str:
        """Return canned responses for testing."""
        return self._fallback_response(prompt)
