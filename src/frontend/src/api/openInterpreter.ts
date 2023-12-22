import { get, BASE_URL } from './apiHelper';

export class OpenInterpreter {
  static async chatStream(
    message: string,
    onMessageCallback: (message: string) => void
  ) {
    const eventSource = new EventSource(`${BASE_URL}/chat?message=${message}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessageCallback(data);
      if (data.end_of_message) {
        eventSource.close();
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
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
}
