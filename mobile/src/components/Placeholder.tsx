import { Feather } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { colors, radius } from '../theme';

interface Props {
  variant: 'event' | 'restaurant';
  height?: number;
  rounded?: boolean;
}

export function Placeholder({ variant, height = 200, rounded = true }: Props) {
  const bg = variant === 'event' ? colors.placeholderEvent : colors.placeholderRestaurant;
  const icon = variant === 'event' ? 'image' : 'coffee';
  return (
    <View
      style={[
        styles.container,
        { height, backgroundColor: bg, borderRadius: rounded ? radius.card : 0 },
      ]}
    >
      <Feather name={icon} size={32} color={colors.textMuted} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
});
