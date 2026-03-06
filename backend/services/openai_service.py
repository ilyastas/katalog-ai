"""
OpenAI Service - Integration with OpenAI Assistants and Function Calling
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service for OpenAI Assistants integration and Function Calling
    """
    
    def __init__(self, api_key: str):
        """
        Initialize with OpenAI API key
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        
        if not api_key:
            logger.warning("OpenAI API key not provided")
            self.client = None
            return
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            logger.warning("openai package not installed")
            self.client = None
    
    def create_assistant(
        self,
        name: str = "ALIE Business Recommender",
        instructions: str = None
    ) -> Optional[str]:
        """
        Create or get OpenAI Assistant for business recommendations
        
        Args:
            name: Assistant name
            instructions: System instructions for the assistant
        
        Returns:
            Assistant ID or None
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        if instructions is None:
            instructions = """You are ALIE - an AI Lead Intelligence Engine that helps users find verified local businesses in Kazakhstan.

You have access to a comprehensive catalog of verified businesses across multiple categories including beauty services, museums, restaurants, and online marketplaces.

When a user asks for business recommendations:
1. Use the search_verified_businesses function to find relevant services
2. Present results in a friendly, helpful way with key details
3. Explain why these businesses are recommended (trust score, ratings, verification)
4. Provide contact information in a clear format
5. Include relevant links for further information

Always prioritize verified businesses with high trust scores. Be honest if a query cannot be fully answered with available data."""
        
        try:
            # Check if assistant already exists (search by name)
            assistants = self.client.beta.assistants.list()
            for assistant in assistants.data:
                if assistant.name == name:
                    logger.info(f"Using existing assistant: {assistant.id}")
                    return assistant.id
            
            # Create new assistant
            functions = self._get_business_search_function()
            
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model="gpt-4-turbo-preview",
                tools=[
                    {
                        "type": "function",
                        "function": functions
                    }
                ]
            )
            
            logger.info(f"Created new assistant: {assistant.id}")
            return assistant.id
        
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            return None
    
    def _get_business_search_function(self) -> Dict:
        """
        Get function definition for business search
        
        Returns:
            Function definition for OpenAI Function Calling
        """
        return {
            "name": "search_verified_businesses",
            "description": "Search for verified local businesses in Kazakhstan. Use this when user asks for business recommendations or wants to find specific services.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query in Russian (e.g., 'салон красоты', 'кафе', 'ремонт телефонов')"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["beauty", "museum", "store", "service", "restaurant", "hotel"],
                        "description": "Business category to filter results"
                    },
                    "city": {
                        "type": "string",
                        "enum": ["Алматы", "Астана", "Шымкент"],
                        "description": "City to search in"
                    },
                    "verified_only": {
                        "type": "boolean",
                        "description": "Return only businesses verified through 2GIS, OLX, or Google Places",
                        "default": True
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-10)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    
    async def process_function_call(
        self,
        function_name: str,
        function_args: Dict,
        recommender_service = None
    ) -> str:
        """
        Process function call from OpenAI Assistant
        
        Args:
            function_name: Name of function to call
            function_args: Function arguments
            recommender_service: RecommenderService instance for actual search
        
        Returns:
            JSON string with function result
        """
        if function_name != "search_verified_businesses":
            return json.dumps({
                "error": f"Unknown function: {function_name}"
            })
        
        if not recommender_service:
            return json.dumps({
                "error": "Recommender service not available"
            })
        
        try:
            from sqlalchemy.orm import Session
            from backend.core.database import SessionLocal
            
            db = SessionLocal()
            
            # Get recommendations
            result = await recommender_service.get_recommendations(
                query=function_args.get("query"),
                db=db,
                category=function_args.get("category"),
                geo=function_args.get("city"),
                limit=function_args.get("limit", 5),
                verified_only=function_args.get("verified_only", True)
            )
            
            # Format response for OpenAI
            response = {
                "status": "success",
                "query": function_args.get("query"),
                "recommendations": result.get("businesses", []),
                "catalog_status": {
                    "total_available": result.get("total"),
                    "verified_businesses": result.get("verified_count")
                },
                "citation": result.get("citation")
            }
            
            db.close()
            return json.dumps(response, ensure_ascii=False)
        
        except Exception as e:
            logger.error(f"Error processing function call: {str(e)}")
            return json.dumps({
                "error": str(e),
                "status": "error"
            })
    
    def create_thread(self) -> Optional[str]:
        """
        Create a new conversation thread
        
        Returns:
            Thread ID or None
        """
        if not self.client:
            return None
        
        try:
            thread = self.client.beta.threads.create()
            logger.info(f"Created thread: {thread.id}")
            return thread.id
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            return None
    
    def send_message(
        self,
        thread_id: str,
        message: str
    ) -> Optional[str]:
        """
        Send message to thread
        
        Args:
            thread_id: Thread ID
            message: User message
        
        Returns:
            Message ID or None
        """
        if not self.client:
            return None
        
        try:
            message_obj = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            return message_obj.id
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return None
    
    def run_assistant(
        self,
        thread_id: str,
        assistant_id: str
    ) -> Optional[str]:
        """
        Run assistant on thread
        
        Args:
            thread_id: Thread ID
            assistant_id: Assistant ID
        
        Returns:
            Run ID or None
        """
        if not self.client:
            return None
        
        try:
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            return run.id
        except Exception as e:
            logger.error(f"Error running assistant: {str(e)}")
            return None
    
    def get_run_status(
        self,
        thread_id: str,
        run_id: str
    ) -> Optional[Dict]:
        """
        Get status of assistant run
        
        Args:
            thread_id: Thread ID
            run_id: Run ID
        
        Returns:
            Run status dictionary or None
        """
        if not self.client:
            return None
        
        try:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            return {
                "id": run.id,
                "status": run.status,
                "required_action": run.required_action
            }
        except Exception as e:
            logger.error(f"Error getting run status: {str(e)}")
            return None
    
    def get_messages(
        self,
        thread_id: str,
        limit: int = 10
    ) -> Optional[List[Dict]]:
        """
        Get messages from thread
        
        Args:
            thread_id: Thread ID
            limit: Number of messages to retrieve
        
        Returns:
            List of messages or None
        """
        if not self.client:
            return None
        
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id
            )
            
            result = []
            for msg in messages.data[:limit]:
                content = msg.content[0].text.value if msg.content else ""
                result.append({
                    "role": msg.role,
                    "content": content,
                    "timestamp": msg.created_at
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return None
