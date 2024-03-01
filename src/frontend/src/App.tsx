import { onMount, onCleanup } from 'solid-js';
import './App.css';
import Chat from './components/Chat';
import Map from './components/Map';
import { del } from './api/apiHelper';

function App() {
  onCleanup(() => {
    del('clear-workdir');
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
