import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { radius, spacing, useTheme } from '../theme';
import { RestaurantItem } from '../types/api';
import { formatRating } from '../utils/format';
import { FavoriteHeart } from './FavoriteHeart';

interface Props {
  restaurant: RestaurantItem;
  favorite: boolean;
  onPress: () => void;
  onToggleFavorite: () => void;
}

export function RestaurantCard({ restaurant, favorite, onPress, onToggleFavorite }: Props) {
  const { theme } = useTheme();
  const accent = theme.categoryAccent.restaurant;

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
        icon: {
          width: 44,
          height: 44,
          borderRadius: radius.pill,
          borderWidth: 1,
          alignItems: 'center',
          justifyContent: 'center',
        },
        body: {
          flex: 1,
        },
        title: {
          ...theme.text.bodyStrong,
          fontSize: 16,
          marginBottom: 2,
        },
        metaRow: {
          flexDirection: 'row',
          alignItems: 'center',
          gap: 4,
        },
        meta: {
          ...theme.text.meta,
        },
      }),
    [theme],
  );

  return (
    <Pressable style={styles.card} onPress={onPress} accessibilityRole="button">
      <View style={[styles.icon, { borderColor: accent }]}>
        <Feather name="coffee" size={18} color={accent} />
      </View>
      <View style={styles.body}>
        <Text style={styles.title} numberOfLines={2}>
          {restaurant.title}
        </Text>
        <View style={styles.metaRow}>
          <Feather name="star" size={12} color={accent} />
          <Text style={styles.meta}>
            {formatRating(restaurant.rating, restaurant.rating_count)}
            {restaurant.location_name ? ` · ${restaurant.location_name}` : ''}
          </Text>
        </View>
      </View>
      <FavoriteHeart
        active={favorite}
        onPress={onToggleFavorite}
        size="sm"
      />
    </Pressable>
  );
}
