import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, View } from 'react-native';

import { CategoryTabs } from '../components/CategoryTabs';
import { EventCard } from '../components/EventCard';
import { RestaurantCard } from '../components/RestaurantCard';
import { useApp } from '../state/AppContext';
import { categoryLabel, colors, spacing, text } from '../theme';
import { EventItem, RestaurantItem } from '../types/api';
import { longDayLabel } from '../utils/date';

type ListItem =
  | { kind: 'event'; item: EventItem }
  | { kind: 'restaurant'; item: RestaurantItem };

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

  const data: ListItem[] = useMemo(() => {
    if (category === 'restaurant') {
      return restaurants.map((r) => ({ kind: 'restaurant', item: r }) as ListItem);
    }
    return events
      .filter((e) => e.category === category)
      .map((e) => ({ kind: 'event', item: e }) as ListItem);
  }, [category, events, restaurants]);

  const isLoading = category === 'restaurant' ? restaurantsLoading : eventsLoading;

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
          <Feather name="arrow-left" size={22} color={colors.text} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={text.eyebrow}>
            {category === 'restaurant' ? 'Restaurants' : longDayLabel(selectedDay)}
          </Text>
          <Text style={styles.title}>{categoryLabel[category]}</Text>
        </View>
      </View>

      <View style={{ marginBottom: spacing.md }}>
        <CategoryTabs value={category} onChange={setCategory} />
      </View>

      {isLoading ? (
        <ActivityIndicator style={styles.loader} color={colors.text} />
      ) : (
        <FlatList
          data={data}
          keyExtractor={(entry) => `${entry.kind}-${entry.item.id}`}
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          ListEmptyComponent={
            <Text style={styles.empty}>Rien à afficher pour l'instant.</Text>
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

const styles = StyleSheet.create({
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
    ...text.h1,
    marginTop: spacing.xxs,
  },
  loader: {
    marginTop: spacing.lg,
  },
  empty: {
    ...text.body,
    color: colors.textMuted,
    paddingHorizontal: spacing.lg,
    marginTop: spacing.lg,
  },
});
