async function savePrompt(agentId) {
  const promptText = document.getElementById('prompt-editor').value;
  const status = document.getElementById('save-status');
  status.textContent = 'Saving...';
  try {
    const res = await fetch(`/api/v1/agents/${agentId}/prompt`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt_text: promptText }),
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || 'Failed to save prompt');
    }
    status.textContent = 'Prompt saved.';
  } catch (err) {
    status.textContent = err.message;
  }
}

async function runExecution(agentId) {
  const output = document.getElementById('execution-output');
  output.textContent = 'Running...';
  let context = {};
  try {
    context = JSON.parse(document.getElementById('execution-context').value || '{}');
  } catch (err) {
    output.textContent = `Invalid JSON in context: ${err.message}`;
    return;
  }
  const payload = {
    agent_id: agentId,
    task: document.getElementById('execution-task').value,
    context,
    mode: document.getElementById('execution-mode').value,
  };
  try {
    const res = await fetch('/api/v1/executions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Execution failed');
    }
    output.textContent = data.output_text;
  } catch (err) {
    output.textContent = err.message;
  }
}
