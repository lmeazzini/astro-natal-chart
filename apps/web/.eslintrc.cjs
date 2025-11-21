module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    '@typescript-eslint/no-unused-vars': ['error', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_'
    }],
  },
  overrides: [
    {
      // Disable react-refresh/only-export-components for shadcn/ui components
      // These components intentionally export both components and variant configurations
      files: ['src/components/ui/**/*.tsx'],
      rules: {
        'react-refresh/only-export-components': 'off',
      },
    },
  ],
};
