import React, {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import { eventsApi } from '../api/events';
import { favoritesApi } from '../api/favorites';
import { placesApi } from '../api/places';
import { restaurantsApi } from '../api/restaurants';
import { CategoryKey } from '../theme/colors';
import {
  EventCategory,
  EventItem,
  FavoriteItem,
  FavoriteItemType,
  PlaceItem,
  RestaurantItem,
} from '../types/api';
import { toISODate } from '../utils/date';

export type ScreenName =
  | 'accueil'
  | 'lieu'
  | 'lieuDetail'
  | 'lieuEvents'
  | 'detail'
  | 'favoris';

export interface DetailTarget {
  type: 'event' | 'restaurant';
  id: number;
  origin: ScreenName;
}

export interface PlaceTarget {
  id: number;
  origin: ScreenName;
}

interface AppState {
  screen: ScreenName;
  category: CategoryKey;
  selectedDay: Date;
  detail: DetailTarget | null;
  placeDetail: PlaceTarget | null;

  eventFeed: EventItem[];
  eventFeedLoading: boolean;
  restaurants: RestaurantItem[];
  restaurantsLoading: boolean;
  places: PlaceItem[];
  placesLoading: boolean;

  favorites: FavoriteItem[];
  favoritesLoading: boolean;
  favoriteEvents: EventItem[];
  favoriteRestaurants: RestaurantItem[];
  favoritePlaces: PlaceItem[];

  searchQuery: string;
  setSearchQuery: (q: string) => void;
  placeSearchQuery: string;
  setPlaceSearchQuery: (q: string) => void;
  favoritesSearchQuery: string;
  setFavoritesSearchQuery: (q: string) => void;

  error: string | null;

  setScreen: (s: ScreenName) => void;
  setCategory: (c: CategoryKey) => void;
  setSelectedDay: (d: Date) => void;
  openDetail: (target: DetailTarget) => void;
  closeDetail: () => void;
  openPlace: (target: PlaceTarget) => void;
  openPlaceEvents: (target: PlaceTarget) => void;
  closePlace: () => void;

  toggleFavorite: (type: FavoriteItemType, itemId: number) => Promise<void>;
  isFavorite: (type: FavoriteItemType, itemId: number) => boolean;
  refreshAll: () => Promise<void>;
}

const SEARCH_MIN_CHARS = 3;

const AppContext = createContext<AppState | undefined>(undefined);

function categoryToEventCategory(c: CategoryKey): EventCategory | null {
  if (c === 'journee') return 'journee';
  if (c === 'soiree') return 'soiree';
  return null;
}

function isEventInFuture(event: EventItem): boolean {
  const endIso = event.date_end ?? event.date_start;
  return new Date(endIso).getTime() >= Date.now();
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [screen, setScreen] = useState<ScreenName>('accueil');
  const [category, setCategory] = useState<CategoryKey>('journee');
  const [selectedDay, setSelectedDay] = useState<Date>(() => {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    return now;
  });
  const [detail, setDetail] = useState<DetailTarget | null>(null);
  const [placeDetail, setPlaceDetail] = useState<PlaceTarget | null>(null);

  const [eventFeed, setEventFeed] = useState<EventItem[]>([]);
  const [eventFeedLoading, setEventFeedLoading] = useState(false);
  const [restaurants, setRestaurants] = useState<RestaurantItem[]>([]);
  const [restaurantsLoading, setRestaurantsLoading] = useState(false);
  const [places, setPlaces] = useState<PlaceItem[]>([]);
  const [placesLoading, setPlacesLoading] = useState(false);

  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [favoritesLoading, setFavoritesLoading] = useState(false);
  const [favoriteEvents, setFavoriteEvents] = useState<EventItem[]>([]);
  const [favoriteRestaurants, setFavoriteRestaurants] = useState<RestaurantItem[]>([]);
  const [favoritePlaces, setFavoritePlaces] = useState<PlaceItem[]>([]);

  const [searchQuery, setSearchQuery] = useState<string>('');
  const [placeSearchQuery, setPlaceSearchQuery] = useState<string>('');
  const [favoritesSearchQuery, setFavoritesSearchQuery] = useState<string>('');

  const [error, setError] = useState<string | null>(null);

  // Sequence guard for the /for-you fetch. When the user flicks Soirée →
  // Journée quickly, the slow response can arrive after the fast one and
  // overwrite the correct state. Every call bumps the token; results only
  // apply if they still match the latest one.
  const feedRequestToken = useRef(0);

  const refreshEventFeed = useCallback(async () => {
    const eventCategory = categoryToEventCategory(category);
    const myToken = ++feedRequestToken.current;
    if (!eventCategory) {
      setEventFeed([]);
      setEventFeedLoading(false);
      return;
    }
    setEventFeedLoading(true);
    try {
      const iso = toISODate(selectedDay);
      const trimmed = searchQuery.trim();
      const params: {
        date: string;
        category: EventCategory;
        search?: string;
      } = { date: iso, category: eventCategory };
      if (trimmed.length >= SEARCH_MIN_CHARS) {
        params.search = trimmed;
      }
      const data = await eventsApi.forYou(params);
      if (myToken !== feedRequestToken.current) return;   // stale response
      setEventFeed(data);
      setError(null);
    } catch (e) {
      if (myToken !== feedRequestToken.current) return;
      setError((e as Error).message);
    } finally {
      if (myToken === feedRequestToken.current) {
        setEventFeedLoading(false);
      }
    }
  }, [selectedDay, category, searchQuery]);

  const refreshRestaurants = useCallback(async () => {
    setRestaurantsLoading(true);
    try {
      const data = await restaurantsApi.list();
      setRestaurants(data);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRestaurantsLoading(false);
    }
  }, []);

  const placesRequestToken = useRef(0);

  const refreshPlaces = useCallback(async () => {
    const myToken = ++placesRequestToken.current;
    setPlacesLoading(true);
    try {
      const trimmed = placeSearchQuery.trim();
      const params = trimmed.length >= SEARCH_MIN_CHARS ? { search: trimmed } : {};
      const data = await placesApi.list(params);
      if (myToken !== placesRequestToken.current) return;
      setPlaces(data);
      setError(null);
    } catch (e) {
      if (myToken !== placesRequestToken.current) return;
      setError((e as Error).message);
    } finally {
      if (myToken === placesRequestToken.current) {
        setPlacesLoading(false);
      }
    }
  }, [placeSearchQuery]);

  const refreshFavorites = useCallback(async () => {
    setFavoritesLoading(true);
    try {
      const list = await favoritesApi.list();
      setFavorites(list);

      const eventFavIds = list.filter((f) => f.item_type === 'event').map((f) => f.item_id);
      const restFavIds = list.filter((f) => f.item_type === 'restaurant').map((f) => f.item_id);
      const placeFavIds = list.filter((f) => f.item_type === 'place').map((f) => f.item_id);

      const [evts, rsts, plcs] = await Promise.all([
        Promise.all(eventFavIds.map((id) => eventsApi.get(id).catch(() => null))),
        Promise.all(restFavIds.map((id) => restaurantsApi.get(id).catch(() => null))),
        Promise.all(placeFavIds.map((id) => placesApi.get(id).catch(() => null))),
      ]);
      const upcomingEvents = (evts.filter(Boolean) as EventItem[]).filter(isEventInFuture);
      setFavoriteEvents(upcomingEvents);
      setFavoriteRestaurants(rsts.filter(Boolean) as RestaurantItem[]);
      setFavoritePlaces(plcs.filter(Boolean) as PlaceItem[]);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setFavoritesLoading(false);
    }
  }, []);

  const refreshAll = useCallback(async () => {
    await Promise.all([
      refreshEventFeed(),
      refreshRestaurants(),
      refreshPlaces(),
      refreshFavorites(),
    ]);
  }, [refreshEventFeed, refreshRestaurants, refreshPlaces, refreshFavorites]);

  useEffect(() => {
    refreshEventFeed();
  }, [refreshEventFeed]);

  useEffect(() => {
    refreshPlaces();
  }, [refreshPlaces]);

  useEffect(() => {
    refreshRestaurants();
    refreshFavorites();
    // These don't depend on the selected day or any query.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isFavorite = useCallback(
    (type: FavoriteItemType, itemId: number) =>
      favorites.some((f) => f.item_type === type && f.item_id === itemId),
    [favorites],
  );

  const toggleFavorite = useCallback(
    async (type: FavoriteItemType, itemId: number) => {
      const existing = favorites.find(
        (f) => f.item_type === type && f.item_id === itemId,
      );
      try {
        if (existing) {
          await favoritesApi.remove(existing.id);
        } else {
          await favoritesApi.add(type, itemId);
        }
        await Promise.all([refreshFavorites(), refreshEventFeed()]);
      } catch (e) {
        setError((e as Error).message);
      }
    },
    [favorites, refreshFavorites, refreshEventFeed],
  );

  const openDetail = useCallback((target: DetailTarget) => {
    setDetail(target);
    setScreen('detail');
  }, []);

  const closeDetail = useCallback(() => {
    setDetail((current) => {
      if (current) {
        setScreen(current.origin);
      } else {
        setScreen('accueil');
      }
      return null;
    });
  }, []);

  const openPlace = useCallback((target: PlaceTarget) => {
    setPlaceDetail(target);
    setScreen('lieuDetail');
  }, []);

  const openPlaceEvents = useCallback((target: PlaceTarget) => {
    setPlaceDetail(target);
    setScreen('lieuEvents');
  }, []);

  const closePlace = useCallback(() => {
    setPlaceDetail((current) => {
      if (!current) {
        setScreen('lieu');
        return null;
      }
      setScreen(current.origin);
      // If we're bouncing back to another lieu screen (LieuEvents → PlaceDetail),
      // the target still needs the placeDetail context to render. Only clear it
      // when we actually leave the lieu flow.
      if (current.origin === 'lieuDetail' || current.origin === 'lieuEvents') {
        return current;
      }
      return null;
    });
  }, []);

  const value = useMemo<AppState>(
    () => ({
      screen,
      category,
      selectedDay,
      detail,
      placeDetail,
      eventFeed,
      eventFeedLoading,
      restaurants,
      restaurantsLoading,
      places,
      placesLoading,
      favorites,
      favoritesLoading,
      favoriteEvents,
      favoriteRestaurants,
      favoritePlaces,
      searchQuery,
      setSearchQuery,
      placeSearchQuery,
      setPlaceSearchQuery,
      favoritesSearchQuery,
      setFavoritesSearchQuery,
      error,
      setScreen,
      setCategory,
      setSelectedDay,
      openDetail,
      closeDetail,
      openPlace,
      openPlaceEvents,
      closePlace,
      toggleFavorite,
      isFavorite,
      refreshAll,
    }),
    [
      screen,
      category,
      selectedDay,
      detail,
      placeDetail,
      eventFeed,
      eventFeedLoading,
      restaurants,
      restaurantsLoading,
      places,
      placesLoading,
      favorites,
      favoritesLoading,
      favoriteEvents,
      favoriteRestaurants,
      favoritePlaces,
      searchQuery,
      placeSearchQuery,
      favoritesSearchQuery,
      error,
      openDetail,
      closeDetail,
      openPlace,
      openPlaceEvents,
      closePlace,
      toggleFavorite,
      isFavorite,
      refreshAll,
    ],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}

export { categoryToEventCategory };
