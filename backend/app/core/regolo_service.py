from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional, Union
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RegoloAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.regolo_api_key,
            base_url=settings.regolo_base_url
        )
        self.model = settings.regolo_model
        self.embedding_model = settings.regolo_embedding_model
    
    async def generate_embedding(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Union[str, Dict[str, Any]] = "required",
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if tools:
                params["tools"] = tools
                params["tool_choice"] = tool_choice
            
            if stream:
                return await self.client.chat.completions.create(
                    **params,
                    stream=True
                )
            else:
                return await self.client.chat.completions.create(
                    **params
                )
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    async def chat_completion_with_function_calling(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tool_responses: Optional[List[Dict[str, Any]]] = None
    ):
        try:
            if tool_responses:
                messages.extend(tool_responses)
            
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = await self.chat_completion(
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            tool_calls = assistant_message.tool_calls
            
            if tool_calls:
                return {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls
                    ]
                }
            else:
                return {
                    "content": assistant_message.content,
                    "tool_calls": None
                }
        except Exception as e:
            logger.error(f"Error in function calling: {e}")
            raise
    
    async def generate_with_context(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        if system_prompt is None:
            system_prompt = """Sei un assistente utile che risponde alle domande basandoti sul contesto fornito.
Usa SOLO le informazioni dal contesto per rispondere alle domande. Se il contesto non contiene
informazioni sufficienti per rispondere alla domanda, dillo chiaramente. Sii conciso e accurato."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contesto:\n{context}\n\nDomanda: {query}"}
        ]
        
        response = await self.chat_completion(messages=messages)
        return response.choices[0].message.content


regolo_service = RegoloAIService()
