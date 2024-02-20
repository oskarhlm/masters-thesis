import { Component, For, createEffect, createSignal, onMount } from 'solid-js';
import './styles.css';
import { AgentType, agentTypesArray } from './types';
import { chatElements } from './chatStore';
import { LLM } from '../../api/llm';

export const [selectedAgentType, setSelectedAgentType] =
  createSignal<AgentType>(
    (sessionStorage.getItem('agentType') as AgentType) || agentTypesArray[0]
  );

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

  onMount(() => {
    console.log(selectedAgentType());
  });

  createEffect(() => {
    LLM.createSession(selectedAgentType());
  });

  return (
    <div class="agent-select-wrapper">
      <select
        name="agent-selector"
        id="agent-selector"
        disabled={chatElements.length > 1}
        onchange={(e) => {
          const agentType = e.target.value as AgentType;
          sessionStorage.setItem('agentType', agentType);
          setSelectedAgentType(agentType);
        }}
      >
        <For each={agentTypesArray}>
          {(agentType, _) => (
            <option
              value={agentType}
              selected={agentType === selectedAgentType()}
            >
              {agentTypeToHumanReadable(agentType)}
            </option>
          )}
        </For>
      </select>
    </div>
  );
};

export default AgentSelector;
