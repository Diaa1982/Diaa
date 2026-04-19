import json
from typing import Any, Dict

from app.services.registry import get_agent, load_global_rules


def render_prompt_package(agent_id: str, task: str, context: Dict[str, Any]) -> dict:
    agent = get_agent(agent_id)
    global_rules = load_global_rules()
    context_text = json.dumps(context, indent=2, ensure_ascii=False) if context else '{}'

    system_prompt = (
        f"GLOBAL OPERATING RULES\n{global_rules}\n\n"
        f"AGENT PROMPT\n{agent['prompt_text']}"
    ).strip()
    user_prompt = (
        f"TASK\n{task}\n\n"
        f"CONTEXT\n{context_text}\n\n"
        f"Return a structured professional response aligned to the selected agent role."
    )
    preview = f"SYSTEM:\n{system_prompt[:4000]}\n\nUSER:\n{user_prompt}"
    return {
        'agent': agent,
        'system_prompt': system_prompt,
        'user_prompt': user_prompt,
        'preview': preview,
    }
