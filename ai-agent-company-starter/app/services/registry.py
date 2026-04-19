import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from app.config import get_settings


@lru_cache(maxsize=1)
def load_manifest() -> Dict[str, Any]:
    settings = get_settings()
    with open(settings.manifest_path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def clear_manifest_cache() -> None:
    load_manifest.cache_clear()


def load_global_rules() -> str:
    settings = get_settings()
    if settings.rules_file_path.exists():
        return settings.rules_file_path.read_text(encoding='utf-8')
    return ''


def list_agents(phase: str | None = None) -> List[Dict[str, Any]]:
    data = load_manifest()
    agents = data['agents']
    if phase:
        agents = [a for a in agents if a['phase'] == phase]
    return agents


def get_agent(agent_id: str) -> Dict[str, Any]:
    for agent in load_manifest()['agents']:
        if agent['id'] == agent_id:
            item = dict(agent)
            item['prompt_text'] = load_agent_prompt(item['prompt_path'])
            return item
    raise KeyError(agent_id)


def load_agent_prompt(prompt_path: str) -> str:
    settings = get_settings()
    absolute = (settings.base_dir / prompt_path).resolve()
    return Path(absolute).read_text(encoding='utf-8')


def update_agent_prompt(agent_id: str, prompt_text: str) -> Dict[str, str]:
    agent = get_agent(agent_id)
    settings = get_settings()
    prompt_file = (settings.base_dir / agent['prompt_path']).resolve()
    prompt_file.write_text(prompt_text, encoding='utf-8')
    clear_manifest_cache()
    return {'agent_id': agent_id, 'prompt_path': agent['prompt_path']}
