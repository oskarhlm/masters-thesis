import { Component, For, createEffect, createSignal } from 'solid-js';
import './styles.css';
import { AgentType, agentTypesArray } from './types';
import { chatElements } from './chatStore';
import { LLMInterpreter } from '../../api/llmInterpreter';

export const [selectedAgentType, setSelectedAgentType] =
  createSignal<AgentType>(agentTypesArray[0]);

const AgentSelector: Component = () => {
  function agentTypeToHumanReadable(agentType: AgentType) {
    switch (agentType) {
      case 'sql':
        return 'SQL Agent';
      case 'oaf':
        return 'OGC API Features Agent';
      default:
        break;
    }
  }

  createEffect(() => {
    LLMInterpreter.createSession(selectedAgentType());
  });

  return (
    <div class="agent-select-wrapper">
      <select
        name="agent-selector"
        id="agent-selector"
        disabled={chatElements.length > 1}
        onchange={(e) => setSelectedAgentType(e.target.value as AgentType)}
      >
        <For each={agentTypesArray}>
          {(agentType, _) => (
            <option value={agentType}>
              {agentTypeToHumanReadable(agentType)}
            </option>
          )}
        </For>
      </select>
    </div>
  );
};

export default AgentSelector;
