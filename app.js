// app.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const Stomp = require('stomp-client');

// Configuration with defaults
const config = {
  ACTIVEMQ_HOST: process.env.ACTIVEMQ_HOST || 'localhost',
  ACTIVEMQ_PORT: parseInt(process.env.ACTIVEMQ_PORT || '61613'),
  QUEUE: process.env.ACTIVEMQ_DEST || '/queue/test',
  USER: process.env.ACTIVEMQ_USER || 'admin',
  PASS: process.env.ACTIVEMQ_PASS || 'admin',
  PORT: process.env.PORT || 3000
};

// Create Express app
const app = express();

// Create HTTP server
const server = http.createServer(app);

// Create Socket.io server
const io = new Server(server);

// Serve any static assets from /public
app.use(express.static('public'));

// Create STOMP client
const stompClient = new Stomp(
  config.ACTIVEMQ_HOST,
  config.ACTIVEMQ_PORT,
  config.USER,
  config.PASS
);

// Function to connect to ActiveMQ
function connectToActiveMQ () {
  return new Promise((resolve, reject) => {
    stompClient.connect(
      (sessionId) => {
        console.log('Connected to ActiveMQ, session:', sessionId);
        stompClient.subscribe(config.QUEUE, (body, headers) => {
          console.log('Received from ActiveMQ:', body);
          io.emit('activemq-message', body);
        });
        resolve(sessionId);
      },
      (error) => {
        console.error('STOMP error:', error);
        reject(error);
      }
    );
  });
}

// Handle WebSocket connections
io.on('connection', (socket) => {
  console.log('Web client connected:', socket.id);
  socket.on('disconnect', () => {
    console.log('Web client disconnected:', socket.id);
  });
});

// Function to start the server
function startServer () {
  return new Promise((resolve) => {
    server.listen(config.PORT, () => {
      console.log(`Server running at http://localhost:${config.PORT}`);
      resolve(server);
    });
  });
}

// Start the server if this file is run directly
if (require.main === module) {
  connectToActiveMQ()
    .then(() => startServer())
    .catch(err => {
      console.error('Failed to start:', err);
      process.exit(1);
    });
}

// Export for testing
module.exports = {
  app,
  server,
  io,
  stompClient,
  config,
  connectToActiveMQ,
  startServer
};
