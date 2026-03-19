# sourcebot/dag/planner/task_decomposer.py

from typing import List
import json
import re
import logging
from sourcebot.utils.output import extract_json
from sourcebot.llm.core.message import Message
logger = logging.getLogger(__name__)

class TaskDecomposer:
    
    def __init__(self, llm, context_builder):
        self.llm = llm
        self.context_builder = context_builder

    async def decompose(self, query: str) -> List[str]:
        if not isinstance(query, str):
          query = json.dumps(query, ensure_ascii=False, indent=2)
        skills_summary = self.context_builder.build_skills_summary()
        rules = self.context_builder.build_rulse()
        decomposer_prompt = self.context_builder.build_decomposer_prompt()
        messages = [
            Message(role = "system", content = decomposer_prompt),
            Message(role = "user", content = f"""
USER REQUEST

{query}
"""),
        ]
        
        result = await self.llm.complete(messages)
        try:
            data = extract_json(result.content)
            return data["tasks"]
        except Exception as e:
            logger.error(f"Failed to parse DAG JSON: {e}")
