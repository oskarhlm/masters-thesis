const socket = new WebSocket('ws://localhost:8080');

socket.onopen = (event) => {
  socket.send('Hello Server!');
};

socket.onmessage = (event) => {
  console.log('Message from server ', event.data);
};
