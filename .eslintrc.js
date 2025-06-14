module.exports = {
  env: {
    browser: true,
    commonjs: true,
    es2021: true,
    node: true
  },
  extends: [
    'standard',
    'eslint:recommended'
  ],
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
        jest: 'readonly',
        it: 'readonly',
        xit: 'readonly',
        fit: 'readonly'
      }
    }
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    // Custom rules can be added here
    semi: ['error', 'always'],
    'no-unused-vars': 'warn',
    'no-console': 'warn',
    'prefer-const': 'error',
    'arrow-body-style': ['error', 'as-needed'],
    'no-var': 'error',
    'object-shorthand': ['error', 'always'],
    'prefer-template': 'error',
    'no-multiple-empty-lines': ['error', { max: 1, maxEOF: 1 }],
    'eol-last': ['error', 'always'],
    'quote-props': ['error', 'as-needed']
  },
  ignorePatterns: [
    'node_modules/',
    'public/javascripts/vendor/',
    'htmlcov/',
    'coverage/',
    '.venv/'
  ]
};
