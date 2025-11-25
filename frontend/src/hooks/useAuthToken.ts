import { useState } from 'react';
import { UserRole } from '../types';

type StoredAuth = { token: string; role: UserRole } | null;

const STORAGE_KEY = 'nr-auth';

function loadInitial(): StoredAuth {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) return null;
  try {
    return JSON.parse(saved) as StoredAuth;
  } catch (err) {
    console.warn('Failed to parse auth token from storage', err);
    return null;
  }
}

export function useAuthToken() {
  const initial = loadInitial();
  const [token, setToken] = useState<string>(initial?.token ?? '');
  const [role, setRole] = useState<UserRole>(initial?.role ?? 'viewer');

  const saveToken = (value: string, userRole: UserRole) => {
    setToken(value);
    setRole(userRole);
    const payload: StoredAuth = { token: value, role: userRole };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  };

  return { token, role, saveToken };
}
