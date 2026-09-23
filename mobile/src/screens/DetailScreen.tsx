import { Feather } from '@expo/vector-icons';
import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { FavoriteHeart } from '../components/FavoriteHeart';
import { Placeholder } from '../components/Placeholder';
import { Tag } from '../components/Tag';
import { eventsApi } from '../api/events';
import { restaurantsApi } from '../api/restaurants';
import { useApp } from '../state/AppContext';
import { categoryAccent, categoryLabel, colors, radius, spacing, text } from '../theme';
import { EventItem, RestaurantItem } from '../types/api';
import { longDayLabel, timeRange } from '../utils/date';
import { formatRating } from '../utils/format';

export function DetailScreen() {
  const { detail, closeDetail, isFavorite, toggleFavorite } = useApp();
  const [event, setEvent] = useState<EventItem | null>(null);
  const [restaurant, setRestaurant] = useState<RestaurantItem | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!detail) return;
    setEvent(null);
    setRestaurant(null);
    setError(null);
    const load = async () => {
      try {
        if (detail.type === 'event') {
          const e = await eventsApi.get(detail.id);
          if (!cancelled) setEvent(e);
        } else {
          const r = await restaurantsApi.get(detail.id);
          if (!cancelled) setRestaurant(r);
        }
      } catch (e) {
        if (!cancelled) setError((e as Error).message);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [detail]);

  if (!detail) return null;

  const favorite = isFavorite(detail.type, detail.id);
  const accent =
    detail.type === 'restaurant'
      ? categoryAccent.restaurant
      : event?.category === 'soiree'
        ? categoryAccent.soiree
        : categoryAccent.journee;

  const loading = detail.type === 'event' ? !event : !restaurant;

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 140 }}>
        <View style={styles.header}>
          <Placeholder
            variant={detail.type === 'event' ? 'event' : 'restaurant'}
            height={240}
            rounded={false}
          />
          <Pressable
            style={styles.backButton}
            onPress={closeDetail}
            accessibilityRole="button"
            accessibilityLabel="Retour"
          >
            <Feather name="arrow-left" size={20} color={colors.text} />
          </Pressable>
          <FavoriteHeart
            active={favorite}
            onPress={() => toggleFavorite(detail.type, detail.id)}
            variant="overlay"
            style={styles.heart}
          />
        </View>

        {loading ? (
          <ActivityIndicator style={{ marginTop: spacing.xl }} color={colors.text} />
        ) : error ? (
          <Text style={styles.error}>{error}</Text>
        ) : detail.type === 'event' && event ? (
          <View style={styles.body}>
            <Tag
              label={categoryLabel[event.category === 'journee' ? 'journee' : 'soiree']}
              color={accent}
            />
            <Text style={styles.title}>{event.title}</Text>
            <View style={styles.metaRow}>
              <Feather name="clock" size={14} color={colors.textMuted} />
              <Text style={styles.metaText}>
                {longDayLabel(new Date(event.date_start))} · {timeRange(event.date_start, event.date_end)}
              </Text>
            </View>
            <View style={styles.metaRow}>
              <Feather name="map-pin" size={14} color={colors.textMuted} />
              <Text style={styles.metaText}>{event.location_name || event.address || 'Genève'}</Text>
            </View>
            <Text style={styles.description}>{event.description || 'Pas de description.'}</Text>
            <Section title="Adresse" body={event.address || 'Non renseignée'} />
            <MapPlaceholder />
          </View>
        ) : restaurant ? (
          <View style={styles.body}>
            <Tag label={categoryLabel.restaurant} color={accent} />
            <Text style={styles.title}>{restaurant.title}</Text>
            <View style={styles.metaRow}>
              <Feather name="star" size={14} color={accent} />
              <Text style={styles.metaText}>
                {formatRating(restaurant.rating, restaurant.rating_count)}
              </Text>
            </View>
            <View style={styles.metaRow}>
              <Feather name="map-pin" size={14} color={colors.textMuted} />
              <Text style={styles.metaText}>
                {restaurant.location_name || restaurant.address || 'Genève'}
              </Text>
            </View>
            {restaurant.opening_hours ? (
              <View style={styles.metaRow}>
                <Feather name="clock" size={14} color={colors.textMuted} />
                <Text style={styles.metaText}>{restaurant.opening_hours}</Text>
              </View>
            ) : null}
            <Text style={styles.description}>
              {restaurant.description || 'Pas de description.'}
            </Text>
            <Section title="Adresse" body={restaurant.address || 'Non renseignée'} />
            <MapPlaceholder />
          </View>
        ) : null}
      </ScrollView>

      <View style={styles.footer}>
        <Pressable style={[styles.button, styles.buttonSecondary]} accessibilityRole="button">
          <Feather name="navigation" size={16} color={colors.text} />
          <Text style={[text.button, { color: colors.text }]}>Itinéraire</Text>
        </Pressable>
        <Pressable
          style={[styles.button, { backgroundColor: accent }]}
          onPress={() => toggleFavorite(detail.type, detail.id)}
          accessibilityRole="button"
        >
          <Feather name="heart" size={16} color={colors.card} />
          <Text style={text.button}>
            {favorite ? 'Ajouté aux favoris' : 'Ajouter aux favoris'}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}

function Section({ title, body }: { title: string; body: string }) {
  return (
    <View style={{ marginTop: spacing.lg }}>
      <Text style={text.eyebrow}>{title}</Text>
      <Text style={[text.body, { marginTop: spacing.xxs }]}>{body}</Text>
    </View>
  );
}

function MapPlaceholder() {
  return (
    <View style={styles.map}>
      <Feather name="map" size={28} color={colors.textMuted} />
      <Text style={[text.meta, { marginTop: spacing.xxs }]}>Carte à venir</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    position: 'relative',
  },
  backButton: {
    position: 'absolute',
    top: spacing.lg,
    left: spacing.lg,
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0.92)',
    borderWidth: 1,
    borderColor: colors.border,
  },
  heart: {
    position: 'absolute',
    top: spacing.lg,
    right: spacing.lg,
  },
  body: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    gap: spacing.xs,
  },
  title: {
    ...text.h1,
    marginTop: spacing.xs,
    marginBottom: spacing.xs,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  metaText: {
    ...text.meta,
  },
  description: {
    ...text.body,
    marginTop: spacing.md,
  },
  map: {
    marginTop: spacing.md,
    height: 120,
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: radius.card,
    alignItems: 'center',
    justifyContent: 'center',
  },
  footer: {
    position: 'absolute',
    left: spacing.lg,
    right: spacing.lg,
    bottom: spacing.lg,
    flexDirection: 'row',
    gap: spacing.sm,
  },
  button: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
    height: 48,
    borderRadius: radius.pill,
  },
  buttonSecondary: {
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
  },
  error: {
    ...text.body,
    color: colors.textMuted,
    padding: spacing.lg,
  },
});
