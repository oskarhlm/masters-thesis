import { Component } from 'solid-js';
import styles from './styles.module.css';

type Props = {
  message: string;
  source: 'human' | 'bot';
};

const ChatMessage: Component<Props> = (props) => {
  return (
    <p class={`${styles.message} ${styles[props.source]}`}>{props.message}</p>
  );
};

export default ChatMessage;
