// app.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const Stomp = require('stomp-client');

// Configuration with defaults
const config = {
  ACTIVEMQ_HOST: process.env.ACTIVEMQ_HOST || 'localhost',
  ACTIVEMQ_PORT: parseInt(process.env.ACTIVEMQ_PORT || '61613'),
  QUEUE: process.env.ACTIVEMQ_DEST || '/queue/test', // Legacy queue for backward compatibility
  SDR_QUEUE: process.env.ACTIVEMQ_SDR_DEST || '/queue/sdr',
  PUBLISHER_QUEUE: process.env.ACTIVEMQ_PUBLISHER_DEST || '/queue/publisher',
  USER: process.env.ACTIVEMQ_USER || 'admin',
  PASS: process.env.ACTIVEMQ_PASS || 'admin',
  PORT: process.env.PORT || 3000
};

// Store the most recent messages
let latestSdrMessage = null;
let latestPublisherMessage = null;

// Create Express app
const app = express();

// Create HTTP server
const server = http.createServer(app);

// Create Socket.io server
const io = new Server(server);

// Serve any static assets from /public
app.use(express.static('public'));

// Add a route for the root path
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>ActiveMQ Test</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; text-align: center; }
        h1 { color: #333; }
        .btn { display: inline-block; padding: 10px 20px; margin: 10px; 
              background-color: #4CAF50; color: white; text-decoration: none; 
              border-radius: 5px; }
      </style>
    </head>
    <body>
      <h1>ActiveMQ Test Application</h1>
      <p>Welcome to the ActiveMQ test application.</p>
      <a href="/latest-view" class="btn">View Latest Messages</a>
    </body>
    </html>
  `);
});

// Add a route to display the latest messages as JSON
app.get('/latest', (req, res) => {
  res.json({
    sdr: latestSdrMessage,
    publisher: latestPublisherMessage
  });
});

// Add a route to display the latest messages in a user-friendly way
app.get('/latest-view', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Latest Messages</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .message-container { margin-bottom: 20px; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .refresh-btn { padding: 10px; background-color: #4CAF50; color: white; border: none; 
                      border-radius: 5px; cursor: pointer; margin-bottom: 20px; }
        .timestamp { color: #666; font-style: italic; }
      </style>
    </head>
    <body>
      <h1>Latest Messages from ActiveMQ</h1>
      <button class="refresh-btn" onclick="fetchLatestMessages()">Refresh Messages</button>

      <div class="message-container">
        <h2>Latest SDR Message</h2>
        <div id="sdr-timestamp" class="timestamp"></div>
        <pre id="sdr-message">Loading...</pre>
      </div>

      <div class="message-container">
        <h2>Latest Publisher Message</h2>
        <div id="publisher-timestamp" class="timestamp"></div>
        <pre id="publisher-message">Loading...</pre>
      </div>

      <script>
        // Function to fetch and display the latest messages
        function fetchLatestMessages() {
          fetch('/latest')
            .then(response => response.json())
            .then(data => {
              // Update SDR message
              if (data.sdr) {
                document.getElementById('sdr-message').textContent = 
                  JSON.stringify(data.sdr, null, 2);
                document.getElementById('sdr-timestamp').textContent = 
                  'Timestamp: ' + new Date(data.sdr.timestamp * 1000).toLocaleString();
              } else {
                document.getElementById('sdr-message').textContent = 'No message received yet';
                document.getElementById('sdr-timestamp').textContent = '';
              }

              // Update Publisher message
              if (data.publisher) {
                document.getElementById('publisher-message').textContent = data.publisher;
                document.getElementById('publisher-timestamp').textContent = 
                  'Received: ' + new Date().toLocaleString();
              } else {
                document.getElementById('publisher-message').textContent = 'No message received yet';
                document.getElementById('publisher-timestamp').textContent = '';
              }
            })
            .catch(error => {
              console.error('Error fetching latest messages:', error);
            });
        }

        // Fetch messages when the page loads
        fetchLatestMessages();

        // Refresh messages every 5 seconds
        setInterval(fetchLatestMessages, 5000);
      </script>
    </body>
    </html>
  `);
});

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

        // Subscribe to SDR queue
        stompClient.subscribe(config.SDR_QUEUE, (body, headers) => {
          console.log('Received from SDR queue:', body);

          try {
            const jsonMessage = JSON.parse(body);
            if (jsonMessage.spectrum_db) {
              latestSdrMessage = jsonMessage;
              console.log('Updated latest SDR message');
              io.emit('sdr-message', jsonMessage);
            }
          } catch (e) {
            console.error('Error parsing SDR message:', e);
          }
        });

        // Subscribe to Publisher queue
        stompClient.subscribe(config.PUBLISHER_QUEUE, (body, headers) => {
          console.log('Received from Publisher queue:', body);

          if (typeof body === 'string' && body.includes('T') && body.endsWith('Z')) {
            latestPublisherMessage = body;
            console.log('Updated latest publisher message');
            io.emit('publisher-message', body);
          }
        });

        // For backward compatibility, also subscribe to the legacy queue
        stompClient.subscribe(config.QUEUE, (body, headers) => {
          console.log('Received from legacy queue:', body);

          // Try to determine the message type and handle accordingly
          try {
            const jsonMessage = JSON.parse(body);
            if (jsonMessage.spectrum_db) {
              latestSdrMessage = jsonMessage;
              console.log('Updated latest SDR message from legacy queue');
              io.emit('sdr-message', jsonMessage);
            }
          } catch (e) {
            // If it's not JSON, check if it's a timestamp from publisher.py
            if (typeof body === 'string' && body.includes('T') && body.endsWith('Z')) {
              latestPublisherMessage = body;
              console.log('Updated latest publisher message from legacy queue');
              io.emit('publisher-message', body);
            }
          }

          // Also emit the generic message event for backward compatibility
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
