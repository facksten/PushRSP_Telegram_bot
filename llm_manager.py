"""
LLM Manager - Handles multiple LLM providers via LangChain
"""
from typing import Optional, Dict, Any, List
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from config import settings, runtime_config
from logger import get_logger

logger = get_logger(__name__)


class LLMManager:
    """Manages multiple LLM providers and model selection"""
    
    def __init__(self):
        self.providers: Dict[str, BaseChatModel] = {}
        self.system_prompt = self._load_system_prompt()
        self._initialize_providers()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from document"""
        try:
            with open('system_prompt.txt', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("system_prompt.txt not found, using default")
            return """You are PushTutor, an advanced Telegram learning assistant bot developed by facksten for the PushRSP team."""
    
    def _initialize_providers(self):
        """Initialize available LLM providers based on API keys"""
        # Gemini
        if settings.gemini_api_key:
            try:
                self.providers['gemini'] = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",  # Updated to latest model
                    google_api_key=settings.gemini_api_key,
                    temperature=0.7,
                    convert_system_message_to_human=True,
                )
                logger.info("Gemini provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        
        # OpenAI
        if settings.openai_api_key:
            try:
                self.providers['openai'] = ChatOpenAI(
                    model="gpt-4o",
                    api_key=settings.openai_api_key,
                    temperature=0.7,
                )
                logger.info("OpenAI provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        # OpenRouter
        if settings.openrouter_api_key:
            try:
                self.providers['openrouter'] = ChatOpenAI(
                    model="anthropic/claude-3.5-sonnet",
                    api_key=settings.openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0.7,
                )
                logger.info("OpenRouter provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter: {e}")
        
        if not self.providers:
            logger.error("No LLM providers available! Please configure API keys.")
    
    def get_provider(self, provider_name: str = None) -> Optional[BaseChatModel]:
        """Get LLM provider by name or use default"""
        if provider_name is None:
            provider_name = runtime_config.get('current_llm_provider', settings.default_llm_provider)
        
        provider = self.providers.get(provider_name)
        if not provider:
            logger.warning(f"Provider {provider_name} not available, using fallback")
            # Try to use any available provider
            if self.providers:
                provider = next(iter(self.providers.values()))
                logger.info(f"Using fallback provider: {list(self.providers.keys())[0]}")
        
        return provider
    
    def list_providers(self) -> List[str]:
        """List available providers"""
        return list(self.providers.keys())
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        provider: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate response using specified LLM provider
        
        Args:
            user_message: User's message
            conversation_history: List of previous messages [{'role': 'user/assistant', 'content': '...'}]
            provider: LLM provider name (gemini/openai/openrouter)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated response text
        """
        llm = self.get_provider(provider)
        if not llm:
            error_msg = "No LLM providers available. Please configure API keys in .env"
            logger.error(error_msg)
            return error_msg
        
        try:
            # Build messages
            messages = [SystemMessage(content=self.system_prompt)]

            # Add conversation history (filter out empty messages)
            if conversation_history:
                for msg in conversation_history:
                    content = msg.get('content', '').strip()
                    if not content:  # Skip empty messages
                        continue
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=content))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=content))

            # Add current user message (ensure it's not empty)
            user_message = user_message.strip() if user_message else ''
            if not user_message:
                logger.warning("Attempted to generate response with empty user message")
                return "متأسفم، پیام خالی ارسال شده است."

            messages.append(HumanMessage(content=user_message))

            logger.info(f"Generating response with {provider or 'default'} provider")
            logger.debug(f"Message history length: {len(messages)}")

            # Generate response
            response = await llm.ainvoke(messages)
            response_text = response.content
            
            logger.info(f"Generated response: {len(response_text)} chars")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return f"خطا در تولید پاسخ: {str(e)}"
    
    def generate_response_sync(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        provider: str = None,
    ) -> str:
        """Synchronous version of generate_response"""
        llm = self.get_provider(provider)
        if not llm:
            return "No LLM providers available"

        try:
            messages = [SystemMessage(content=self.system_prompt)]

            # Add conversation history (filter out empty messages)
            if conversation_history:
                for msg in conversation_history:
                    content = msg.get('content', '').strip()
                    if not content:  # Skip empty messages
                        continue
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=content))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=content))

            # Add current user message (ensure it's not empty)
            user_message = user_message.strip() if user_message else ''
            if not user_message:
                logger.warning("Attempted to generate response with empty user message")
                return "متأسفم، پیام خالی ارسال شده است."

            messages.append(HumanMessage(content=user_message))

            response = llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return f"خطا در تولید پاسخ: {str(e)}"


# Global LLM manager instance
llm_manager = LLMManager()
