import { EventItem, PlaceItem } from '../types/api';
import { api } from './client';

export interface PlaceListParams {
  search?: string;
}

function toQueryString(params: PlaceListParams): string {
  const usp = new URLSearchParams();
  if (params.search) usp.set('search', params.search);
  const qs = usp.toString();
  return qs ? `?${qs}` : '';
}

export const placesApi = {
  list: (params: PlaceListParams = {}) =>
    api.get<PlaceItem[]>(`/places${toQueryString(params)}`),
  get: (id: number) => api.get<PlaceItem>(`/places/${id}`),
  events: (id: number) => api.get<EventItem[]>(`/places/${id}/events`),
};
