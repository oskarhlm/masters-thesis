import './App.css';
import Chat from './components/Chat';
import Map from './components/Map';

function App() {
  console.log('hei');
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
