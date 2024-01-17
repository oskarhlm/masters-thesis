import './styles.css';
import ChatMessage from './ChatMessage';
import { For, onCleanup } from 'solid-js';
import { ChatElement } from './types';
import { MessageHeader } from './MessageHeader';
import Input from './Input';
import { chatElements } from './chatStore';
import { OpenInterpreter } from '../../api/openInterpreter';

const Chat = () => {
  let chatBottomRef: HTMLDivElement;

  function renderChatElement(el: ChatElement) {
    switch (el.type) {
      case 'message':
        console.log(el.message);
        return <ChatMessage message={el.message} source={el.source} />;
      case 'messageGroupHeader':
        return <MessageHeader source={el.source} />;
      default:
        break;
    }
  }

  // onCleanup(async () => {
  //   await OpenInterpreter.clearHistory();
  // });

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
