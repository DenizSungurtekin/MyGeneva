import { Feather, Ionicons } from '@expo/vector-icons';
import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { EventImage } from '../components/EventImage';
import { EventMap } from '../components/EventMap';
import { FavoriteHeart } from '../components/FavoriteHeart';
import { Tag } from '../components/Tag';
import { eventsApi } from '../api/events';
import { restaurantsApi } from '../api/restaurants';
import { useApp } from '../state/AppContext';
import { categoryLabel, radius, spacing, useTheme } from '../theme';
import { EventItem, RestaurantItem } from '../types/api';
import { longDayLabel, timeRange } from '../utils/date';
import { formatRating } from '../utils/format';

export function DetailScreen() {
  const { detail, closeDetail, isFavorite, toggleFavorite } = useApp();
  const { theme } = useTheme();
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

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          flex: 1,
          backgroundColor: theme.colors.background,
        },
        header: {
          position: 'relative',
        },
        hero: {
          height: 240,
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
          backgroundColor: theme.colors.overlayCircle,
          borderWidth: 1,
          borderColor: theme.colors.border,
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
          ...theme.text.h1,
          marginTop: spacing.xs,
          marginBottom: spacing.xs,
        },
        metaRow: {
          flexDirection: 'row',
          alignItems: 'center',
          gap: 6,
        },
        metaText: {
          ...theme.text.meta,
        },
        description: {
          ...theme.text.body,
          color: theme.colors.textSecondary,
          marginTop: spacing.md,
        },
        map: {
          marginTop: spacing.md,
          height: 120,
          backgroundColor: theme.colors.lieuCard,
          borderColor: theme.colors.border,
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
          backgroundColor: theme.colors.card,
          borderWidth: 1,
          borderColor: theme.colors.border,
        },
        buttonPrimary: {
          backgroundColor: theme.colors.accentJournee,
        },
        error: {
          ...theme.text.body,
          color: theme.colors.textMuted,
          padding: spacing.lg,
        },
      }),
    [theme],
  );

  if (!detail) return null;

  const favorite = isFavorite(detail.type, detail.id);
  const accent =
    detail.type === 'restaurant'
      ? theme.categoryAccent.restaurant
      : event?.category === 'soiree'
        ? theme.categoryAccent.soiree
        : theme.categoryAccent.journee;

  const loading = detail.type === 'event' ? !event : !restaurant;

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 140 }}>
        <View style={styles.header}>
          <EventImage
            imageUrl={detail.type === 'event' ? event?.image_url ?? null : restaurant?.image_url ?? null}
            variant={detail.type === 'event' ? 'event' : 'restaurant'}
            style={styles.hero}
            iconSize={32}
          />
          <Pressable
            style={styles.backButton}
            onPress={closeDetail}
            accessibilityRole="button"
            accessibilityLabel="Retour"
          >
            <Feather name="arrow-left" size={20} color={theme.colors.text} />
          </Pressable>
          <FavoriteHeart
            active={favorite}
            onPress={() => toggleFavorite(detail.type, detail.id)}
            variant="overlay"
            style={styles.heart}
          />
        </View>

        {loading ? (
          <ActivityIndicator style={{ marginTop: spacing.xl }} color={theme.colors.text} />
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
              <Feather name="clock" size={14} color={theme.colors.textMuted} />
              <Text style={styles.metaText}>
                {longDayLabel(new Date(event.date_start))} · {timeRange(event.date_start, event.date_end)}
              </Text>
            </View>
            <View style={styles.metaRow}>
              <Feather name="map-pin" size={14} color={theme.colors.textMuted} />
              <Text style={styles.metaText}>{event.location_name || event.address || 'Genève'}</Text>
            </View>
            <Text style={styles.description}>{event.description || 'Pas de description.'}</Text>
            <Section title="Adresse" body={event.address || 'Non renseignée'} />
            <EventMap
              address={event.address || event.location_name || 'Genève'}
              latitude={event.latitude}
              longitude={event.longitude}
            />
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
              <Feather name="map-pin" size={14} color={theme.colors.textMuted} />
              <Text style={styles.metaText}>
                {restaurant.location_name || restaurant.address || 'Genève'}
              </Text>
            </View>
            {restaurant.opening_hours ? (
              <View style={styles.metaRow}>
                <Feather name="clock" size={14} color={theme.colors.textMuted} />
                <Text style={styles.metaText}>{restaurant.opening_hours}</Text>
              </View>
            ) : null}
            <Text style={styles.description}>
              {restaurant.description || 'Pas de description.'}
            </Text>
            <Section title="Adresse" body={restaurant.address || 'Non renseignée'} />
            <EventMap
              address={restaurant.address || restaurant.location_name || 'Genève'}
              latitude={restaurant.latitude}
              longitude={restaurant.longitude}
            />
          </View>
        ) : null}
      </ScrollView>

      <View style={styles.footer}>
        <Pressable
          style={[styles.button, styles.buttonSecondary]}
          onPress={() => {
            const item = detail.type === 'event' ? event : restaurant;
            if (!item) return;
            const target =
              item.latitude != null && item.longitude != null
                ? `${item.latitude},${item.longitude}`
                : (item.address || item.location_name || 'Genève');
            Linking.openURL(
              `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(target)}`,
            ).catch(() => undefined);
          }}
          accessibilityRole="button"
          accessibilityLabel="Ouvrir l'itinéraire vers ce lieu"
        >
          <Feather name="navigation" size={16} color={theme.colors.text} />
          <Text style={[theme.text.button, { color: theme.colors.text }]}>Itinéraire</Text>
        </Pressable>
        <Pressable
          style={[styles.button, styles.buttonPrimary]}
          onPress={() => toggleFavorite(detail.type, detail.id)}
          accessibilityRole="button"
        >
          <Ionicons
            name={favorite ? 'heart' : 'heart-outline'}
            size={18}
            color={theme.colors.ctaText}
          />
          <Text style={theme.text.button}>Favoris</Text>
        </Pressable>
      </View>
    </View>
  );
}

function Section({ title, body }: { title: string; body: string }) {
  const { theme } = useTheme();
  return (
    <View style={{ marginTop: spacing.lg }}>
      <Text style={theme.text.eyebrow}>{title}</Text>
      <Text style={[theme.text.body, { marginTop: spacing.xxs }]}>{body}</Text>
    </View>
  );
}

