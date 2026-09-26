import React, { useMemo } from 'react';
import { ActivityIndicator, FlatList, StyleSheet, Text, View } from 'react-native';

import { PlaceCard } from '../components/PlaceCard';
import { useApp } from '../state/AppContext';
import { spacing, useTheme } from '../theme';

export function PlacesListScreen() {
  const {
    places,
    placesLoading,
    isFavorite,
    toggleFavorite,
    openPlace,
  } = useApp();
  const { theme } = useTheme();

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          flex: 1,
        },
        header: {
          paddingHorizontal: spacing.lg,
          paddingTop: spacing.md,
          marginBottom: spacing.lg,
        },
        title: {
          ...theme.text.h1,
          marginTop: spacing.xxs,
        },
        loader: {
          marginTop: spacing.lg,
        },
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
        <Text style={theme.text.eyebrow}>Où sortir</Text>
        <Text style={styles.title}>Lieux</Text>
      </View>

      {placesLoading ? (
        <ActivityIndicator style={styles.loader} color={theme.colors.text} />
      ) : (
        <FlatList
          data={places}
          keyExtractor={(p) => `place-${p.id}`}
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          ListEmptyComponent={
            <Text style={styles.empty}>
              Aucun lieu pour l'instant. Ils apparaîtront ici dès que des événements y seront listés.
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
