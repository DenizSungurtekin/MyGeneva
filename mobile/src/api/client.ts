import Constants from 'expo-constants';
import { Platform } from 'react-native';

const DEFAULT_HOST = Platform.select({
  // Android emulator resolves the host machine at 10.0.2.2, not localhost.
  android: 'http://10.0.2.2:8000',
  default: 'http://localhost:8000',
});

const configured = (Constants.expoConfig?.extra as { apiUrl?: string } | undefined)?.apiUrl;

// On device, the loopback isn't useful — use LAN IP via EXPO_PUBLIC_API_URL if set.
const envUrl = (globalThis.process?.env?.EXPO_PUBLIC_API_URL as string | undefined) ?? undefined;

export const API_URL = envUrl || configured || DEFAULT_HOST!;

export interface ApiErrorPayload {
  detail?: string;
}

export class ApiError extends Error {
  status: number;
  payload: ApiErrorPayload | null;
  constructor(status: number, payload: ApiErrorPayload | null, message: string) {
    super(message);
    this.status = status;
    this.payload = payload;
  }
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(init.headers ?? {}),
    },
  });

  if (response.status === 204) {
    return undefined as T;
  }

  let payload: unknown = null;
  const raw = await response.text();
  if (raw) {
    try {
      payload = JSON.parse(raw);
    } catch {
      payload = raw;
    }
  }

  if (!response.ok) {
    const detail =
      (payload && typeof payload === 'object' && 'detail' in payload
        ? String((payload as ApiErrorPayload).detail)
        : response.statusText) || 'Request failed';
    throw new ApiError(response.status, payload as ApiErrorPayload | null, detail);
  }

  return payload as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  delete: <T = void>(path: string) => request<T>(path, { method: 'DELETE' }),
};
