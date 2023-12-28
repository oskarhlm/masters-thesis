import { createSignal } from 'solid-js';
import { get, BASE_URL, del } from './apiHelper';

export const [isStreaming, setIsStreaming] = createSignal(false);

export class OpenInterpreter {
  static async chatStream(
    message: string,
    onMessageCallback: (message: string) => void
  ) {
    const eventSource = new EventSource(`${BASE_URL}/chat?message=${message}`);

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
}
