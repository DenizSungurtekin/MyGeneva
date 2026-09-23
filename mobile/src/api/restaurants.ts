import { RestaurantItem } from '../types/api';
import { api } from './client';

export const restaurantsApi = {
  list: () => api.get<RestaurantItem[]>('/restaurants'),
  get: (id: number) => api.get<RestaurantItem>(`/restaurants/${id}`),
};
