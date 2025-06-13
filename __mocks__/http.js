// Create a mock server that doesn't actually listen on a port
const mockServer = {
  listen: jest.fn((port, callback) => {
    // Just call the callback without actually listening
    if (callback) callback();
    return mockServer;
  })
};

const http = {
  createServer: jest.fn(() => mockServer)
};

module.exports = http;
