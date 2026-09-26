import { Feather } from '@expo/vector-icons';
import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, View } from 'react-native';

import { placesApi } from '../api/places';
import { EventCard } from '../components/EventCard';
import { useApp } from '../state/AppContext';
import { spacing, useTheme } from '../theme';
import { EventItem, PlaceItem } from '../types/api';

export function LieuEventsScreen() {
  const {
    placeDetail,
    closePlace,
    isFavorite,
    toggleFavorite,
    openDetail,
  } = useApp();
  const { theme } = useTheme();
  const [place, setPlace] = useState<PlaceItem | null>(null);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    if (!placeDetail) return;
    setLoading(true);
    Promise.all([placesApi.get(placeDetail.id), placesApi.events(placeDetail.id)])
      .then(([p, evs]) => {
        if (!cancelled) {
          setPlace(p);
          setEvents(evs);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [placeDetail]);

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
          paddingBottom: spacing.md,
        },
        back: { marginRight: spacing.xs, marginBottom: 2 },
        title: { ...theme.text.h1, marginTop: spacing.xxs },
        loader: { marginTop: spacing.lg },
        empty: {
          ...theme.text.body,
          color: theme.colors.textMuted,
          paddingHorizontal: spacing.lg,
          marginTop: spacing.lg,
        },
      }),
    [theme],
  );

  if (!placeDetail) return null;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable
          onPress={closePlace}
          style={styles.back}
          accessibilityRole="button"
          accessibilityLabel="Retour"
          hitSlop={8}
        >
          <Feather name="arrow-left" size={22} color={theme.colors.text} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={theme.text.eyebrow}>Événements</Text>
          <Text style={styles.title}>{place?.name ?? '...'}</Text>
        </View>
      </View>

      {loading ? (
        <ActivityIndicator style={styles.loader} color={theme.colors.text} />
      ) : (
        <FlatList
          data={events}
          keyExtractor={(e) => `event-${e.id}`}
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          ListEmptyComponent={
            <Text style={styles.empty}>
              Aucun événement à venir à cet endroit.
            </Text>
          }
          renderItem={({ item }) => (
            <EventCard
              event={item}
              favorite={isFavorite('event', item.id)}
              onPress={() =>
                openDetail({ type: 'event', id: item.id, origin: 'lieuEvents' })
              }
              onToggleFavorite={() => toggleFavorite('event', item.id)}
              showDate
            />
          )}
        />
      )}
    </View>
  );
}
