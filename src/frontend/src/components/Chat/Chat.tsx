import styles from './styles.module.css';
import ChatMessage from './ChatMessage';
import { For, JSX, onMount, createSignal } from 'solid-js';
import { Source, Message, type ChatMessageGroup } from './types';
import ChatMessageGroupComponent from './ChatMessageGroup';

export default function Chat() {
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
    const messages: Message[] = Array.from({ length: 20 }, () => {
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
          // <div>
          //   <For each={group.messageComponents}>{(component) => component}</For>
          // </div>
          <ChatMessageGroupComponent
            source={group.source}
            messageComponents={group.messageComponents}
          />
        )}
      </For>
    </div>
  );
}
