import { EventCategory, EventItem } from '../types/api';
import { api } from './client';

export interface EventListParams {
  category?: EventCategory;
  date?: string; // YYYY-MM-DD
}

function toQueryString(params: EventListParams): string {
  const usp = new URLSearchParams();
  if (params.category) usp.set('category', params.category);
  if (params.date) usp.set('date', params.date);
  const qs = usp.toString();
  return qs ? `?${qs}` : '';
}

export const eventsApi = {
  list: (params: EventListParams = {}) =>
    api.get<EventItem[]>(`/events${toQueryString(params)}`),
  get: (id: number) => api.get<EventItem>(`/events/${id}`),
};
