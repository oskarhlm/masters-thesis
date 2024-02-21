import './styles.css';
import { LLM, isStreaming, sessionId } from '../../api/llm';
import { addChatMessage, addStreamingChatMessage } from './chatStore';
import {
  Component,
  For,
  JSX,
  Show,
  createEffect,
  createSignal,
} from 'solid-js';
import { removeIndex } from '../../utils/listUtils';

type Props = {
  chatBottomRef: HTMLDivElement;
};

const Input: Component<Props> = (props) => {
  let submitBtnRef: HTMLInputElement;
  let textareaRef: HTMLTextAreaElement;

  let closeStream: (() => void) | undefined;

  const [files, setFiles] = createSignal<File[]>([]);

  async function sendMessage() {
    if (files().length) {
      await LLM.uploadFiles(
        files(),
        !textareaRef.value.length
          ? addStreamingChatMessage('bot', () => {
              props.chatBottomRef?.scrollIntoView({
                behavior: 'smooth',
              });
            })
          : undefined
      );

      setFiles([]);
    }

    if (textareaRef.value.length === 0) return;
    const humanMessage = textareaRef.value;

    addChatMessage(humanMessage, 'human');
    props.chatBottomRef?.scrollIntoView({
      behavior: 'smooth',
    });

    textareaRef.value = '';

    closeStream = await LLM.chatStream(
      humanMessage,
      addStreamingChatMessage('bot', () => {
        props.chatBottomRef?.scrollIntoView({
          behavior: 'smooth',
        });
      })
    );
  }

  const handleFileUpload: JSX.EventHandler<HTMLInputElement, InputEvent> = (
    event
  ) => {
    setFiles([...files(), ...Array.from(event.currentTarget.files!)]);
  };

  function removeFile(fileIndex: number) {
    const newFileList = removeIndex(files(), fileIndex);
    setFiles(newFileList);
  }

  createEffect(() => {
    const sendImageUrl = '/send-icon.png';
    const stopImageUrl = '/stop-icon.png';
    submitBtnRef.style.backgroundImage = `url('${
      isStreaming() ? stopImageUrl : sendImageUrl
    }')`;
  });

  return (
    <div class="input-wrapper">
      <Show when={files().length > 0}>
        <ul>
          <For each={files()}>
            {(file, index) => (
              <li>
                <span>
                  <button onclick={() => removeFile(index())}>
                    <img src="/delete-icon.png" alt="Delete" />
                  </button>
                  {file.name}
                </span>
              </li>
            )}
          </For>
        </ul>
      </Show>
      <div class="input-container">
        <label for="file-upload">
          <img src="/file-icon.png" alt="Upload file" />
        </label>
        <input
          type="file"
          id="file-upload"
          onInput={handleFileUpload}
          multiple
        />
        <hr />
        <textarea
          name="chat-input"
          id="chat-input"
          onkeydown={(e) => {
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
          onclick={() => {
            isStreaming() ? closeStream!() : sendMessage();
          }}
        />
      </div>
    </div>
  );
};

export default Input;
