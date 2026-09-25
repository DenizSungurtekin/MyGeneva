import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';

import { radius, useTheme } from '../theme';

interface Props {
  variant: 'event' | 'restaurant';
  height?: number;
  rounded?: boolean;
}

export function Placeholder({ variant, height = 200, rounded = true }: Props) {
  const { theme } = useTheme();
  const bg =
    variant === 'event' ? theme.colors.placeholderEvent : theme.colors.placeholderRestaurant;
  const iconColor =
    variant === 'event'
      ? theme.colors.placeholderEventIcon
      : theme.colors.placeholderRestaurantIcon;
  const icon = variant === 'event' ? 'image' : 'coffee';
  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        },
      }),
    [],
  );
  return (
    <View
      style={[
        styles.container,
        { height, backgroundColor: bg, borderRadius: rounded ? radius.card : 0 },
      ]}
    >
      <Feather name={icon} size={32} color={iconColor} />
    </View>
  );
}
