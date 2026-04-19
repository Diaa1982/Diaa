import logging
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

import httpx

from app.config import get_settings
from app.services.execution_store import execution_store
from app.services.prompt_renderer import render_prompt_package

logger = logging.getLogger(__name__)


class ExecutionService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def execute(self, agent_id: str, task: str, context: Dict[str, Any], mode: str | None = None) -> Dict[str, Any]:
        selected_mode = (mode or self.settings.default_execution_mode).strip()
        now = datetime.now(timezone.utc).isoformat()
        execution_id = str(uuid4())
        package = render_prompt_package(agent_id=agent_id, task=task, context=context)

        record = {
            'execution_id': execution_id,
            'agent_id': agent_id,
            'mode': selected_mode,
            'status': 'running',
            'task': task,
            'context': context,
            'output_text': '',
            'rendered_prompt_preview': package['preview'],
            'error_text': '',
            'created_at': now,
            'updated_at': now,
        }
        execution_store.create(record)

        try:
            if selected_mode == 'mock':
                output_text = self._run_mock(agent_id, task, context, package)
            elif selected_mode == 'prompt_only':
                output_text = self._run_prompt_only(package)
            elif selected_mode == 'openai_compatible':
                output_text = await self._run_openai_compatible(package)
            else:
                raise ValueError(f'Unsupported execution mode: {selected_mode}')

            execution_store.update(
                execution_id,
                status='completed',
                output_text=output_text,
                rendered_prompt_preview=package['preview'],
                error_text='',
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception('Execution failed for %s', execution_id)
            execution_store.update(
                execution_id,
                status='failed',
                output_text='',
                rendered_prompt_preview=package['preview'],
                error_text=str(exc),
            )
            raise

        saved = execution_store.get(execution_id)
        if saved is None:
            raise RuntimeError('Execution record missing after completion.')
        return saved

    async def retry(self, execution_id: str) -> Dict[str, Any]:
        existing = execution_store.get(execution_id)
        if not existing:
            raise KeyError(execution_id)
        return await self.execute(
            agent_id=existing['agent_id'],
            task=existing['task'],
            context=existing['context'],
            mode=existing['mode'],
        )

    def _run_mock(self, agent_id: str, task: str, context: Dict[str, Any], package: Dict[str, Any]) -> str:
        context_keys = ', '.join(sorted(context.keys())) if context else 'none'
        return f'''# Mock Execution Result

## Agent
- ID: {agent_id}
- Name: {package['agent']['name']}
- Role: {package['agent']['role_title']}

## Task Summary
{task}

## Context Received
- Keys: {context_keys}

## Recommended Response Structure
1. Objective clarification
2. Current-state interpretation
3. Key findings or commercial implications
4. Risks and assumptions
5. Recommended next action

## Draft Output
This is a deterministic mock response generated for workflow validation. Replace `mock` mode with `openai_compatible` after environment credentials and routing are configured.

## Notes
- Prompt path: {package['agent']['prompt_path']}
- Execution mode: mock
'''

    def _run_prompt_only(self, package: Dict[str, Any]) -> str:
        return (
            '# Prompt Package\n\n'
            '## System Prompt\n'
            f"```text\n{package['system_prompt']}\n```\n\n"
            '## User Prompt\n'
            f"```text\n{package['user_prompt']}\n```\n"
        )

    async def _run_openai_compatible(self, package: Dict[str, Any]) -> str:
        if not self.settings.llm_base_url or not self.settings.llm_api_key or not self.settings.llm_model:
            raise RuntimeError('LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL must be configured for openai_compatible mode.')

        payload = {
            'model': self.settings.llm_model,
            'messages': [
                {'role': 'system', 'content': package['system_prompt']},
                {'role': 'user', 'content': package['user_prompt']},
            ],
            'temperature': self.settings.llm_temperature,
            'max_tokens': self.settings.llm_max_tokens,
        }
        headers = {
            'Authorization': f'Bearer {self.settings.llm_api_key}',
            'Content-Type': 'application/json',
        }
        url = self.settings.llm_base_url.rstrip('/') + '/chat/completions'
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        try:
            return data['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError('Unexpected chat completions response format.') from exc


execution_service = ExecutionService()
