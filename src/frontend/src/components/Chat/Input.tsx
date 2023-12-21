import styles from './styles.module.css';

export function Input() {
  let submitBtnRef: HTMLInputElement;
  let textareaRef: HTMLTextAreaElement;

  function sendMessage() {
    textareaRef.value = '';
  }

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
          onClick={sendMessage}
        />
      </div>
    </div>
  );
}
