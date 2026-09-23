import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { ActivityIndicator, FlatList, StyleSheet, Text, View } from 'react-native';

import { EventCard } from '../components/EventCard';
import { RestaurantCard } from '../components/RestaurantCard';
import { useApp } from '../state/AppContext';
import { colors, spacing, text } from '../theme';
import { EventItem, RestaurantItem } from '../types/api';

type Row =
  | { kind: 'event'; item: EventItem }
  | { kind: 'restaurant'; item: RestaurantItem };

export function FavoritesScreen() {
  const {
    favoriteEvents,
    favoriteRestaurants,
    favoritesLoading,
    isFavorite,
    toggleFavorite,
    openDetail,
  } = useApp();

  const rows: Row[] = useMemo(() => {
    const combined: Row[] = [
      ...favoriteEvents.map((e) => ({ kind: 'event', item: e }) as Row),
      ...favoriteRestaurants.map((r) => ({ kind: 'restaurant', item: r }) as Row),
    ];
    return combined;
  }, [favoriteEvents, favoriteRestaurants]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={text.eyebrow}>Sauvegardés</Text>
        <Text style={styles.title}>Favoris</Text>
      </View>

      {favoritesLoading ? (
        <ActivityIndicator style={{ marginTop: spacing.lg }} color={colors.text} />
      ) : rows.length === 0 ? (
        <View style={styles.empty}>
          <Feather name="heart" size={32} color={colors.textMuted} />
          <Text style={styles.emptyTitle}>Aucun favori pour l'instant</Text>
          <Text style={styles.emptyBody}>
            Appuie sur le cœur d'un événement ou d'un restaurant pour le retrouver ici.
          </Text>
        </View>
      ) : (
        <FlatList
          data={rows}
          keyExtractor={(row) => `${row.kind}-${row.item.id}`}
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          renderItem={({ item: row }) =>
            row.kind === 'event' ? (
              <EventCard
                event={row.item}
                favorite={isFavorite('event', row.item.id)}
                onPress={() =>
                  openDetail({ type: 'event', id: row.item.id, origin: 'favoris' })
                }
                onToggleFavorite={() => toggleFavorite('event', row.item.id)}
              />
            ) : (
              <RestaurantCard
                restaurant={row.item}
                favorite={isFavorite('restaurant', row.item.id)}
                onPress={() =>
                  openDetail({ type: 'restaurant', id: row.item.id, origin: 'favoris' })
                }
                onToggleFavorite={() => toggleFavorite('restaurant', row.item.id)}
              />
            )
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    marginBottom: spacing.lg,
  },
  title: {
    ...text.h1,
    marginTop: spacing.xxs,
  },
  empty: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.xl,
    gap: spacing.xs,
  },
  emptyTitle: {
    ...text.h3,
    marginTop: spacing.sm,
  },
  emptyBody: {
    ...text.body,
    color: colors.textMuted,
    textAlign: 'center',
  },
});
