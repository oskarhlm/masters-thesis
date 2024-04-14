import { JSX } from 'solid-js/jsx-runtime';

export type MessageSource = 'bot' | 'human';

export const agentTypesArray = ['python', 'sql', 'oaf', 'lg-agent-supervisor'] as const;

export type AgentType = (typeof agentTypesArray)[number];

export type ChatElement =
  | {
      type: 'agentSelector';
      agentType: AgentType;
    }
  | {
      type: 'dateHeader';
      date: Date;
    }
  | {
      type: 'messageGroupHeader';
      source: MessageSource;
    }
  | {
      type: 'message';
      id: string;
      source: MessageSource;
      message: string;
    }
  | {
      type: 'information';
      content: string | JSX.Element;
    }
  | {
      type: 'spinner';
      content?: string | JSX.Element;
    }
  | {
      type: 'tool';
      toolName: string;
      runId: string;
      input?: string | null;
      output?: string | null;
    };
