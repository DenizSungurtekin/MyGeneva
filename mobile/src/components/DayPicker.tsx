import React, { useEffect, useMemo, useRef } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { radius, spacing, useTheme } from '../theme';
import { buildDayStrip, isSameDay, shortDayLabel } from '../utils/date';

interface Props {
  value: Date;
  onChange: (d: Date) => void;
  before?: number;
  after?: number;
}

const PILL_WIDTH = 60;

export function DayPicker({ value, onChange, before = 3, after = 7 }: Props) {
  const { theme } = useTheme();
  const today = useMemo(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  }, []);

  const days = useMemo(() => buildDayStrip(today, before, after), [today, before, after]);

  const scrollRef = useRef<ScrollView>(null);
  useEffect(() => {
    const index = days.findIndex((d) => isSameDay(d, value));
    if (index >= 0 && scrollRef.current) {
      const OFFSET_WIDTH = 68;
      scrollRef.current.scrollTo({ x: Math.max(0, (index - 2) * OFFSET_WIDTH), animated: false });
    }
  }, [days, value]);

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          paddingHorizontal: spacing.lg,
          gap: spacing.xs,
        },
        pill: {
          width: PILL_WIDTH,
          paddingVertical: spacing.xs,
          borderRadius: radius.chip,
          borderWidth: 1,
          borderColor: theme.colors.border,
          backgroundColor: theme.colors.soft,
          alignItems: 'center',
        },
        pillActive: {
          backgroundColor: theme.colors.activePillBg,
          borderColor: theme.colors.activePillBg,
        },
        weekday: {
          ...theme.text.eyebrow,
          color: theme.colors.textMuted,
        },
        weekdayActive: {
          color: theme.colors.activePillText,
        },
        day: {
          ...theme.text.h3,
          fontSize: 20,
          color: theme.colors.text,
          marginTop: 2,
        },
        dayActive: {
          color: theme.colors.activePillText,
        },
      }),
    [theme],
  );

  return (
    <ScrollView
      ref={scrollRef}
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {days.map((day) => {
        const active = isSameDay(day, value);
        const isToday = isSameDay(day, today);
        return (
          <Pressable
            key={day.toISOString()}
            onPress={() => onChange(day)}
            style={[styles.pill, active && styles.pillActive]}
            accessibilityRole="button"
            accessibilityLabel={day.toDateString()}
          >
            <Text style={[styles.weekday, active && styles.weekdayActive]}>
              {isToday ? "auj." : shortDayLabel(day)}
            </Text>
            <Text style={[styles.day, active && styles.dayActive]}>{day.getDate()}</Text>
          </Pressable>
        );
      })}
      <View style={{ width: spacing.lg }} />
    </ScrollView>
  );
}
