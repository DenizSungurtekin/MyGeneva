import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import { Pressable, StyleProp, StyleSheet, TextInput, View, ViewStyle } from 'react-native';

import { radius, spacing, useTheme } from '../theme';

interface Props {
  value: string;
  onChangeText: (v: string) => void;
  placeholder?: string;
  style?: StyleProp<ViewStyle>;
}

export function SearchInput({
  value,
  onChangeText,
  placeholder = 'Rechercher',
  style,
}: Props) {
  const { theme } = useTheme();
  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          flexDirection: 'row',
          alignItems: 'center',
          gap: spacing.xs,
          paddingHorizontal: spacing.sm,
          paddingVertical: 6,
          borderRadius: radius.pill,
          borderWidth: 1,
          borderColor: theme.colors.border,
          backgroundColor: theme.colors.soft,
        },
        text: {
          flex: 1,
          ...theme.text.meta,
          color: theme.colors.text,
          padding: 0,
        },
      }),
    [theme],
  );

  return (
    <View style={[styles.container, style]}>
      <Feather name="search" size={16} color={theme.colors.textMuted} />
      <TextInput
        style={styles.text}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={theme.colors.textMuted}
        returnKeyType="search"
        autoCorrect={false}
        autoCapitalize="none"
      />
      {value.length > 0 ? (
        <Pressable
          onPress={() => onChangeText('')}
          accessibilityRole="button"
          accessibilityLabel="Effacer la recherche"
          hitSlop={8}
        >
          <Feather name="x" size={16} color={theme.colors.textMuted} />
        </Pressable>
      ) : null}
    </View>
  );
}
