import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { EventCard } from '../components/EventCard';
import { PlaceCard } from '../components/PlaceCard';
import { RestaurantCard } from '../components/RestaurantCard';
import { useApp } from '../state/AppContext';
import { spacing, useTheme } from '../theme';

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
  } = useApp();
  const { theme } = useTheme();

  const isEmpty =
    favoriteEvents.length === 0 &&
    favoriteRestaurants.length === 0 &&
    favoritePlaces.length === 0;

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: { flex: 1 },
        header: {
          paddingHorizontal: spacing.lg,
          paddingTop: spacing.md,
          marginBottom: spacing.lg,
        },
        title: {
          ...theme.text.h1,
          marginTop: spacing.xxs,
        },
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
        emptyTitle: {
          ...theme.text.h3,
          marginTop: spacing.sm,
        },
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
        <Text style={theme.text.eyebrow}>Sauvegardés</Text>
        <Text style={styles.title}>Favoris</Text>
      </View>

      {favoritesLoading ? (
        <ActivityIndicator style={{ marginTop: spacing.lg }} color={theme.colors.text} />
      ) : isEmpty ? (
        <View style={styles.empty}>
          <Feather name="heart" size={32} color={theme.colors.textMuted} />
          <Text style={styles.emptyTitle}>Aucun favori pour l'instant</Text>
          <Text style={styles.emptyBody}>
            Appuie sur le cœur d'un lieu ou d'un événement pour le retrouver ici.
          </Text>
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          showsVerticalScrollIndicator={false}
        >
          {favoritePlaces.length > 0 && (
            <>
              <Text style={styles.sectionHeader}>Lieux</Text>
              {favoritePlaces.map((p) => (
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
          {favoriteEvents.length > 0 && (
            <>
              <Text style={styles.sectionHeader}>Événements</Text>
              {favoriteEvents.map((e) => (
                <EventCard
                  key={`event-${e.id}`}
                  event={e}
                  favorite={isFavorite('event', e.id)}
                  onPress={() =>
                    openDetail({ type: 'event', id: e.id, origin: 'favoris' })
                  }
                  onToggleFavorite={() => toggleFavorite('event', e.id)}
                />
              ))}
            </>
          )}
          {favoriteRestaurants.length > 0 && (
            <>
              <Text style={styles.sectionHeader}>Restaurants</Text>
              {favoriteRestaurants.map((r) => (
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
