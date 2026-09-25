import { Feather } from '@expo/vector-icons';
import React from 'react';
import { Pressable, StyleSheet, ViewStyle } from 'react-native';

import { radius, useTheme } from '../theme';

interface Props {
  active: boolean;
  onPress: () => void;
  size?: 'sm' | 'md';
  variant?: 'card' | 'overlay';
  style?: ViewStyle;
}

export function FavoriteHeart({ active, onPress, size = 'md', variant = 'card', style }: Props) {
  const { theme } = useTheme();
  const dim = size === 'sm' ? 32 : 40;
  const iconSize = size === 'sm' ? 16 : 20;
  const bg =
    variant === 'overlay'
      ? theme.colors.overlayCircle
      : active
        ? theme.colors.background
        : theme.colors.card;

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
          borderColor: theme.colors.border,
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
        color={active ? theme.colors.favoriteHeart : theme.colors.text}
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
});
