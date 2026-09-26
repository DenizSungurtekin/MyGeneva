import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { CategoryTabs } from '../components/CategoryTabs';
import { DayPicker } from '../components/DayPicker';
import { EventCard } from '../components/EventCard';
import { RestaurantCard } from '../components/RestaurantCard';
import { SectionHeader } from '../components/SectionHeader';
import { useApp } from '../state/AppContext';
import { spacing, useTheme } from '../theme';
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
    eventHighlights,
    eventHighlightsLoading,
    restaurants,
    restaurantsLoading,
    isFavorite,
    toggleFavorite,
    openDetail,
    setScreen,
  } = useApp();
  const { theme, mode, toggle } = useTheme();

  const targetCategory = category === 'restaurant' ? null : (category as EventCategory);

  // Full list is used to decide whether "Voir tout" is worth showing.
  const fullItems = useMemo(() => {
    if (category === 'restaurant') return restaurants;
    return events.filter((e) => e.category === targetCategory);
  }, [category, events, restaurants, targetCategory]);

  // Preview shown on the home is:
  // - restaurants: first N (no ranking signal yet)
  // - events: /events/highlights, ranked by favorite count, tiebreak random.
  const preview =
    category === 'restaurant' ? restaurants.slice(0, PREVIEW_LIMIT) : eventHighlights;
  const isLoading =
    category === 'restaurant' ? restaurantsLoading : eventHighlightsLoading;

  const styles = useMemo(
    () =>
      StyleSheet.create({
        content: {
          paddingTop: spacing.md,
          paddingBottom: spacing.xxl,
        },
        header: {
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          paddingHorizontal: spacing.lg,
          marginBottom: spacing.md,
        },
        headerText: {
          flex: 1,
        },
        headerTitle: {
          ...theme.text.h1,
          marginTop: spacing.xxs,
          textTransform: 'capitalize',
        },
        themeToggle: {
          width: 40,
          height: 40,
          borderRadius: 20,
          borderWidth: 1,
          borderColor: theme.colors.border,
          backgroundColor: theme.colors.soft,
          alignItems: 'center',
          justifyContent: 'center',
          marginLeft: spacing.sm,
          marginTop: 2,
        },
        loader: {
          marginTop: spacing.lg,
        },
        emptyText: {
          ...theme.text.body,
          color: theme.colors.textMuted,
          paddingHorizontal: spacing.lg,
          marginTop: spacing.sm,
        },
      }),
    [theme],
  );

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text style={theme.text.eyebrow}>Aujourd'hui à Genève</Text>
          <Text style={styles.headerTitle}>{longDayLabel(selectedDay)}</Text>
        </View>
        <Pressable
          onPress={toggle}
          style={styles.themeToggle}
          accessibilityRole="button"
          accessibilityLabel={mode === 'dark' ? 'Passer en thème clair' : 'Passer en thème sombre'}
          hitSlop={6}
        >
          <Feather
            name={mode === 'dark' ? 'sun' : 'moon'}
            size={18}
            color={theme.colors.text}
          />
        </Pressable>
      </View>

      <DayPicker value={selectedDay} onChange={setSelectedDay} />

      <View style={{ height: spacing.md }} />
      <CategoryTabs value={category} onChange={setCategory} />

      <SectionHeader
        title={category === 'restaurant' ? 'À déguster' : 'Sélection du jour'}
        actionLabel={fullItems.length > PREVIEW_LIMIT ? 'Voir tout' : undefined}
        onAction={fullItems.length > PREVIEW_LIMIT ? () => setScreen('liste') : undefined}
      />

      {isLoading ? (
        <ActivityIndicator style={styles.loader} color={theme.colors.text} />
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
