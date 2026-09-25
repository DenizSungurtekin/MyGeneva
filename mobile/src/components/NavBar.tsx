import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { spacing, useTheme } from '../theme';
import { ScreenName, useApp } from '../state/AppContext';

const TABS: { key: ScreenName; label: string; icon: keyof typeof Feather.glyphMap }[] = [
  { key: 'accueil', label: 'Accueil', icon: 'home' },
  { key: 'favoris', label: 'Favoris', icon: 'heart' },
];

export function NavBar() {
  const { screen, setScreen } = useApp();
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();
  const active: ScreenName = screen === 'liste' || screen === 'detail' ? 'accueil' : screen;

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          flexDirection: 'row',
          borderTopColor: theme.colors.border,
          borderTopWidth: 1,
          backgroundColor: theme.colors.card,
          paddingTop: spacing.xs,
        },
        tab: {
          flex: 1,
          alignItems: 'center',
          gap: 2,
          paddingVertical: spacing.xs,
        },
        label: {
          ...theme.text.meta,
          fontSize: 11,
          color: theme.colors.navInactive,
        },
        labelActive: {
          color: theme.colors.text,
        },
      }),
    [theme],
  );

  return (
    <View style={[styles.container, { paddingBottom: Math.max(insets.bottom, spacing.sm) }]}>
      {TABS.map((tab) => {
        const isActive = tab.key === active;
        return (
          <Pressable
            key={tab.key}
            onPress={() => setScreen(tab.key)}
            style={styles.tab}
            accessibilityRole="tab"
            accessibilityState={{ selected: isActive }}
          >
            <Feather
              name={tab.icon}
              size={22}
              color={isActive ? theme.colors.text : theme.colors.navInactive}
            />
            <Text style={[styles.label, isActive && styles.labelActive]}>{tab.label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}
