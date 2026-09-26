import React, { useMemo } from 'react';
import { ActivityIndicator, FlatList, StyleSheet, Text, View } from 'react-native';

import { PlaceCard } from '../components/PlaceCard';
import { SearchInput } from '../components/SearchInput';
import { useApp } from '../state/AppContext';
import { spacing, useTheme } from '../theme';

export function PlacesListScreen() {
  const {
    places,
    placesLoading,
    isFavorite,
    toggleFavorite,
    openPlace,
    placeSearchQuery,
    setPlaceSearchQuery,
  } = useApp();
  const { theme } = useTheme();

  // Backend already sorts by fav_count desc → name asc. On top of that, float
  // the user's own favorites to the top so the personal signal wins.
  const orderedPlaces = useMemo(() => {
    const mine: typeof places = [];
    const others: typeof places = [];
    for (const p of places) {
      if (isFavorite('place', p.id)) mine.push(p);
      else others.push(p);
    }
    return [...mine, ...others];
  }, [places, isFavorite]);

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
        loader: { marginTop: spacing.lg },
        empty: {
          ...theme.text.body,
          color: theme.colors.textMuted,
          textAlign: 'center',
          paddingHorizontal: spacing.xl,
          marginTop: spacing.xl,
        },
      }),
    [theme],
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.titleBlock}>
          <Text style={theme.text.eyebrow}>Où sortir</Text>
          <Text style={styles.title}>Lieux</Text>
        </View>
        <SearchInput
          value={placeSearchQuery}
          onChangeText={setPlaceSearchQuery}
          style={styles.search}
        />
      </View>

      {placesLoading && orderedPlaces.length === 0 ? (
        <ActivityIndicator style={styles.loader} color={theme.colors.text} />
      ) : (
        <FlatList
          data={orderedPlaces}
          keyExtractor={(p) => `place-${p.id}`}
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          keyboardShouldPersistTaps="handled"
          ListEmptyComponent={
            <Text style={styles.empty}>
              {placeSearchQuery.trim().length >= 3
                ? `Aucun lieu ne correspond à "${placeSearchQuery.trim()}".`
                : 'Aucun lieu pour l\'instant.'}
            </Text>
          }
          renderItem={({ item }) => (
            <PlaceCard
              place={item}
              favorite={isFavorite('place', item.id)}
              onPress={() => openPlace({ id: item.id, origin: 'lieu' })}
              onToggleFavorite={() => toggleFavorite('place', item.id)}
            />
          )}
        />
      )}
    </View>
  );
}
