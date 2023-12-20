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
      source: MessageSource;
    };
