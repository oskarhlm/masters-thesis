import './styles.css';
import ChatMessage from './ChatMessage';
import { For } from 'solid-js';
import { ChatElement } from './types';
import { MessageHeader } from './MessageHeader';
import Input from './Input';
import { chatElements } from './chatStore';
import AgentSelector from './AgentSelector';
import InfoMessage from './InfoMessage';

const Chat = () => {
  let chatBottomRef: HTMLDivElement;

  function renderChatElement(el: ChatElement) {
    switch (el.type) {
      case 'agentSelector':
        return <AgentSelector />;
      case 'information':
        return <InfoMessage content={el.content} />;
      case 'message':
        return <ChatMessage message={el.message} source={el.source} />;
      case 'messageGroupHeader':
        return <MessageHeader source={el.source} />;
      default:
        break;
    }
  }

  return (
    <div class="chat">
      <div class="chat-messages">
        <For each={chatElements}>{renderChatElement}</For>
        <div ref={chatBottomRef!} />
      </div>
      <Input chatBottomRef={chatBottomRef!} />
    </div>
  );
};

export default Chat;
