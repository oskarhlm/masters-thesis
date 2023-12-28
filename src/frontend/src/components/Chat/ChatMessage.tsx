import { Component, createMemo } from 'solid-js';
import './styles.css';

type Props = {
  message: string;
  source: 'human' | 'bot';
};

const ChatMessage: Component<Props> = (props) => {
  const parsedMessage = createMemo(() => {
    const segments = [];
    const regex = /```(\w*)\n([\s\S]*?)```/gs; // Updated regex
    let lastIndex = 0;

    props.message.replace(regex, (match, language, code, index) => {
      // Text before code block
      if (index > lastIndex) {
        segments.push(<span>{props.message.slice(lastIndex, index)}</span>);
      }
      // Code block - ignore 'language' if not needed
      segments.push(<pre>{code}</pre>);
      lastIndex = index + match.length;
      return match;
    });

    // Remaining text after the last code block
    if (lastIndex < props.message.length) {
      segments.push(<span>{props.message.slice(lastIndex)}</span>);
    }

    return segments;
  });

  return <p class={`message ${props.source}`}>{parsedMessage()}</p>;
};

export default ChatMessage;
