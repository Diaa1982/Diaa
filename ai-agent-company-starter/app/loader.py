import json
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List

from .config import MANIFEST_PATH

@lru_cache(maxsize=1)
def load_manifest() -> Dict[str, Any]:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)

def load_agent_prompt(prompt_path: str) -> str:
    absolute = MANIFEST_PATH.parent.parent / prompt_path
    return Path(absolute).read_text(encoding="utf-8")

def list_agents() -> List[Dict[str, Any]]:
    manifest = load_manifest()
    return manifest["agents"]

def get_agent(agent_id: str) -> Dict[str, Any]:
    for agent in list_agents():
        if agent["id"] == agent_id:
            data = dict(agent)
            data["prompt_text"] = load_agent_prompt(agent["prompt_path"])
            return data
    raise KeyError(agent_id)
