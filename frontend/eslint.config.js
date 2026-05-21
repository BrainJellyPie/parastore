import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import reactCompiler from "eslint-plugin-react-compiler";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";

export default tseslint.config(
  { ignores: ["dist", "node_modules", "public"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { ...globals.browser, ...globals.es2022 },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_", caughtErrorsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
  // React Compiler excludes the same file list as REACT_COMPILER_EXCLUDES in vite.config.ts.
  // Only components that use R3F hooks (useFrame/useLoader/useGLTF/useAnimations).
  {
    files: ["src/**/*.{ts,tsx}"],
    ignores: [
      "src/views/simulation/SimulationLayout.tsx",
      "src/features/playback/components/PlaybackScene.tsx",
      "src/features/playback/components/PersonaView.tsx",
      "src/features/playback/hooks/useSimulationLoop.ts",
      "src/features/store-viewer/components/SolidFloor.tsx",
      "src/features/store-viewer/components/AssetWall.tsx",
      "src/features/store-viewer/components/AssetRug.tsx",
      "src/features/store-viewer/components/AssetFixture.tsx",
      "src/features/store-viewer/components/AssetPersona.tsx",
      "src/shared/hooks/useGlbModel.ts",
    ],
    plugins: { "react-compiler": reactCompiler },
    rules: {
      "react-compiler/react-compiler": "warn",
    },
  },
);
