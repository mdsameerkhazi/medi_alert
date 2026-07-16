# Local Setup & Project Configuration

To run CareConnect locally, follow these steps to ensure your environment is configured correctly.

## 1. Prerequisites
- **Node.js**: (LTS version recommended)
- **npm** or **yarn**
- **Expo CLI**: `npm install -g expo-cli` (Recommended for rapid mobile prototyping)

## 2. Installation
```bash
# Install dependencies
npm install

# Initialize Tailwind (NativeWind)
npx tailwindcss init
```

## 3. Project Structure
Ensure your local folder matches the architecture defined in the project:
- `/src/components`: Place for predicted components (TopAppBar, BottomNavBar).
- `/src/screens`: All generated screens (Dashboard, Medication, etc.).
- `/src/store`: Zustand configuration (`useAppStore.ts`).
- `/src/services`: Mock API files.

## 4. Running the App
```bash
# Start the development server
npm run start

# Run on Web (localhost)
npm run web
```

## 5. Required Configuration Files
- **tailwind.config.js**: Configure your content paths to include `./src/**/*.{js,jsx,ts,tsx}`.
- **tsconfig.json**: Ensure strict typing for the established interfaces.
- **babel.config.js**: Include the `nativewind/babel` plugin.

## 6. Development Notes
- The app uses **Zustand** for global state (Auth, SOS, Vitals).
- **NativeWind** handles the "Clinical Clarity" design system tokens via Tailwind utility classes.
- Navigation is handled by **React Navigation** (Stack and Tab navigators).