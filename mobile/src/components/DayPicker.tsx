import React, { useMemo, useRef, useEffect } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, text } from '../theme';
import { buildDayStrip, isSameDay, shortDayLabel } from '../utils/date';

interface Props {
  value: Date;
  onChange: (d: Date) => void;
  before?: number;
  after?: number;
}

export function DayPicker({ value, onChange, before = 3, after = 14 }: Props) {
  const today = useMemo(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  }, []);

  const days = useMemo(() => buildDayStrip(today, before, after), [today, before, after]);

  const scrollRef = useRef<ScrollView>(null);
  useEffect(() => {
    // Center-ish the selected day on mount.
    const index = days.findIndex((d) => isSameDay(d, value));
    if (index >= 0 && scrollRef.current) {
      const PILL_WIDTH = 68;
      scrollRef.current.scrollTo({ x: Math.max(0, (index - 2) * PILL_WIDTH), animated: false });
    }
  }, [days, value]);

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

const PILL_WIDTH = 60;

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.lg,
    gap: spacing.xs,
  },
  pill: {
    width: PILL_WIDTH,
    paddingVertical: spacing.xs,
    borderRadius: radius.chip,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.card,
    alignItems: 'center',
  },
  pillActive: {
    backgroundColor: colors.text,
    borderColor: colors.text,
  },
  weekday: {
    ...text.eyebrow,
    color: colors.textMuted,
  },
  weekdayActive: {
    color: colors.card,
  },
  day: {
    ...text.h3,
    fontSize: 20,
    color: colors.text,
    marginTop: 2,
  },
  dayActive: {
    color: colors.card,
  },
});
