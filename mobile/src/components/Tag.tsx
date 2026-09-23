import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, text } from '../theme';

interface Props {
  label: string;
  color?: string;
}

export function Tag({ label, color = colors.text }: Props) {
  return (
    <View style={[styles.container, { borderColor: color }]}>
      <Text style={[styles.label, { color }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: radius.pill,
    borderWidth: 1,
    backgroundColor: 'transparent',
  },
  label: {
    ...text.eyebrow,
  },
});
