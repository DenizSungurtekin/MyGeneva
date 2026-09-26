import { EventItem, PlaceItem } from '../types/api';
import { api } from './client';

export const placesApi = {
  list: () => api.get<PlaceItem[]>('/places'),
  get: (id: number) => api.get<PlaceItem>(`/places/${id}`),
  events: (id: number) => api.get<EventItem[]>(`/places/${id}/events`),
};
