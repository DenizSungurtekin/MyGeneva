import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { EventCard } from '../components/EventCard';
import { PlaceCard } from '../components/PlaceCard';
import { RestaurantCard } from '../components/RestaurantCard';
import { SearchInput } from '../components/SearchInput';
import { useApp } from '../state/AppContext';
import { spacing, useTheme } from '../theme';

const SEARCH_MIN_CHARS = 3;

function containsCI(haystack: string | null | undefined, needle: string): boolean {
  if (!haystack) return false;
  return haystack.toLowerCase().includes(needle);
}

export function FavoritesScreen() {
  const {
    favoriteEvents,
    favoriteRestaurants,
    favoritePlaces,
    favoritesLoading,
    isFavorite,
    toggleFavorite,
    openDetail,
    openPlace,
    favoritesSearchQuery,
    setFavoritesSearchQuery,
  } = useApp();
  const { theme } = useTheme();

  const trimmed = favoritesSearchQuery.trim().toLowerCase();
  const searchActive = trimmed.length >= SEARCH_MIN_CHARS;

  const filteredPlaces = useMemo(() => {
    if (!searchActive) return favoritePlaces;
    return favoritePlaces.filter(
      (p) => containsCI(p.name, trimmed) || containsCI(p.address, trimmed),
    );
  }, [favoritePlaces, searchActive, trimmed]);

  const filteredEvents = useMemo(() => {
    if (!searchActive) return favoriteEvents;
    return favoriteEvents.filter(
      (e) =>
        containsCI(e.title, trimmed) ||
        containsCI(e.description, trimmed) ||
        containsCI(e.location_name, trimmed),
    );
  }, [favoriteEvents, searchActive, trimmed]);

  const filteredRestaurants = useMemo(() => {
    if (!searchActive) return favoriteRestaurants;
    return favoriteRestaurants.filter(
      (r) =>
        containsCI(r.title, trimmed) ||
        containsCI(r.description, trimmed) ||
        containsCI(r.location_name, trimmed),
    );
  }, [favoriteRestaurants, searchActive, trimmed]);

  const isEmpty =
    filteredEvents.length === 0 &&
    filteredRestaurants.length === 0 &&
    filteredPlaces.length === 0;

  const isSourceEmpty =
    favoriteEvents.length === 0 &&
    favoriteRestaurants.length === 0 &&
    favoritePlaces.length === 0;

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: { flex: 1 },
        header: {
          flexDirection: 'row',
          alignItems: 'flex-end',
          gap: spacing.sm,
          paddingHorizontal: spacing.lg,
          paddingTop: spacing.md,
          marginBottom: spacing.lg,
        },
        titleBlock: { flexShrink: 0 },
        title: { ...theme.text.h1, marginTop: spacing.xxs },
        search: { flex: 1, marginBottom: 4 },
        sectionHeader: {
          ...theme.text.eyebrow,
          paddingHorizontal: spacing.lg,
          marginTop: spacing.md,
          marginBottom: spacing.xs,
        },
        empty: {
          flex: 1,
          alignItems: 'center',
          justifyContent: 'center',
          paddingHorizontal: spacing.xl,
          gap: spacing.xs,
        },
        emptyTitle: { ...theme.text.h3, marginTop: spacing.sm },
        emptyBody: {
          ...theme.text.body,
          color: theme.colors.textMuted,
          textAlign: 'center',
        },
      }),
    [theme],
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.titleBlock}>
          <Text style={theme.text.eyebrow}>Sauvegardés</Text>
          <Text style={styles.title}>Favoris</Text>
        </View>
        <SearchInput
          value={favoritesSearchQuery}
          onChangeText={setFavoritesSearchQuery}
          style={styles.search}
        />
      </View>

      {favoritesLoading ? (
        <ActivityIndicator style={{ marginTop: spacing.lg }} color={theme.colors.text} />
      ) : isSourceEmpty ? (
        <View style={styles.empty}>
          <Feather name="heart" size={32} color={theme.colors.textMuted} />
          <Text style={styles.emptyTitle}>Aucun favori pour l'instant</Text>
          <Text style={styles.emptyBody}>
            Appuie sur le cœur d'un lieu ou d'un événement pour le retrouver ici.
          </Text>
        </View>
      ) : isEmpty ? (
        <View style={styles.empty}>
          <Feather name="search" size={32} color={theme.colors.textMuted} />
          <Text style={styles.emptyTitle}>Aucun résultat</Text>
          <Text style={styles.emptyBody}>
            Rien de sauvegardé ne contient « {favoritesSearchQuery.trim()} ».
          </Text>
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {filteredPlaces.length > 0 && (
            <>
              <Text style={styles.sectionHeader}>Lieux</Text>
              {filteredPlaces.map((p) => (
                <PlaceCard
                  key={`place-${p.id}`}
                  place={p}
                  favorite
                  onPress={() => openPlace({ id: p.id, origin: 'favoris' })}
                  onToggleFavorite={() => toggleFavorite('place', p.id)}
                />
              ))}
            </>
          )}
          {filteredEvents.length > 0 && (
            <>
              <Text style={styles.sectionHeader}>Événements</Text>
              {filteredEvents.map((e) => (
                <EventCard
                  key={`event-${e.id}`}
                  event={e}
                  favorite={isFavorite('event', e.id)}
                  onPress={() =>
                    openDetail({ type: 'event', id: e.id, origin: 'favoris' })
                  }
                  onToggleFavorite={() => toggleFavorite('event', e.id)}
                  showDate
                />
              ))}
            </>
          )}
          {filteredRestaurants.length > 0 && (
            <>
              <Text style={styles.sectionHeader}>Restaurants</Text>
              {filteredRestaurants.map((r) => (
                <RestaurantCard
                  key={`rest-${r.id}`}
                  restaurant={r}
                  favorite={isFavorite('restaurant', r.id)}
                  onPress={() =>
                    openDetail({ type: 'restaurant', id: r.id, origin: 'favoris' })
                  }
                  onToggleFavorite={() => toggleFavorite('restaurant', r.id)}
                />
              ))}
            </>
          )}
        </ScrollView>
      )}
    </View>
  );
}
