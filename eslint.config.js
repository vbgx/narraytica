export default [
  {
    ignores: ["**/dist/**", "**/build/**", "**/.turbo/**", "**/node_modules/**"],
  },
  {
    files: ["**/*.js", "**/*.cjs", "**/*.mjs", "**/*.ts", "**/*.tsx"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
    },
    rules: {
      "no-unused-vars": "warn",
      "no-undef": "error"
    },
  },
];
