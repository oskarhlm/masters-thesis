import { Component, For, createEffect, createSignal, onMount } from 'solid-js';
import './styles.css';
import { AgentType, agentTypesArray } from './types';
import { chatElements, setChatElements } from './chatStore';
import { LLM } from '../../api/llm';

export const [selectedAgentType, setSelectedAgentType] =
  createSignal<AgentType>(
    (sessionStorage.getItem('agentType') as AgentType) || agentTypesArray[0]
  );

const AgentSelector: Component = () => {
  function agentTypeToHumanReadable(agentType: AgentType) {
    switch (agentType) {
      case 'python':
        return 'Python Agent';
      case 'sql':
        return 'SQL Agent';
      case 'oaf':
        return 'OGC API Features Agent';
      case 'lg-agent-supervisor':
        return 'Agent Supervisor Pattern';
      default:
        break;
    }
  }

  onMount(() => addAgentTypeInformationMessage(selectedAgentType()));

  function addAgentTypeInformationMessage(agentType: AgentType) {
    if (agentType === 'lg-agent-supervisor') {
      setChatElements([
        ...chatElements,
        {
          type: 'information',
          content: (
            <>
              <i>{'Agent Supervisor Pattern'}</i> does not support token
              streaming.
            </>
          ),
        },
      ]);
    }
  }

  createEffect(() => {
    LLM.createSession(selectedAgentType());
  });

  return (
    <div class="agent-select-wrapper">
      <select
        name="agent-selector"
        id="agent-selector"
        disabled={chatElements.filter((el) => el.type === 'message').length > 0}
        onchange={(e) => {
          const agentType = e.target.value as AgentType;
          sessionStorage.setItem('agentType', agentType);
          setSelectedAgentType(agentType);
          addAgentTypeInformationMessage(agentType);
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
