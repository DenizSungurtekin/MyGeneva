import { Feather } from '@expo/vector-icons';
import React, { useCallback, useMemo, useState } from 'react';
import { Image, Linking, Pressable, StyleSheet, Text, View } from 'react-native';

import { radius, spacing, useTheme } from '../theme';

interface Props {
  address: string;
  latitude?: number | null;
  longitude?: number | null;
}

const STATIC_MAPS_KEY = (globalThis.process?.env?.EXPO_PUBLIC_GOOGLE_MAPS_STATIC_KEY as
  | string
  | undefined) ?? undefined;
const MAP_HEIGHT = 160;
// Wider than needed and scale=2 → retina-sharp when scaled to card width.
const MAP_WIDTH_PX = 640;
const MAP_HEIGHT_PX = 320;

function staticMapUrl(address: string, latitude?: number | null, longitude?: number | null): string | null {
  if (!STATIC_MAPS_KEY) return null;
  const target =
    latitude != null && longitude != null
      ? `${latitude},${longitude}`
      : (address || '').trim();
  if (!target) return null;
  const q = encodeURIComponent(target);
  return (
    `https://maps.googleapis.com/maps/api/staticmap` +
    `?center=${q}&zoom=15&size=${MAP_WIDTH_PX}x${MAP_HEIGHT_PX}&scale=2` +
    `&markers=color:red%7C${q}&key=${STATIC_MAPS_KEY}`
  );
}

function deepLinkUrl(address: string, latitude?: number | null, longitude?: number | null): string {
  if (latitude != null && longitude != null) {
    return `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`;
  }
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
}

export function EventMap({ address, latitude, longitude }: Props) {
  const { theme } = useTheme();
  const [mapFailed, setMapFailed] = useState(false);
  const mapUrl = useMemo(
    () => staticMapUrl(address, latitude, longitude),
    [address, latitude, longitude],
  );
  const showMap = Boolean(mapUrl) && !mapFailed;

  const styles = useMemo(
    () =>
      StyleSheet.create({
        card: {
          marginTop: spacing.md,
          backgroundColor: theme.colors.lieuCard,
          borderColor: theme.colors.border,
          borderWidth: 1,
          borderRadius: radius.card,
          overflow: 'hidden',
        },
        mapImage: {
          width: '100%',
          height: MAP_HEIGHT,
          backgroundColor: theme.colors.soft,
        },
        body: {
          padding: spacing.md,
          gap: spacing.sm,
        },
        row: {
          flexDirection: 'row',
          alignItems: 'center',
          gap: spacing.sm,
        },
        addressText: {
          ...theme.text.body,
          flex: 1,
          color: theme.colors.text,
        },
        button: {
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'center',
          gap: spacing.xs,
          paddingVertical: spacing.sm,
          paddingHorizontal: spacing.md,
          borderRadius: radius.pill,
          backgroundColor: theme.colors.card,
          borderColor: theme.colors.border,
          borderWidth: 1,
        },
        buttonLabel: {
          ...theme.text.metaStrong,
          color: theme.colors.text,
        },
      }),
    [theme],
  );

  const open = useCallback(() => {
    Linking.openURL(deepLinkUrl(address, latitude, longitude)).catch(() => {
      // No graceful fallback if the OS refuses to open URLs.
    });
  }, [address, latitude, longitude]);

  return (
    <View style={styles.card}>
      {showMap && mapUrl ? (
        <Pressable onPress={open} accessibilityRole="button" accessibilityLabel="Ouvrir dans Google Maps">
          <Image
            source={{ uri: mapUrl }}
            style={styles.mapImage}
            resizeMode="cover"
            onError={() => setMapFailed(true)}
            accessibilityIgnoresInvertColors
          />
        </Pressable>
      ) : null}
      <View style={styles.body}>
        <View style={styles.row}>
          <Feather name="map-pin" size={18} color={theme.colors.text} />
          <Text style={styles.addressText} numberOfLines={2}>
            {address || 'Adresse non renseignée'}
          </Text>
        </View>
        <Pressable
          onPress={open}
          style={styles.button}
          accessibilityRole="button"
          accessibilityLabel="Ouvrir dans Google Maps"
        >
          <Feather name="external-link" size={16} color={theme.colors.text} />
          <Text style={styles.buttonLabel}>Ouvrir dans Maps</Text>
        </Pressable>
      </View>
    </View>
  );
}
