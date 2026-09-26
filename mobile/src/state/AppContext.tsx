import React, {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { eventsApi } from '../api/events';
import { favoritesApi } from '../api/favorites';
import { restaurantsApi } from '../api/restaurants';
import { CategoryKey } from '../theme/colors';
import {
  EventCategory,
  EventItem,
  FavoriteItem,
  FavoriteItemType,
  RestaurantItem,
} from '../types/api';
import { toISODate } from '../utils/date';

export type ScreenName = 'accueil' | 'detail' | 'favoris';

export interface DetailTarget {
  type: FavoriteItemType;
  id: number;
  origin: ScreenName; // where to return to
}

interface AppState {
  screen: ScreenName;
  category: CategoryKey;
  selectedDay: Date;
  detail: DetailTarget | null;

  eventFeed: EventItem[];
  eventFeedLoading: boolean;
  restaurants: RestaurantItem[];
  restaurantsLoading: boolean;

  favorites: FavoriteItem[];
  favoritesLoading: boolean;
  favoriteEvents: EventItem[];
  favoriteRestaurants: RestaurantItem[];

  // Home search — persists across navigation to Detail and back.
  searchQuery: string;
  setSearchQuery: (q: string) => void;

  error: string | null;

  setScreen: (s: ScreenName) => void;
  setCategory: (c: CategoryKey) => void;
  setSelectedDay: (d: Date) => void;
  openDetail: (target: DetailTarget) => void;
  closeDetail: () => void;

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
  // A favourite is kept as long as the event hasn't finished. Use date_end
  // when the source provided one, else fall back to date_start (best guess).
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

  const [eventFeed, setEventFeed] = useState<EventItem[]>([]);
  const [eventFeedLoading, setEventFeedLoading] = useState(false);
  const [restaurants, setRestaurants] = useState<RestaurantItem[]>([]);
  const [restaurantsLoading, setRestaurantsLoading] = useState(false);

  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [favoritesLoading, setFavoritesLoading] = useState(false);
  const [favoriteEvents, setFavoriteEvents] = useState<EventItem[]>([]);
  const [favoriteRestaurants, setFavoriteRestaurants] = useState<RestaurantItem[]>([]);

  const [searchQuery, setSearchQuery] = useState<string>('');

  const [error, setError] = useState<string | null>(null);

  const refreshEventFeed = useCallback(async () => {
    const eventCategory = categoryToEventCategory(category);
    if (!eventCategory) {
      // Restaurant tab (hidden today) doesn't feed events.
      setEventFeed([]);
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
      } = {
        date: iso,
        category: eventCategory,
      };
      if (trimmed.length >= SEARCH_MIN_CHARS) {
        params.search = trimmed;
      }
      const data = await eventsApi.forYou(params);
      setEventFeed(data);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setEventFeedLoading(false);
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

  const refreshFavorites = useCallback(async () => {
    setFavoritesLoading(true);
    try {
      const list = await favoritesApi.list();
      setFavorites(list);

      const eventFavIds = list.filter((f) => f.item_type === 'event').map((f) => f.item_id);
      const restFavIds = list
        .filter((f) => f.item_type === 'restaurant')
        .map((f) => f.item_id);

      const [evts, rsts] = await Promise.all([
        Promise.all(
          eventFavIds.map((id) => eventsApi.get(id).catch(() => null)),
        ),
        Promise.all(
          restFavIds.map((id) => restaurantsApi.get(id).catch(() => null)),
        ),
      ]);
      const upcomingEvents = (evts.filter(Boolean) as EventItem[]).filter(isEventInFuture);
      setFavoriteEvents(upcomingEvents);
      setFavoriteRestaurants(rsts.filter(Boolean) as RestaurantItem[]);
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
      refreshFavorites(),
    ]);
  }, [refreshEventFeed, refreshRestaurants, refreshFavorites]);

  // Feed refetches on day/category/search change. Debounce lives in the
  // typing UX (search input) if we want to smooth network chatter later —
  // for now every keystroke past the 3-char threshold fires a query.
  useEffect(() => {
    refreshEventFeed();
  }, [refreshEventFeed]);

  useEffect(() => {
    refreshRestaurants();
    refreshFavorites();
    // Intentionally run once on mount — restaurants + favorites don't depend
    // on the currently-selected day.
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
        // A favorite count change may reshuffle the feed's ranking.
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

  const value = useMemo<AppState>(
    () => ({
      screen,
      category,
      selectedDay,
      detail,
      eventFeed,
      eventFeedLoading,
      restaurants,
      restaurantsLoading,
      favorites,
      favoritesLoading,
      favoriteEvents,
      favoriteRestaurants,
      searchQuery,
      setSearchQuery,
      error,
      setScreen,
      setCategory,
      setSelectedDay,
      openDetail,
      closeDetail,
      toggleFavorite,
      isFavorite,
      refreshAll,
    }),
    [
      screen,
      category,
      selectedDay,
      detail,
      eventFeed,
      eventFeedLoading,
      restaurants,
      restaurantsLoading,
      favorites,
      favoritesLoading,
      favoriteEvents,
      favoriteRestaurants,
      searchQuery,
      error,
      openDetail,
      closeDetail,
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
