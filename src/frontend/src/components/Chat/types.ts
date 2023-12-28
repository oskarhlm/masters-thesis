export type MessageSource = 'bot' | 'human';

export type ChatElement =
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
