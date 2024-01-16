import { createSignal } from 'solid-js';
import { get, BASE_URL, del } from './apiHelper';

export const [isStreaming, setIsStreaming] = createSignal(false);

export class OpenInterpreter {
  static async chatStream(
    message: string,
    onMessageCallback: (message: string) => void
  ) {
    const eventSource = new EventSource(`${BASE_URL}/streaming-chat?message=${message}`);

    setIsStreaming(true);

    const closeStream = () => {
      console.log('Closing the stream.');
      eventSource.close();
      setIsStreaming(false);
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.stream_complete) {
        closeStream();
      }

      onMessageCallback(data.message);
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      closeStream();
    };

    return closeStream;
  }

  static async history() {
    try {
      const response = await get('/history');
      return response;
    } catch (error) {
      console.error('Error in OpenInterpreter.chat:', error);
      throw error;
    }
  }

  static async clearHistory() {
    try {
      const response = await del('/history');
      return response;
    } catch (error) {
      console.error('Could not delete history stored on server:', error);
      throw error;
    }
  }

  static async uploadFiles(
    files: File[],
    onMessageCallback?: (message: string) => void
  ) {
    if (!files.length) return;

    let formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    formData.append(
      'should_respond',
      (onMessageCallback !== undefined).toString()
    );

    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${BASE_URL}/upload`, true);
    xhr.setRequestHeader('Accept', 'text/event-stream');

    let seenBytes = 0;

    xhr.onreadystatechange = () => {
      if (xhr.readyState >= 3 && onMessageCallback) {
        const data = xhr.responseText.substring(seenBytes);
        data
          .split('\n\n')
          .filter((d) => d.length)
          .map((d) => JSON.parse(d.trim().replace('data:', '')))
          .forEach((d) => onMessageCallback(d.message));
        seenBytes = xhr.responseText.length;
      }
    };

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        console.log(`Received ${event.loaded} of ${event.total} bytes`);
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        console.log('Upload complete');
      } else {
        console.error('Upload failed');
      }
    };

    xhr.send(formData);
  }
}
