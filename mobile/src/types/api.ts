export type EventCategory = 'journee' | 'soiree';

export interface EventItem {
  id: number;
  title: string;
  description: string;
  category: EventCategory;
  location_name: string;
  latitude: number | null;
  longitude: number | null;
  address: string;
  date_start: string; // ISO
  date_end: string | null;
  image_url: string | null;
  source: string | null;
  source_url: string | null;
  place_id: number | null;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface PlaceItem {
  id: number;
  name: string;
  address: string;
  latitude: number | null;
  longitude: number | null;
  image_url: string | null;
  description: string;
  source: string | null;
  external_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface RestaurantItem {
  id: number;
  title: string;
  description: string;
  location_name: string;
  latitude: number | null;
  longitude: number | null;
  address: string;
  opening_hours: string | null;
  rating: number | null;
  rating_count: number | null;
  image_url: string | null;
  source: string | null;
  source_url: string | null;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export type FavoriteItemType = 'event' | 'restaurant' | 'place';

export interface FavoriteItem {
  id: number;
  user_id: string;
  item_type: FavoriteItemType;
  item_id: number;
  created_at: string;
}
