import React from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { Text } from 'react-native';

import { categoryAccent, CategoryKey, categoryLabel, colors, radius, spacing, text } from '../theme';

const ORDER: CategoryKey[] = ['journee', 'soiree', 'restaurant'];

interface Props {
  value: CategoryKey;
  onChange: (c: CategoryKey) => void;
}

export function CategoryTabs({ value, onChange }: Props) {
  return (
    <View style={styles.container}>
      {ORDER.map((key) => {
        const active = value === key;
        return (
          <Pressable
            key={key}
            onPress={() => onChange(key)}
            style={[
              styles.tab,
              active && { backgroundColor: categoryAccent[key], borderColor: categoryAccent[key] },
            ]}
            accessibilityRole="tab"
            accessibilityState={{ selected: active }}
          >
            <Text style={[styles.label, active && styles.labelActive]}>
              {categoryLabel[key]}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: spacing.xs,
    paddingHorizontal: spacing.lg,
  },
  tab: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.card,
  },
  label: {
    ...text.metaStrong,
    color: colors.text,
  },
  labelActive: {
    color: colors.card,
  },
});
