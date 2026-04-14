"""
LangChain Agent implementation for Granblue RAG.
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.agents.tools.search import create_search_tool
from app.models.schemas import ChatMessage, Source

logger = setup_logging()
settings = get_settings()


class GranblueAgent:
    """Agent for Granblue Fantasy knowledge base."""
    
    SYSTEM_PROMPT = """あなたはグランブルーファンタジーの攻略情報に特化したAIアシスタントです。

あなたの役割：
- ユーザーの質問に対して、正確で役立つ攻略情報を提供する
- キャラクター、武器、編成、クエストなどの情報を検索・分析する
- 初心者から上級者まで、レベルに応じたアドバイスを提供する
- 必ず情報源を明示し、信頼性の高い回答をする

回答のガイドライン：
1. まず質問の意図を理解し、必要な情報を検索する
2. 検索結果に基づいて回答を構成する
3. 具体的で実践的なアドバイスを提供する
4. 代替案や注意点も含める
5. 情報源を明示する

利用可能なツール：
- search_knowledge: グラブルの攻略情報を検索する

質問に対して、丁寧で分かりやすい日本語で回答してください。
"""
    
    def __init__(self):
        """Initialize agent."""
        self.settings = settings
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base,
        )
        
        # Create tools
        self.tools = [
            create_search_tool(),
        ]
        
        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )
        
        logger.info("Agent initialized successfully")
    
    def invoke(
        self,
        message: str,
        chat_history: Optional[List[ChatMessage]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke agent with a message.
        
        Args:
            message: User message
            chat_history: Previous chat messages
            context: Additional context (user info, etc.)
            
        Returns:
            Agent response with sources
        """
        try:
            logger.info(f"Processing message: {message[:100]}...")
            
            # Prepare chat history
            history = []
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages
                    if msg.role == "user":
                        history.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        history.append(AIMessage(content=msg.content))
            
            # Add context to message if provided
            enhanced_message = message
            if context:
                context_str = self._format_context(context)
                if context_str:
                    enhanced_message = f"{context_str}\n\n質問: {message}"
            
            # Invoke agent
            result = self.agent_executor.invoke({
                "input": enhanced_message,
                "chat_history": history,
            })
            
            logger.info("Agent response generated successfully")
            
            return {
                "response": result["output"],
                "sources": self._extract_sources(result),
                "intermediate_steps": result.get("intermediate_steps", []),
            }
            
        except Exception as e:
            logger.error(f"Agent invocation failed: {e}")
            raise
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format user context into string."""
        parts = []
        
        if "user_rank" in context and context["user_rank"]:
            parts.append(f"ユーザーランク: {context['user_rank']}")
        
        if "owned_characters" in context and context["owned_characters"]:
            chars = ", ".join(context["owned_characters"][:10])
            parts.append(f"所持キャラクター: {chars}")
        
        if "favorite_element" in context and context["favorite_element"]:
            parts.append(f"好きな属性: {context['favorite_element']}")
        
        return "\n".join(parts) if parts else ""
    
    def _extract_sources(self, result: Dict[str, Any]) -> List[Source]:
        """Extract sources from agent result."""
        sources = []
        
        # Extract from intermediate steps
        for step in result.get("intermediate_steps", []):
            if len(step) >= 2:
                action, observation = step[0], step[1]
                
                # Parse observation for document metadata
                # This is a simple implementation - can be enhanced
                if isinstance(observation, str) and "タイプ:" in observation:
                    # Extract basic info from formatted context
                    # In production, you'd want to parse this more carefully
                    pass
        
        return sources


def get_agent() -> GranblueAgent:
    """Get agent instance."""
    return GranblueAgent()
