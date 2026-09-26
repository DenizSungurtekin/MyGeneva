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

export type ScreenName = 'accueil' | 'liste' | 'detail' | 'favoris';

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

  events: EventItem[];
  eventsLoading: boolean;
  eventHighlights: EventItem[];
  eventHighlightsLoading: boolean;
  restaurants: RestaurantItem[];
  restaurantsLoading: boolean;

  favorites: FavoriteItem[];
  favoritesLoading: boolean;
  favoriteEvents: EventItem[];
  favoriteRestaurants: RestaurantItem[];

  // ListScreen search state — kept at app level so navigating to Detail and
  // back preserves the user's active query + results.
  listSearchQuery: string;
  listSearchResults: EventItem[];
  listSearchLoading: boolean;
  setListSearchQuery: (q: string) => void;

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

const LIST_SEARCH_MIN_CHARS = 3;

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
  const [category, setCategory] = useState<CategoryKey>('soiree');
  const [selectedDay, setSelectedDay] = useState<Date>(() => {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    return now;
  });
  const [detail, setDetail] = useState<DetailTarget | null>(null);

  const [events, setEvents] = useState<EventItem[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);
  const [eventHighlights, setEventHighlights] = useState<EventItem[]>([]);
  const [eventHighlightsLoading, setEventHighlightsLoading] = useState(false);
  const [restaurants, setRestaurants] = useState<RestaurantItem[]>([]);
  const [restaurantsLoading, setRestaurantsLoading] = useState(false);

  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [favoritesLoading, setFavoritesLoading] = useState(false);
  const [favoriteEvents, setFavoriteEvents] = useState<EventItem[]>([]);
  const [favoriteRestaurants, setFavoriteRestaurants] = useState<RestaurantItem[]>([]);

  const [listSearchQuery, setListSearchQuery] = useState<string>('');
  const [listSearchResults, setListSearchResults] = useState<EventItem[]>([]);
  const [listSearchLoading, setListSearchLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const refreshEvents = useCallback(async () => {
    setEventsLoading(true);
    try {
      const iso = toISODate(selectedDay);
      const data = await eventsApi.list({ date: iso });
      setEvents(data);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setEventsLoading(false);
    }
  }, [selectedDay]);

  const refreshEventHighlights = useCallback(async () => {
    const eventCategory = categoryToEventCategory(category);
    if (!eventCategory) {
      // Restaurant tab doesn't use highlights — clear stale state so consumers
      // fall back to their own preview logic.
      setEventHighlights([]);
      return;
    }
    setEventHighlightsLoading(true);
    try {
      const iso = toISODate(selectedDay);
      const data = await eventsApi.highlights({
        date: iso,
        category: eventCategory,
        limit: 3,
      });
      setEventHighlights(data);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setEventHighlightsLoading(false);
    }
  }, [selectedDay, category]);

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
      refreshEvents(),
      refreshEventHighlights(),
      refreshRestaurants(),
      refreshFavorites(),
    ]);
  }, [refreshEvents, refreshEventHighlights, refreshRestaurants, refreshFavorites]);

  useEffect(() => {
    refreshEvents();
  }, [refreshEvents]);

  useEffect(() => {
    refreshEventHighlights();
  }, [refreshEventHighlights]);

  // ListScreen search: refetch when query or category changes. Query is
  // trimmed and normalized before comparing to the min-chars threshold so
  // "  ab " doesn't count as 4 chars.
  useEffect(() => {
    const trimmed = listSearchQuery.trim();
    if (trimmed.length < LIST_SEARCH_MIN_CHARS) {
      setListSearchResults([]);
      setListSearchLoading(false);
      return;
    }
    let cancelled = false;
    setListSearchLoading(true);
    const eventCategory = categoryToEventCategory(category);
    eventsApi
      .list({
        search: trimmed,
        ...(eventCategory ? { category: eventCategory } : {}),
      })
      .then((res) => {
        if (!cancelled) setListSearchResults(res);
      })
      .catch(() => {
        if (!cancelled) setListSearchResults([]);
      })
      .finally(() => {
        if (!cancelled) setListSearchLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [listSearchQuery, category]);

  useEffect(() => {
    refreshRestaurants();
    refreshFavorites();
    // Intentionally run once on mount for restaurants and favorites;
    // refreshEvents is date-scoped and handles its own dependency.
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
        await Promise.all([refreshFavorites(), refreshEventHighlights()]);
      } catch (e) {
        setError((e as Error).message);
      }
    },
    [favorites, refreshFavorites, refreshEventHighlights],
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
      events,
      eventsLoading,
      eventHighlights,
      eventHighlightsLoading,
      restaurants,
      restaurantsLoading,
      favorites,
      favoritesLoading,
      favoriteEvents,
      favoriteRestaurants,
      listSearchQuery,
      listSearchResults,
      listSearchLoading,
      setListSearchQuery,
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
      events,
      eventsLoading,
      eventHighlights,
      eventHighlightsLoading,
      restaurants,
      restaurantsLoading,
      favorites,
      favoritesLoading,
      favoriteEvents,
      favoriteRestaurants,
      listSearchQuery,
      listSearchResults,
      listSearchLoading,
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
