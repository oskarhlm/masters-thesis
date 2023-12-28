import styles from './styles.module.css';
import { OpenInterpreter, isStreaming } from '../../api/openInterpreter';
import { addChatMessage, addStreamingChatMessage } from './chatStore';
import { Component, createEffect } from 'solid-js';

type Props = {
  chatBottomRef: HTMLDivElement;
};

const Input: Component<Props> = (props) => {
  let submitBtnRef: HTMLInputElement;
  let textareaRef: HTMLTextAreaElement;

  let closeStream: () => void | undefined;

  async function sendMessage() {
    if (textareaRef.value.length === 0) return;

    addChatMessage(textareaRef.value, 'human');
    props.chatBottomRef?.scrollIntoView({
      behavior: 'smooth',
    });

    closeStream = await OpenInterpreter.chatStream(
      textareaRef.value,
      addStreamingChatMessage('bot', () => {
        props.chatBottomRef?.scrollIntoView({
          behavior: 'smooth',
        });
      })
    );

    textareaRef.value = '';
  }

  function terminateResponse() {
    if (!closeStream) {
      console.error('Termination function undefined');
      return;
    }

    closeStream();
  }

  createEffect(() => {
    const sendImageUrl = '/send-icon.png';
    const stopImageUrl = '/stop-icon.png';
    submitBtnRef.style.backgroundImage = `url('${
      isStreaming() ? stopImageUrl : sendImageUrl
    }')`;
  });

  return (
    <div class={styles['input-wrapper']}>
      <div class={styles['input-container']}>
        <textarea
          name="chat-input"
          id="chat-input"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              submitBtnRef.click();
            }
          }}
          ref={textareaRef!}
        />
        <input
          type="submit"
          value={''}
          ref={submitBtnRef!}
          onClick={() => {
            isStreaming() ? terminateResponse() : sendMessage();
          }}
        />
      </div>
    </div>
  );
};

export default Input;
