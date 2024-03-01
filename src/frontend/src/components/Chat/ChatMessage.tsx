import { Component } from 'solid-js';
import showdown from 'showdown';
import './styles.css';

type Props = {
  message: string;
  source: 'human' | 'bot';
};

showdown.setFlavor('github');
const converter = new showdown.Converter();

const ChatMessage: Component<Props> = (props) => {
  return (
    <div
      class={`message ${props.source}`}
      innerHTML={converter.makeHtml(props.message)}
    />
  );
};

export default ChatMessage;
