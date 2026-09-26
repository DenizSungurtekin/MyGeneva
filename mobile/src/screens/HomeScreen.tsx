import { Feather } from '@expo/vector-icons';
import React, { useMemo } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { CategoryTabs } from '../components/CategoryTabs';
import { DayPicker } from '../components/DayPicker';
import { EventCard } from '../components/EventCard';
import { RestaurantCard } from '../components/RestaurantCard';
import { SectionHeader } from '../components/SectionHeader';
import { useApp } from '../state/AppContext';
import { radius, spacing, useTheme } from '../theme';
import { EventItem, RestaurantItem } from '../types/api';
import { longDayLabel } from '../utils/date';

type FeedItem = EventItem | RestaurantItem;

export function HomeScreen() {
  const {
    selectedDay,
    setSelectedDay,
    category,
    setCategory,
    eventFeed,
    eventFeedLoading,
    restaurants,
    restaurantsLoading,
    isFavorite,
    toggleFavorite,
    openDetail,
    searchQuery,
    setSearchQuery,
  } = useApp();
  const { theme, mode, toggle } = useTheme();

  // Restaurant tab is currently hidden (CategoryTabs.ORDER); the branch
  // here stays so bringing it back is a one-line switch.
  const isRestaurant = category === 'restaurant';
  const data: FeedItem[] = isRestaurant ? restaurants : eventFeed;
  const isLoading = isRestaurant ? restaurantsLoading : eventFeedLoading;
  const trimmedSearch = searchQuery.trim();
  const searchActive = trimmedSearch.length >= 3;

  const styles = useMemo(
    () =>
      StyleSheet.create({
        content: {
          paddingTop: spacing.md,
          paddingBottom: spacing.xxl,
        },
        header: {
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          paddingHorizontal: spacing.lg,
          marginBottom: spacing.md,
        },
        headerText: {
          flex: 1,
        },
        headerTitle: {
          ...theme.text.h1,
          marginTop: spacing.xxs,
          textTransform: 'capitalize',
        },
        themeToggle: {
          width: 40,
          height: 40,
          borderRadius: 20,
          borderWidth: 1,
          borderColor: theme.colors.border,
          backgroundColor: theme.colors.soft,
          alignItems: 'center',
          justifyContent: 'center',
          marginLeft: spacing.sm,
          marginTop: 2,
        },
        filterRow: {
          flexDirection: 'row',
          alignItems: 'center',
          gap: spacing.sm,
          paddingHorizontal: spacing.lg,
          marginTop: spacing.md,
        },
        searchInput: {
          flex: 1,
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
        searchText: {
          flex: 1,
          ...theme.text.meta,
          color: theme.colors.text,
          padding: 0,
        },
        loader: {
          marginTop: spacing.lg,
        },
        emptyText: {
          ...theme.text.body,
          color: theme.colors.textMuted,
          paddingHorizontal: spacing.lg,
          marginTop: spacing.md,
        },
      }),
    [theme],
  );

  const header = (
    <View>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text style={theme.text.eyebrow}>Aujourd'hui à Genève</Text>
          <Text style={styles.headerTitle}>{longDayLabel(selectedDay)}</Text>
        </View>
        <Pressable
          onPress={toggle}
          style={styles.themeToggle}
          accessibilityRole="button"
          accessibilityLabel={mode === 'dark' ? 'Passer en thème clair' : 'Passer en thème sombre'}
          hitSlop={6}
        >
          <Feather
            name={mode === 'dark' ? 'sun' : 'moon'}
            size={18}
            color={theme.colors.text}
          />
        </Pressable>
      </View>

      <DayPicker value={selectedDay} onChange={setSelectedDay} />

      <View style={styles.filterRow}>
        <CategoryTabs value={category} onChange={setCategory} paddingHorizontal={0} />
        <View style={styles.searchInput}>
          <Feather name="search" size={16} color={theme.colors.textMuted} />
          <TextInput
            style={styles.searchText}
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder="Rechercher"
            placeholderTextColor={theme.colors.textMuted}
            returnKeyType="search"
            autoCorrect={false}
            autoCapitalize="none"
          />
          {searchQuery.length > 0 ? (
            <Pressable
              onPress={() => setSearchQuery('')}
              accessibilityRole="button"
              accessibilityLabel="Effacer la recherche"
              hitSlop={8}
            >
              <Feather name="x" size={16} color={theme.colors.textMuted} />
            </Pressable>
          ) : null}
        </View>
      </View>

      <SectionHeader title="Pour Toi" />
    </View>
  );

  // Single tree: FlatList is mounted whether we're loading, empty, or filled.
  // Switching between View and FlatList on loading transitions was remounting
  // the DayPicker + CategoryTabs + TextInput inside the header — dropping
  // keyboard focus after each keystroke and flickering the day pills on
  // category switch. Keeping the same tree preserves component identity.
  return (
    <FlatList
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
      ListHeaderComponent={header}
      keyboardShouldPersistTaps="handled"
      data={data}
      keyExtractor={(item) => `${isRestaurant ? 'r' : 'e'}-${item.id}`}
      ListEmptyComponent={
        isLoading ? (
          <ActivityIndicator style={styles.loader} color={theme.colors.text} />
        ) : (
          <Text style={styles.emptyText}>
            {searchActive
              ? `Aucun événement ne contient "${trimmedSearch}" ce jour-là.`
              : 'Rien de prévu pour ce moment-là. Change de jour ou reviens plus tard.'}
          </Text>
        )
      }
      renderItem={({ item }) => {
        if (isRestaurant) {
          const r = item as RestaurantItem;
          return (
            <RestaurantCard
              restaurant={r}
              favorite={isFavorite('restaurant', r.id)}
              onPress={() =>
                openDetail({ type: 'restaurant', id: r.id, origin: 'accueil' })
              }
              onToggleFavorite={() => toggleFavorite('restaurant', r.id)}
            />
          );
        }
        const e = item as EventItem;
        return (
          <EventCard
            event={e}
            favorite={isFavorite('event', e.id)}
            onPress={() => openDetail({ type: 'event', id: e.id, origin: 'accueil' })}
            onToggleFavorite={() => toggleFavorite('event', e.id)}
            showCategoryChip={false}
          />
        );
      }}
    />
  );
}
