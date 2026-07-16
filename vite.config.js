import { defineConfig } from 'vite';
import fs from 'fs';
import path from 'path';

export default defineConfig({
  plugins: [
    {
      name: 'copy-screens',
      closeBundle() {
        const rootDir = path.resolve(__dirname);
        const distDir = path.resolve(rootDir, 'dist');

        // Read all items in the root directory
        const items = fs.readdirSync(rootDir);

        items.forEach((item) => {
          // Ignore standard non-screen folders
          if (['dist', 'node_modules', '.git', '.expo', '.gemini', 'backend'].includes(item)) {
            return;
          }

          const srcDir = path.resolve(rootDir, item);
          const stat = fs.statSync(srcDir);

          if (stat.isDirectory()) {
            // Check if it contains a screen file (code.html)
            const codeHtmlPath = path.resolve(srcDir, 'code.html');
            if (fs.existsSync(codeHtmlPath)) {
              const destDir = path.resolve(distDir, item);
              fs.mkdirSync(destDir, { recursive: true });
              fs.cpSync(srcDir, destDir, { recursive: true });
              console.log(`Copied screen folder "${item}" to dist/${item}`);
            }
          }
        });
      }
    }
  ]
});
