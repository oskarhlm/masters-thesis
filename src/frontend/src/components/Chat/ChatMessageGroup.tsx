import { type ChatMessageGroup } from './types';
import { For } from 'solid-js';
import styles from './styles.module.css';

export default function ChatMessageGroup(props: ChatMessageGroup) {
  return (
    <div class="group">
      <p class={`${styles['group-header']} ${styles[props.source]}`}>
        {props.source}
      </p>
      <div class={styles['group-messages']}>
        <For each={props.messageComponents}>{(component) => component}</For>
      </div>
    </div>
  );
}
