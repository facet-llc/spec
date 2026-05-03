import js from '@eslint/js';
import ts from 'typescript-eslint';
import security from 'eslint-plugin-security';

export default [
  {
    ignores: ['dist/**', 'node_modules/**', 'examples/**', '*.config.js'],
  },
  js.configs.recommended,
  ...ts.configs.recommended,
  security.configs.recommended,
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
        Response: 'readonly',
        AbortController: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        globalThis: 'readonly',
      },
    },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      'no-console': 'off',
      'no-undef': 'off',
      // Tuned for SDK code: object-injection rule false-positives on
      // typed property access; dropped because all object reads here go
      // through validated keys (kid, iss, etc.).
      'security/detect-object-injection': 'off',
    },
  },
  {
    // Test files legitimately read conformance vectors by path.
    files: ['test/**/*.ts'],
    rules: {
      'security/detect-non-literal-fs-filename': 'off',
    },
  },
];
