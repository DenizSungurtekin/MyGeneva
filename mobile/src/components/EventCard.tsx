import React, { useMemo } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { radius, spacing, useTheme } from '../theme';
import { EventItem } from '../types/api';
import { timeRange } from '../utils/date';
import { EventImage } from './EventImage';
import { FavoriteHeart } from './FavoriteHeart';

interface Props {
  event: EventItem;
  favorite: boolean;
  onPress: () => void;
  onToggleFavorite: () => void;
}

export function EventCard({ event, favorite, onPress, onToggleFavorite }: Props) {
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
        title: {
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
        imageUrl={event.image_url}
        variant="event"
        style={styles.thumb}
        iconSize={22}
      />
      <View style={styles.body}>
        <Text style={styles.title} numberOfLines={2}>
          {event.title}
        </Text>
        <Text style={styles.meta} numberOfLines={1}>
          {[event.location_name || event.address, timeRange(event.date_start, event.date_end)]
            .filter(Boolean)
            .join(' · ')}
        </Text>
      </View>
      <FavoriteHeart active={favorite} onPress={onToggleFavorite} size="sm" />
    </Pressable>
  );
}
