import { Feather } from '@expo/vector-icons';
import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { categoryAccent, colors, radius, spacing, text } from '../theme';
import { EventItem } from '../types/api';
import { timeRange } from '../utils/date';
import { FavoriteHeart } from './FavoriteHeart';

interface Props {
  event: EventItem;
  favorite: boolean;
  onPress: () => void;
  onToggleFavorite: () => void;
}

export function EventCard({ event, favorite, onPress, onToggleFavorite }: Props) {
  const accent = event.category === 'journee' ? categoryAccent.journee : categoryAccent.soiree;
  const iconName = event.category === 'journee' ? 'sun' : 'moon';

  return (
    <Pressable style={styles.card} onPress={onPress} accessibilityRole="button">
      <View style={[styles.icon, { borderColor: accent }]}>
        <Feather name={iconName} size={18} color={accent} />
      </View>
      <View style={styles.body}>
        <Text style={styles.title} numberOfLines={2}>
          {event.title}
        </Text>
        <Text style={styles.meta} numberOfLines={1}>
          {timeRange(event.date_start, event.date_end)} · {event.location_name}
        </Text>
      </View>
      <FavoriteHeart
        active={favorite}
        onPress={onToggleFavorite}
        size="sm"
      />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    gap: spacing.md,
    alignItems: 'center',
    padding: spacing.md,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.sm,
    backgroundColor: colors.card,
    borderColor: colors.border,
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
    ...text.bodyStrong,
    fontSize: 16,
    marginBottom: 2,
  },
  meta: {
    ...text.meta,
  },
});
