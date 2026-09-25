import React, { useMemo } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { radius, spacing, useTheme } from '../theme';

interface Props {
  label: string;
  color?: string;
}

export function Tag({ label, color }: Props) {
  const { theme } = useTheme();
  const resolvedColor = color ?? theme.colors.text;
  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          alignSelf: 'flex-start',
          paddingHorizontal: spacing.sm,
          paddingVertical: 4,
          borderRadius: radius.pill,
          borderWidth: 1,
          backgroundColor: 'transparent',
        },
        label: {
          ...theme.text.eyebrow,
        },
      }),
    [theme],
  );
  return (
    <View style={[styles.container, { borderColor: resolvedColor }]}>
      <Text style={[styles.label, { color: resolvedColor }]}>{label}</Text>
    </View>
  );
}
