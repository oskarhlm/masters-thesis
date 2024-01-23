import { onMount } from 'solid-js';
import './App.css';
import Chat from './components/Chat';
import Map from './components/Map';
import { LLMInterpreter } from './api/openInterpreter';

function App() {
  onMount(() => {
    LLMInterpreter.createSession();
  });

  return (
    <>
      <div class="chat-map-wrapper">
        <Chat />
        <Map />
      </div>
    </>
  );
}

export default App;
