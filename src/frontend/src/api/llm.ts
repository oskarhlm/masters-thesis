import { createSignal } from 'solid-js';
import { get, BASE_URL, post } from './apiHelper';
import { addGeoJSONToMap } from '../components/Map/Map';
import { AgentType } from '../components/Chat/types';
import { updateMapState } from './mapState';

export const [isStreaming, setIsStreaming] = createSignal(false);
export const [sessionId, setSessionId] = createSignal<string | null>(null);

export class LLM {
  static async chatStream(
    message: string,
    onMessageCallback: (
      message: string | undefined,
      messageEnd?: boolean
    ) => void
  ) {
    const eventSource = new EventSource(
      `${BASE_URL}/streaming-chat?message=${message}`
    );

    setIsStreaming(true);

    const closeStream = async () => {
      console.log('Closing the stream.');
      eventSource.close();
      setIsStreaming(false);
      updateMapState();
    };

    eventSource.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      if (data.stream_complete) {
        closeStream();
      }

      if (data.geojson_path) {
        console.log(data.layer_name);
        const res = await get('/geojson', {
          geojson_path: data.geojson_path,
        });
        addGeoJSONToMap(res, data.layer_name);
      }

      if (data.message_end) {
        onMessageCallback(undefined, true);
        return;
      }

      onMessageCallback(data.message);
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      closeStream();
    };

    return closeStream;
  }

  static async getSession(sessionId: string) {
    try {
      const response = await get('/session', {
        session_id: sessionId,
      });
      return response;
    } catch (error) {
      console.error('Error in LLMInterpreter.chat:', error);
      throw error;
    }
  }

  static async createSession(agentType: AgentType) {
    setSessionId(null);
    try {
      const response = await post('/session', {
        agent_type: agentType,
      });
      console.log(response);
      setSessionId(response.session_id);
      return response;
    } catch (error) {
      console.error('Error in OpenInterpreter.chat:', error);
      throw error;
    }
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
