import js from '@eslint/js';
import ts from 'typescript-eslint';

export default [
  {
    ignores: ['dist/**', 'node_modules/**', 'examples/**', '*.config.js'],
  },
  js.configs.recommended,
  ...ts.configs.recommended,
  {
    languageOptions: {
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
      },
      globals: {
        Buffer: 'readonly',
        process: 'readonly',
        crypto: 'readonly',
        TextEncoder: 'readonly',
        URL: 'readonly',
        URLSearchParams: 'readonly',
        fetch: 'readonly',
        console: 'readonly',
        Map: 'readonly',
        Promise: 'readonly',
        BufferSource: 'readonly',
        CryptoKey: 'readonly',
        globalThis: 'readonly',
      },
    },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      'no-console': 'off',
      'no-undef': 'off',
    },
  },
];
