const socketIo = {
  Server: jest.fn(() => ({
    on: jest.fn(),
    emit: jest.fn()
  }))
};

module.exports = socketIo;
