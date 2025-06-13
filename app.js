// app.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const Stomp = require('stomp-client');

const ACTIVEMQ_HOST = process.env.ACTIVEMQ_HOST || 'localhost';
const ACTIVEMQ_PORT = parseInt(process.env.ACTIVEMQ_PORT || '61613');
const QUEUE = process.env.ACTIVEMQ_DEST || '/queue/test';
const USER = process.env.ACTIVEMQ_USER || 'admin';
const PASS = process.env.ACTIVEMQ_PASS || 'admin';

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Serve any static assets from /public
app.use(express.static('public'));

// Set up STOMP client
const stompClient = new Stomp(
  ACTIVEMQ_HOST,
  ACTIVEMQ_PORT,
  USER,
  PASS
);

// Connect and subscribe
stompClient.connect(
  (sessionId) => {
    console.log('Connected to ActiveMQ, session:', sessionId);
    stompClient.subscribe(QUEUE, (body, headers) => {
      console.log('Received from ActiveMQ:', body);
      io.emit('activemq-message', body);
    });
  },
  (error) => {
    console.error('STOMP error:', error);
  }
);

// Handle WebSocket connections
io.on('connection', (socket) => {
  console.log('Web client connected:', socket.id);
  socket.on('disconnect', () => {
    console.log('Web client disconnected:', socket.id);
  });
});

// Start HTTP + Socket.io server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
