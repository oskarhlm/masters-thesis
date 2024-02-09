import { AgentType, ChatElement, MessageSource } from './types';
import { createStore } from 'solid-js/store';

export const [chatElements, setChatElements] = createStore<ChatElement[]>([
  { type: 'agentSelector', agentType: 'oaf' } satisfies ChatElement,
]);

function createUniqueId(): string {
  return `id-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

export function addChatMessage(
  message: string,
  source: MessageSource,
  id?: string
) {
  setChatElements([
    ...chatElements,
    {
      type: 'messageGroupHeader',
      source: source,
    },
    {
      type: 'message',
      id: id || createUniqueId(),
      source: source,
      message: message,
    },
  ] satisfies ChatElement[]);
}

export function addStreamingChatMessage(
  source: MessageSource,
  callback?: () => void
) {
  const messageId = createUniqueId();
  addChatMessage('', source, messageId);

  return (nextToken: string | undefined) => {
    if (nextToken) {
      setChatElements(
        (el) => el.type === 'message' && el.id === messageId,
        'message' as any,
        (msg) => msg + nextToken
      );
    }

    callback && callback();
  };
}
