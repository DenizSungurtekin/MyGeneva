import { Feather } from '@expo/vector-icons';
import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { CategoryTabs } from '../components/CategoryTabs';
import { EventCard } from '../components/EventCard';
import { RestaurantCard } from '../components/RestaurantCard';
import { eventsApi } from '../api/events';
import { categoryToEventCategory, useApp } from '../state/AppContext';
import { categoryLabel, radius, spacing, useTheme } from '../theme';
import { EventItem, RestaurantItem } from '../types/api';
import { longDayLabel } from '../utils/date';

type ListItem =
  | { kind: 'event'; item: EventItem }
  | { kind: 'restaurant'; item: RestaurantItem };

const SEARCH_MIN_CHARS = 3;

export function ListScreen() {
  const {
    category,
    setCategory,
    selectedDay,
    events,
    eventsLoading,
    restaurants,
    restaurantsLoading,
    isFavorite,
    toggleFavorite,
    openDetail,
    setScreen,
  } = useApp();
  const { theme } = useTheme();

  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState<EventItem[] | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const trimmed = search.trim();
  const searchActive = trimmed.length >= SEARCH_MIN_CHARS;

  useEffect(() => {
    if (!searchActive) {
      setSearchResults(null);
      return;
    }
    let cancelled = false;
    setSearchLoading(true);
    const eventCategory = categoryToEventCategory(category);
    eventsApi
      .list({
        search: trimmed,
        ...(eventCategory ? { category: eventCategory } : {}),
      })
      .then((res) => {
        if (!cancelled) setSearchResults(res);
      })
      .catch(() => {
        if (!cancelled) setSearchResults([]);
      })
      .finally(() => {
        if (!cancelled) setSearchLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [trimmed, searchActive, category]);

  const data: ListItem[] = useMemo(() => {
    if (searchActive) {
      return (searchResults ?? []).map((e) => ({ kind: 'event', item: e }) as ListItem);
    }
    if (category === 'restaurant') {
      return restaurants.map((r) => ({ kind: 'restaurant', item: r }) as ListItem);
    }
    return events
      .filter((e) => e.category === category)
      .map((e) => ({ kind: 'event', item: e }) as ListItem);
  }, [searchActive, searchResults, category, events, restaurants]);

  const isLoading = searchActive
    ? searchLoading
    : category === 'restaurant'
      ? restaurantsLoading
      : eventsLoading;

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          flex: 1,
        },
        header: {
          flexDirection: 'row',
          alignItems: 'flex-end',
          gap: spacing.sm,
          paddingHorizontal: spacing.lg,
          paddingTop: spacing.md,
          paddingBottom: spacing.md,
        },
        back: {
          marginRight: spacing.xs,
          marginBottom: 2,
        },
        title: {
          ...theme.text.h1,
          marginTop: spacing.xxs,
        },
        filterRow: {
          flexDirection: 'row',
          alignItems: 'center',
          gap: spacing.sm,
          paddingHorizontal: spacing.lg,
          marginBottom: spacing.md,
        },
        searchInput: {
          flex: 1,
          flexDirection: 'row',
          alignItems: 'center',
          gap: spacing.xs,
          paddingHorizontal: spacing.sm,
          paddingVertical: 6,
          borderRadius: radius.pill,
          borderWidth: 1,
          borderColor: theme.colors.border,
          backgroundColor: theme.colors.soft,
        },
        searchText: {
          flex: 1,
          ...theme.text.meta,
          color: theme.colors.text,
          padding: 0,
        },
        loader: {
          marginTop: spacing.lg,
        },
        empty: {
          ...theme.text.body,
          color: theme.colors.textMuted,
          paddingHorizontal: spacing.lg,
          marginTop: spacing.lg,
        },
      }),
    [theme],
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable
          onPress={() => setScreen('accueil')}
          style={styles.back}
          accessibilityRole="button"
          accessibilityLabel="Retour"
          hitSlop={8}
        >
          <Feather name="arrow-left" size={22} color={theme.colors.text} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={theme.text.eyebrow}>
            {category === 'restaurant' ? 'Restaurants' : longDayLabel(selectedDay)}
          </Text>
          <Text style={styles.title}>
            {searchActive ? 'Recherche' : categoryLabel[category]}
          </Text>
        </View>
      </View>

      <View style={styles.filterRow}>
        <CategoryTabs value={category} onChange={setCategory} paddingHorizontal={0} />
        <View style={styles.searchInput}>
          <Feather name="search" size={16} color={theme.colors.textMuted} />
          <TextInput
            style={styles.searchText}
            value={search}
            onChangeText={setSearch}
            placeholder="Rechercher"
            placeholderTextColor={theme.colors.textMuted}
            returnKeyType="search"
            autoCorrect={false}
            autoCapitalize="none"
          />
          {search.length > 0 ? (
            <Pressable
              onPress={() => setSearch('')}
              accessibilityRole="button"
              accessibilityLabel="Effacer la recherche"
              hitSlop={8}
            >
              <Feather name="x" size={16} color={theme.colors.textMuted} />
            </Pressable>
          ) : null}
        </View>
      </View>

      {isLoading ? (
        <ActivityIndicator style={styles.loader} color={theme.colors.text} />
      ) : (
        <FlatList
          data={data}
          keyExtractor={(entry) => `${entry.kind}-${entry.item.id}`}
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          ListEmptyComponent={
            <Text style={styles.empty}>
              {searchActive
                ? `Aucun événement ne contient "${trimmed}".`
                : 'Rien de prévu pour ce moment-là. Change de jour ou reviens plus tard.'}
            </Text>
          }
          renderItem={({ item: entry }) => {
            if (entry.kind === 'event') {
              return (
                <EventCard
                  event={entry.item}
                  favorite={isFavorite('event', entry.item.id)}
                  onPress={() =>
                    openDetail({ type: 'event', id: entry.item.id, origin: 'liste' })
                  }
                  onToggleFavorite={() => toggleFavorite('event', entry.item.id)}
                />
              );
            }
            return (
              <RestaurantCard
                restaurant={entry.item}
                favorite={isFavorite('restaurant', entry.item.id)}
                onPress={() =>
                  openDetail({ type: 'restaurant', id: entry.item.id, origin: 'liste' })
                }
                onToggleFavorite={() => toggleFavorite('restaurant', entry.item.id)}
              />
            );
          }}
        />
      )}
    </View>
  );
}
