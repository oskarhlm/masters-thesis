import { Component } from 'solid-js';
import styles from './styles.module.css';

type Props = {
  source: 'human' | 'bot';
};

export default function ChatMessage(props: Props) {
  const lorem =
    'Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptatibus, obcaecati!';
  const mesageLength = Math.floor(Math.random() * lorem.length);
  const message = lorem.slice(mesageLength);

  // const sourceClass = styles[`${props.source}`]

  return <p class={`${styles.message} ${styles[props.source]}`}>{message}</p>;
}
