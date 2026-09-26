import { EventCategory, EventItem } from '../types/api';
import { api } from './client';

export interface EventListParams {
  category?: EventCategory;
  date?: string;   // YYYY-MM-DD
  search?: string; // 3+ chars, ilike on title|description
}

export interface EventHighlightsParams extends EventListParams {
  limit?: number;
}

function toQueryString(params: EventHighlightsParams): string {
  const usp = new URLSearchParams();
  if (params.category) usp.set('category', params.category);
  if (params.date) usp.set('date', params.date);
  if (params.search) usp.set('search', params.search);
  if (params.limit !== undefined) usp.set('limit', String(params.limit));
  const qs = usp.toString();
  return qs ? `?${qs}` : '';
}

export const eventsApi = {
  list: (params: EventListParams = {}) =>
    api.get<EventItem[]>(`/events${toQueryString(params)}`),
  highlights: (params: EventHighlightsParams = {}) =>
    api.get<EventItem[]>(`/events/highlights${toQueryString(params)}`),
  get: (id: number) => api.get<EventItem>(`/events/${id}`),
};
