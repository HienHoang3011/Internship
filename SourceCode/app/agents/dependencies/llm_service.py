from app.infra.llm.gpt_oss_20b import GPTOSS20BService
from app.agents.tools.db_search import search_knowledge_base
from app.agents.tools.web_search import web_search

llm_service = GPTOSS20BService()

llm_safe = llm_service.llm 
llm_with_tool = llm_service.get_agent_llm(tools=[search_knowledge_base, web_search])