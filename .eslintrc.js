module.exports = {
  env: {
    browser: true,
    commonjs: true,
    es2021: true,
    node: true
  },
  extends: 'standard',
  overrides: [
    {
      env: {
        node: true
      },
      files: [
        '.eslintrc.{js,cjs}'
      ],
      parserOptions: {
        sourceType: 'script'
      }
    },
    {
      files: [
        'tests/**/*.js',
        '__mocks__/**/*.js'
      ],
      env: {
        jest: true
      },
      globals: {
        describe: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
        jest: 'readonly'
      }
    }
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    // Custom rules can be added here
    semi: ['error', 'always'],
    'no-unused-vars': 'warn'
  },
  ignorePatterns: [
    'node_modules/',
    'public/javascripts/vendor/',
    'htmlcov/',
    'coverage/'
  ]
};
