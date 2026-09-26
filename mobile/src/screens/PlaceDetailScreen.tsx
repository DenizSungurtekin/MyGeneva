import { Feather } from '@expo/vector-icons';
import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { placesApi } from '../api/places';
import { EventImage } from '../components/EventImage';
import { EventMap } from '../components/EventMap';
import { FavoriteHeart } from '../components/FavoriteHeart';
import { useApp } from '../state/AppContext';
import { radius, spacing, useTheme } from '../theme';
import { PlaceItem } from '../types/api';

export function PlaceDetailScreen() {
  const {
    placeDetail,
    closePlace,
    openPlaceEvents,
    isFavorite,
    toggleFavorite,
  } = useApp();
  const { theme } = useTheme();
  const [place, setPlace] = useState<PlaceItem | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!placeDetail) return;
    setPlace(null);
    setError(null);
    placesApi
      .get(placeDetail.id)
      .then((p) => {
        if (!cancelled) setPlace(p);
      })
      .catch((e) => {
        if (!cancelled) setError((e as Error).message);
      });
    return () => {
      cancelled = true;
    };
  }, [placeDetail]);

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: { flex: 1, backgroundColor: theme.colors.background },
        header: { position: 'relative' },
        hero: { height: 240 },
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
        heart: { position: 'absolute', top: spacing.lg, right: spacing.lg },
        body: {
          paddingHorizontal: spacing.lg,
          paddingTop: spacing.lg,
          gap: spacing.xs,
        },
        title: {
          ...theme.text.h1,
          marginTop: spacing.xs,
        },
        description: {
          ...theme.text.body,
          color: theme.colors.textSecondary,
          marginTop: spacing.sm,
        },
        cta: {
          marginTop: spacing.lg,
          marginHorizontal: spacing.lg,
          flexDirection: 'row',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 8,
          paddingVertical: spacing.md,
          borderRadius: radius.pill,
          backgroundColor: theme.colors.accentJournee,
        },
        ctaLabel: {
          ...theme.text.button,
          color: theme.colors.ctaText,
        },
        error: {
          ...theme.text.body,
          color: theme.colors.textMuted,
          padding: spacing.lg,
        },
      }),
    [theme],
  );

  if (!placeDetail) return null;

  const favorite = isFavorite('place', placeDetail.id);

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: spacing.xxl }}>
        <View style={styles.header}>
          <EventImage
            imageUrl={place?.image_url ?? null}
            variant="restaurant"
            style={styles.hero}
            iconSize={32}
          />
          <Pressable
            style={styles.backButton}
            onPress={closePlace}
            accessibilityRole="button"
            accessibilityLabel="Retour"
          >
            <Feather name="arrow-left" size={20} color={theme.colors.text} />
          </Pressable>
          <FavoriteHeart
            active={favorite}
            onPress={() => toggleFavorite('place', placeDetail.id)}
            variant="overlay"
            style={styles.heart}
          />
        </View>

        {!place && !error ? (
          <ActivityIndicator style={{ marginTop: spacing.xl }} color={theme.colors.text} />
        ) : error ? (
          <Text style={styles.error}>{error}</Text>
        ) : place ? (
          <>
            <View style={styles.body}>
              <Text style={styles.title}>{place.name}</Text>
              {place.description ? (
                <Text style={styles.description}>{place.description}</Text>
              ) : null}
            </View>

            <View style={{ paddingHorizontal: spacing.lg }}>
              <EventMap
                address={place.address || place.name}
                latitude={place.latitude}
                longitude={place.longitude}
              />
            </View>

            <Pressable
              style={styles.cta}
              onPress={() => openPlaceEvents({ id: place.id, origin: 'lieuDetail' })}
              accessibilityRole="button"
              accessibilityLabel="Voir les événements de ce lieu"
            >
              <Feather name="calendar" size={16} color={theme.colors.ctaText} />
              <Text style={styles.ctaLabel}>Voir les événements</Text>
            </Pressable>
          </>
        ) : null}
      </ScrollView>
    </View>
  );
}
