import { Feather } from '@expo/vector-icons';
import React from 'react';
import { Pressable, StyleSheet, ViewStyle } from 'react-native';

import { colors, radius } from '../theme';

interface Props {
  active: boolean;
  onPress: () => void;
  size?: 'sm' | 'md';
  variant?: 'card' | 'overlay';
  style?: ViewStyle;
}

export function FavoriteHeart({ active, onPress, size = 'md', variant = 'card', style }: Props) {
  const dim = size === 'sm' ? 32 : 40;
  const iconSize = size === 'sm' ? 16 : 20;
  const bg =
    variant === 'overlay'
      ? 'rgba(255, 255, 255, 0.92)'
      : active
        ? colors.background
        : colors.card;

  return (
    <Pressable
      onPress={(e) => {
        e.stopPropagation?.();
        onPress();
      }}
      style={[
        styles.base,
        {
          width: dim,
          height: dim,
          borderRadius: dim / 2,
          backgroundColor: bg,
          borderColor: colors.border,
        },
        style,
      ]}
      accessibilityRole="button"
      accessibilityLabel={active ? 'Retirer des favoris' : 'Ajouter aux favoris'}
      hitSlop={8}
    >
      <Feather
        name="heart"
        size={iconSize}
        color={active ? colors.accentJournee : colors.text}
        style={active ? styles.filled : undefined}
      />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: radius.pill,
  },
  filled: {
    // Feather doesn't provide a filled heart — the accent-coloured stroke is
    // the visual signal that the item is favourite. Kept as a hook for a
    // future custom SVG if we want a "filled" variant.
  },
});
