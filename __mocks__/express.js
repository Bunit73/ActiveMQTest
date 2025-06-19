const express = jest.fn(() => ({
  use: jest.fn(),
  get: jest.fn()
}));

express.static = jest.fn(() => 'static-middleware');

module.exports = express;
