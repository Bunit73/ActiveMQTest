const express = jest.fn(() => ({
  use: jest.fn()
}));

express.static = jest.fn(() => 'static-middleware');

module.exports = express;
