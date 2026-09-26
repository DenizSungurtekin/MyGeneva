import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useApp } from '../state/AppContext';
import { categoryLabel, radius, spacing, useTheme } from '../theme';
import { EventItem } from '../types/api';
import { timeRange } from '../utils/date';
import { EventImage } from './EventImage';
import { FavoriteHeart } from './FavoriteHeart';

interface Props {
  event: EventItem;
  favorite: boolean;
  onPress: () => void;
  onToggleFavorite: () => void;
  /** Show the [Journée]/[Soirée] chip. Off on screens where the user is
   *  already filtering by category (Home). Kept on mixed-category screens
   *  like Favorites or a place's event list. */
  showCategoryChip?: boolean;
  /** Prefix the meta line with the event's date (dd/mm). Useful when the
   *  screen shows events from multiple days (Favorites, LieuEvents). */
  showDate?: boolean;
}

function formatDayMonth(iso: string): string {
  const d = new Date(iso);
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  return `${dd}/${mm}`;
}

export function EventCard({
  event,
  favorite,
  onPress,
  onToggleFavorite,
  showCategoryChip = true,
  showDate = false,
}: Props) {
  const { theme } = useTheme();
  const { places, openPlace, setSelectedDay, setCategory, setSearchQuery, setScreen } = useApp();

  const place = event.place_id != null ? places.find((p) => p.id === event.place_id) : undefined;

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
        thumb: { width: 64, height: 64, borderRadius: 12 },
        body: { flex: 1 },
        title: {
          ...theme.text.bodyStrong,
          fontSize: 16,
          marginBottom: 4,
        },
        chipRow: {
          flexDirection: 'row',
          flexWrap: 'wrap',
          gap: 6,
          marginBottom: 4,
        },
        chip: {
          flexDirection: 'row',
          alignItems: 'center',
          paddingHorizontal: spacing.sm,
          paddingVertical: 3,
          borderRadius: radius.pill,
          borderWidth: 1,
        },
        chipLabel: {
          ...theme.text.eyebrow,
          fontSize: 10,
        },
        meta: {
          ...theme.text.meta,
        },
      }),
    [theme],
  );

  const categoryColor =
    event.category === 'soiree'
      ? theme.categoryAccent.soiree
      : theme.categoryAccent.journee;

  const onPressCategoryChip = () => {
    // Take the user to the Home feed pre-filtered on this event's day + category.
    setSelectedDay(new Date(event.date_start));
    setCategory(event.category);
    setSearchQuery('');
    setScreen('accueil');
  };

  const onPressPlaceChip = () => {
    if (place) {
      openPlace({ id: place.id, origin: 'accueil' });
    }
  };

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
        <View style={styles.chipRow}>
          {showCategoryChip ? (
            <Pressable
              onPress={(e) => {
                e.stopPropagation?.();
                onPressCategoryChip();
              }}
              style={[styles.chip, { borderColor: categoryColor }]}
              accessibilityRole="button"
              accessibilityLabel={`Voir ${categoryLabel[event.category]}`}
            >
              <Text style={[styles.chipLabel, { color: categoryColor }]}>
                {categoryLabel[event.category]}
              </Text>
            </Pressable>
          ) : null}
          {place ? (
            <Pressable
              onPress={(e) => {
                e.stopPropagation?.();
                onPressPlaceChip();
              }}
              style={[styles.chip, { borderColor: theme.colors.textMuted }]}
              accessibilityRole="button"
              accessibilityLabel={`Voir le lieu ${place.name}`}
            >
              <Feather name="map-pin" size={10} color={theme.colors.textMuted} />
              <Text
                style={[
                  styles.chipLabel,
                  { color: theme.colors.textMuted, marginLeft: 4 },
                ]}
                numberOfLines={1}
              >
                {place.name}
              </Text>
            </Pressable>
          ) : null}
        </View>
        <Text style={styles.meta} numberOfLines={1}>
          {[
            showDate ? formatDayMonth(event.date_start) : null,
            timeRange(event.date_start, event.date_end),
          ]
            .filter(Boolean)
            .join(' · ')}
        </Text>
      </View>
      <FavoriteHeart active={favorite} onPress={onToggleFavorite} size="sm" />
    </Pressable>
  );
}
