import { FavoriteItem, FavoriteItemType } from '../types/api';
import { api } from './client';

export const favoritesApi = {
  list: () => api.get<FavoriteItem[]>('/favorites'),
  add: (item_type: FavoriteItemType, item_id: number) =>
    api.post<FavoriteItem>('/favorites', { item_type, item_id }),
  remove: (id: number) => api.delete<void>(`/favorites/${id}`),
};
