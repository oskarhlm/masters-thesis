import styles from './styles.module.css';
import ChatMessage from './ChatMessage';
import { For, createSignal, onMount } from 'solid-js';
import { ChatElement, MessageSource } from './types';
import { MessageHeader } from './MessageHeader';
import { Input } from './Input';

export default function Chat() {
  const [chatElements, setChatElements] = createSignal<ChatElement[]>([]);

  function initializeChatElements() {
    // const chatElements: ChatElement[] = Array.from({ length: 20 }, () => {
    //   const source: MessageSource =
    //     Math.round(Math.random()) === 0 ? 'bot' : 'human';
    //   return {
    //     type: 'message',
    //     source: source,
    //   };
    // });

    const chatElements: ChatElement[] = [];
    let prevSource: MessageSource | undefined;
    for (let i = 0; i < 20; i++) {
      const source: MessageSource =
        Math.round(Math.random()) === 0 ? 'bot' : 'human';

      if (source !== prevSource) {
        chatElements.push({
          type: 'messageGroupHeader',
          source: source,
        });

        prevSource = source;
      }

      chatElements.push({
        type: 'message',
        source: source,
      });
    }

    return chatElements;
  }

  onMount(() => {
    setChatElements(initializeChatElements());
  });

  function renderChatElement(el: ChatElement) {
    switch (el.type) {
      case 'message':
        return <ChatMessage source={el.source} />;
      case 'messageGroupHeader':
        return <MessageHeader source={el.source} />;
      default:
        break;
    }
  }

  return (
    <div class={styles.chat}>
      <div class={styles['chat-messages']}>
        <For each={chatElements()}>{renderChatElement}</For>
      </div>
      <Input />
    </div>
  );
}
