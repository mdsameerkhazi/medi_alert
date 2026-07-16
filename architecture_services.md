# Project Architecture & Logic: CareConnect

## 1. Folder Structure
```text
src/
├── assets/          # Images, Icons, Fonts
├── components/      # Reusable UI Components
│   ├── common/      # Button, Input, Card, Loading, EmptyState
│   ├── layout/      # TopAppBar, BottomNavBar
│   └── feature/     # SOSButton, ProgressIndicator
├── navigation/      # React Navigation configuration
│   ├── AuthStack.tsx
│   ├── MainTabs.tsx
│   └── RootNavigator.tsx
├── services/        # Mock Service Files
│   ├── authService.ts
│   ├── medicationService.ts
│   ├── healthService.ts
│   ├── caregiverService.ts
│   └── notificationService.ts
├── store/           # Zustand Store configuration
│   └── useAppStore.ts
├── theme/           # Design System & TypeScript Interfaces
│   ├── tokens.ts
│   └── types.ts
└── screens/         # Placeholder Screen Components
```

## 2. TypeScript Interfaces
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  role: 'patient' | 'caregiver';
}

interface Medication {
  id: string;
  name: string;
  dosage: string;
  time: string;
  taken: boolean;
}

interface HealthMetric {
  type: 'heart_rate' | 'blood_pressure' | 'steps';
  value: number;
  unit: string;
  timestamp: string;
}

interface AppState {
  user: User | null;
  medications: Medication[];
  healthData: HealthMetric[];
  isEmergency: boolean;
  setEmergency: (status: boolean) => void;
  // ... other actions
}
```

## 3. Zustand Store Configuration
```typescript
import { create } from 'zustand';

export const useAppStore = create<AppState>((set) => ({
  user: null,
  medications: [],
  healthData: [],
  isEmergency: false,
  setEmergency: (status) => set({ isEmergency: status }),
  // Mock actions for Phase 1
  login: (userData: User) => set({ user: userData }),
  logout: () => set({ user: null }),
}));
```

## 4. Mock Services (Skeleton)
```typescript
export const authService = {
  login: async () => ({ success: true, user: { id: '1', name: 'John Doe' } }),
  register: async () => ({ success: true }),
};

export const medicationService = {
  getTodayMeds: async () => [{ id: '1', name: 'Aspirin', dosage: '100mg', time: '08:00', taken: false }],
};
// ... other services follow similar patterns
```