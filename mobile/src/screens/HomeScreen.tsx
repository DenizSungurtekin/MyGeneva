import React, { useMemo } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { CategoryTabs } from '../components/CategoryTabs';
import { DayPicker } from '../components/DayPicker';
import { EventCard } from '../components/EventCard';
import { RestaurantCard } from '../components/RestaurantCard';
import { SectionHeader } from '../components/SectionHeader';
import { useApp } from '../state/AppContext';
import { colors, spacing, text } from '../theme';
import { EventCategory } from '../types/api';
import { longDayLabel } from '../utils/date';

const PREVIEW_LIMIT = 3;

export function HomeScreen() {
  const {
    selectedDay,
    setSelectedDay,
    category,
    setCategory,
    events,
    eventsLoading,
    restaurants,
    restaurantsLoading,
    isFavorite,
    toggleFavorite,
    openDetail,
    setScreen,
  } = useApp();

  const targetCategory = category === 'restaurant' ? null : (category as EventCategory);

  const items = useMemo(() => {
    if (category === 'restaurant') return restaurants;
    return events.filter((e) => e.category === targetCategory);
  }, [category, events, restaurants, targetCategory]);

  const preview = items.slice(0, PREVIEW_LIMIT);
  const isLoading = category === 'restaurant' ? restaurantsLoading : eventsLoading;

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.header}>
        <Text style={text.eyebrow}>Aujourd'hui à Genève</Text>
        <Text style={styles.headerTitle}>{longDayLabel(selectedDay)}</Text>
      </View>

      <DayPicker value={selectedDay} onChange={setSelectedDay} />

      <View style={{ height: spacing.md }} />
      <CategoryTabs value={category} onChange={setCategory} />

      <SectionHeader
        title={category === 'restaurant' ? 'À déguster' : 'Sélection du jour'}
        actionLabel={items.length > PREVIEW_LIMIT ? 'Voir tout' : undefined}
        onAction={items.length > PREVIEW_LIMIT ? () => setScreen('liste') : undefined}
      />

      {isLoading ? (
        <ActivityIndicator style={styles.loader} color={colors.text} />
      ) : preview.length === 0 ? (
        <Text style={styles.emptyText}>
          Rien à afficher pour cette catégorie. Ajoute des données via le seed backend.
        </Text>
      ) : (
        preview.map((item) => {
          if (category === 'restaurant') {
            const r = item as (typeof restaurants)[number];
            return (
              <RestaurantCard
                key={r.id}
                restaurant={r}
                favorite={isFavorite('restaurant', r.id)}
                onPress={() =>
                  openDetail({ type: 'restaurant', id: r.id, origin: 'accueil' })
                }
                onToggleFavorite={() => toggleFavorite('restaurant', r.id)}
              />
            );
          }
          const e = item as (typeof events)[number];
          return (
            <EventCard
              key={e.id}
              event={e}
              favorite={isFavorite('event', e.id)}
              onPress={() => openDetail({ type: 'event', id: e.id, origin: 'accueil' })}
              onToggleFavorite={() => toggleFavorite('event', e.id)}
            />
          );
        })
      )}

      <View style={{ height: spacing.xxl }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    paddingTop: spacing.md,
    paddingBottom: spacing.xxl,
  },
  header: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  headerTitle: {
    ...text.h1,
    marginTop: spacing.xxs,
    textTransform: 'capitalize',
  },
  loader: {
    marginTop: spacing.lg,
  },
  emptyText: {
    ...text.body,
    color: colors.textMuted,
    paddingHorizontal: spacing.lg,
    marginTop: spacing.sm,
  },
});
