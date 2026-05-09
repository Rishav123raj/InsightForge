import type { AssistantSettings, BestTitleRow, ChatResponse, CityEngagementRow } from '../types/api';

const normalizeBaseUrl = (value: string) => value.replace(/\/$/, '');

async function request<T>(path: string, settings: AssistantSettings, init?: RequestInit): Promise<T> {
  const response = await fetch(`${normalizeBaseUrl(settings.apiBaseUrl)}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': settings.apiKey,
      'X-User-Role': settings.role,
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API ${response.status}: ${detail || response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export function askAssistant(question: string, settings: AssistantSettings): Promise<ChatResponse> {
  return request<ChatResponse>('/api/chat', settings, {
    method: 'POST',
    body: JSON.stringify({ question })
  });
}

export function fetchBestTitles(settings: AssistantSettings): Promise<BestTitleRow[]> {
  return request<BestTitleRow[]>(`/api/analytics/best-titles?year=${settings.year}`, settings);
}

export function fetchCityEngagement(settings: AssistantSettings): Promise<CityEngagementRow[]> {
  return request<CityEngagementRow[]>(`/api/analytics/city-engagement?month=${encodeURIComponent(settings.month)}`, settings);
}