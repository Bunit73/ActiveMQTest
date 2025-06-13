const StompClient = jest.fn().mockImplementation(() => ({
  connect: jest.fn((callback, errorCallback) => {
    if (callback) callback(null, 'session-id');
  }),
  subscribe: jest.fn((queue, callback) => {
    // Store the callback so we can call it in tests
    StompClient.subscribeCallback = callback;
  })
}));

// Add a property to store the subscribe callback
StompClient.subscribeCallback = null;

module.exports = StompClient;
