export type MessageSource = 'bot' | 'human';

export const agentTypesArray = ['sql', 'oaf'] as const;

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
    };
