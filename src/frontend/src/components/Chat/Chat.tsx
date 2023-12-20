import styles from './styles.module.css';
import ChatMessage from './ChatMessage';
import { For, JSX, onMount, createSignal } from 'solid-js';
import { Source } from './types';

export default function Chat() {
  // const messages = Array.from({ length: 10 }, () => (
  //   <ChatMessage source={Math.round(Math.random()) === 0 ? 'bot' : 'human'} />
  // ));

  type Message = {
    source: Source;
    component: JSX.Element;
  };

  type ChatMessageGroup = {
    source: Source;
    messageComponents: JSX.Element[];
  };

  const [groups, setGroups] = createSignal<ChatMessageGroup[]>([]);

  function addMessageToChat(message: Message) {
    const lastMessageSource: Source | undefined =
      groups()[groups().length - 1]?.source;
    console.log(lastMessageSource);

    if (!lastMessageSource) {
      setGroups([
        {
          source: message.source,
          messageComponents: [message.component],
        },
      ]);
      return;
    }

    if (message.source !== lastMessageSource) {
      setGroups([
        ...groups(),
        {
          source: message.source,
          messageComponents: [message.component],
        },
      ]);
    } else {
      groups()[groups().length - 1].messageComponents.push(message.component);
    }
  }

  onMount(() => {
    const messages: Message[] = Array.from({ length: 10 }, () => {
      const source: Source = Math.round(Math.random()) === 0 ? 'bot' : 'human';
      return {
        source: source,
        component: <ChatMessage source={source} />,
      };
    });

    messages.forEach((msg) => addMessageToChat(msg));
    console.log(groups());
  });

  return (
    <div class={styles.chat}>
      <For each={groups()}>
        {(group) => (
          <div>
            <For each={group.messageComponents}>{(component) => component}</For>
          </div>
        )}
      </For>
    </div>
  );
}
