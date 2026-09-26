import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { radius, spacing, useTheme } from '../theme';
import { PlaceItem } from '../types/api';
import { EventImage } from './EventImage';
import { FavoriteHeart } from './FavoriteHeart';

interface Props {
  place: PlaceItem;
  favorite: boolean;
  onPress: () => void;
  onToggleFavorite: () => void;
}

export function PlaceCard({ place, favorite, onPress, onToggleFavorite }: Props) {
  const { theme } = useTheme();
  const styles = useMemo(
    () =>
      StyleSheet.create({
        card: {
          flexDirection: 'row',
          gap: spacing.md,
          alignItems: 'center',
          padding: spacing.md,
          marginHorizontal: spacing.lg,
          marginBottom: spacing.sm,
          backgroundColor: theme.colors.card,
          borderColor: theme.colors.border,
          borderWidth: 1,
          borderRadius: radius.card,
        },
        thumb: {
          width: 64,
          height: 64,
          borderRadius: 12,
        },
        body: {
          flex: 1,
        },
        name: {
          ...theme.text.bodyStrong,
          fontSize: 16,
          marginBottom: 2,
        },
        meta: {
          ...theme.text.meta,
        },
      }),
    [theme],
  );

  return (
    <Pressable style={styles.card} onPress={onPress} accessibilityRole="button">
      <EventImage
        imageUrl={place.image_url}
        variant="restaurant"
        style={styles.thumb}
        iconSize={22}
      />
      <View style={styles.body}>
        <Text style={styles.name} numberOfLines={2}>
          {place.name}
        </Text>
        <Text style={styles.meta} numberOfLines={1}>
          <Feather name="map-pin" size={12} color={theme.colors.textMuted} />
          {'  '}
          {place.address || 'Adresse non renseignée'}
        </Text>
      </View>
      <FavoriteHeart active={favorite} onPress={onToggleFavorite} size="sm" />
    </Pressable>
  );
}
