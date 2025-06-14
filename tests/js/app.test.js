// tests/js/app.test.js
// Mock the dependencies before requiring the app
jest.mock('express', () => {
  const mockExpress = jest.fn(() => ({
    use: jest.fn()
  }));
  mockExpress.static = jest.fn(() => 'static-middleware');
  return mockExpress;
});

jest.mock('socket.io', () => ({
  Server: jest.fn(() => ({
    on: jest.fn(),
    emit: jest.fn()
  }))
}));

jest.mock('stomp-client', () => jest.fn().mockImplementation(() => ({
  connect: jest.fn((successCallback) => {
    if (successCallback) successCallback('session-id');
    return Promise.resolve('session-id');
  }),
  subscribe: jest.fn()
})));

jest.mock('http', () => ({
  createServer: jest.fn(() => ({
    listen: jest.fn((port, callback) => {
      if (callback) callback();
      return this;
    })
  }))
}));

describe('App Configuration', () => {
  // Save original environment
  const originalEnv = process.env;

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();

    // Reset the environment
    process.env = { ...originalEnv };

    // Clear the module cache to ensure fresh imports
    jest.resetModules();
  });

  afterAll(() => {
    // Restore original environment
    process.env = originalEnv;
  });

  test('should use default values when environment variables are not set', () => {
    // Clear relevant environment variables
    delete process.env.ACTIVEMQ_HOST;
    delete process.env.ACTIVEMQ_PORT;
    delete process.env.ACTIVEMQ_DEST;
    delete process.env.ACTIVEMQ_USER;
    delete process.env.ACTIVEMQ_PASS;
    delete process.env.PORT;

    // Import the app
    const app = require('../../app');

    // Verify config has default values
    expect(app.config).toEqual({
      ACTIVEMQ_HOST: 'localhost',
      ACTIVEMQ_PORT: 61613,
      QUEUE: '/queue/test',
      USER: 'admin',
      PASS: 'admin',
      PORT: 3000
    });

    // Verify Stomp client was created with default values
    const StompMock = require('stomp-client');
    expect(StompMock).toHaveBeenCalledWith(
      'localhost',
      61613,
      'admin',
      'admin'
    );
  });

  test('should use environment variables when they are set', () => {
    // Set environment variables
    process.env.ACTIVEMQ_HOST = 'activemq-host';
    process.env.ACTIVEMQ_PORT = '1234';
    process.env.ACTIVEMQ_DEST = '/queue/custom';
    process.env.ACTIVEMQ_USER = 'user';
    process.env.ACTIVEMQ_PASS = 'pass';
    process.env.PORT = '8080';

    // Import the app
    const app = require('../../app');

    // Verify config has environment values
    expect(app.config).toEqual({
      ACTIVEMQ_HOST: 'activemq-host',
      ACTIVEMQ_PORT: 1234,
      QUEUE: '/queue/custom',
      USER: 'user',
      PASS: 'pass',
      PORT: '8080'
    });

    // Verify Stomp client was created with environment values
    const StompMock = require('stomp-client');
    expect(StompMock).toHaveBeenCalledWith(
      'activemq-host',
      1234,
      'user',
      'pass'
    );
  });
});
