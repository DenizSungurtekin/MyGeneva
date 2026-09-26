import React, { useMemo } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { categoryLabel, CategoryKey, radius, spacing, useTheme } from '../theme';

// Restaurant tab intentionally hidden — the feature isn't ready yet.
// Backend endpoints, model, and detail path stay in place so the tab can be
// re-enabled with a single line when we bring restaurants back (probably as
// "restaurants near this event" contextual, not a standalone browse).
const ORDER: CategoryKey[] = ['journee', 'soiree'];

interface Props {
  value: CategoryKey;
  onChange: (c: CategoryKey) => void;
}

export function CategoryTabs({ value, onChange }: Props) {
  const { theme } = useTheme();
  const styles = useMemo(
    () =>
      StyleSheet.create({
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
          borderColor: theme.colors.border,
          backgroundColor: theme.colors.soft,
        },
        tabActive: {
          backgroundColor: theme.colors.text,
          borderColor: theme.colors.text,
        },
        label: {
          ...theme.text.metaStrong,
          color: theme.colors.text,
        },
        labelActive: {
          color: theme.colors.background,
        },
      }),
    [theme],
  );

  return (
    <View style={styles.container}>
      {ORDER.map((key) => {
        const active = value === key;
        return (
          <Pressable
            key={key}
            onPress={() => onChange(key)}
            style={[styles.tab, active && styles.tabActive]}
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
