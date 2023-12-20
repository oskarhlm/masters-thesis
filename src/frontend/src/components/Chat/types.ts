import { JSX } from 'solid-js/jsx-runtime';

export type Source = 'bot' | 'human';

export type Message = {
  source: Source;
  component: JSX.Element;
};

export type ChatMessageGroup = {
  source: Source;
  messageComponents: JSX.Element[];
};
