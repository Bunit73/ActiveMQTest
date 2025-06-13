// tests/js/socket.test.js

// The mocks are automatically loaded from the __mocks__ directory
jest.mock('socket.io');
jest.mock('stomp-client');
jest.mock('http');
jest.mock('express');

describe('Socket.io Integration', () => {
  let app;
  let io;

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();

    // Clear the module cache to ensure fresh imports
    jest.resetModules();

    // Import the app
    app = require('../../app');
    io = app.io;
  });

  test('should set up Socket.io connection handler', () => {
    // Verify Socket.io connection handler was set up
    expect(io.on).toHaveBeenCalledWith('connection', expect.any(Function));
  });

  test('should handle Socket.io client connections and disconnections', () => {
    // Get the connection handler
    const connectionHandler = io.on.mock.calls[0][1];
    expect(connectionHandler).toBeDefined();

    // Create a mock socket
    const mockSocket = {
      id: 'socket-id',
      on: jest.fn()
    };

    // Simulate a client connection
    connectionHandler(mockSocket);

    // Verify disconnect handler was set up
    expect(mockSocket.on).toHaveBeenCalledWith('disconnect', expect.any(Function));
  });
});
