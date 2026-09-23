import {
  Fraunces_600SemiBold,
  Fraunces_700Bold,
  useFonts as useFraunces,
} from '@expo-google-fonts/fraunces';
import {
  WorkSans_400Regular,
  WorkSans_500Medium,
  WorkSans_600SemiBold,
  useFonts as useWorkSans,
} from '@expo-google-fonts/work-sans';
import { StatusBar } from 'expo-status-bar';
import React, { useCallback, useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as SplashScreen from 'expo-splash-screen';

import { NavBar } from './src/components/NavBar';
import { DetailScreen } from './src/screens/DetailScreen';
import { FavoritesScreen } from './src/screens/FavoritesScreen';
import { HomeScreen } from './src/screens/HomeScreen';
import { ListScreen } from './src/screens/ListScreen';
import { AppProvider, useApp } from './src/state/AppContext';
import { colors, spacing, text } from './src/theme';

SplashScreen.preventAutoHideAsync().catch(() => {
  // If it's already hidden, that's fine.
});

function ScreenRouter() {
  const { screen, error } = useApp();
  return (
    <View style={styles.root}>
      {error ? (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText} numberOfLines={2}>
            {error}
          </Text>
        </View>
      ) : null}
      <View style={{ flex: 1 }}>
        {screen === 'accueil' && <HomeScreen />}
        {screen === 'liste' && <ListScreen />}
        {screen === 'detail' && <DetailScreen />}
        {screen === 'favoris' && <FavoritesScreen />}
      </View>
      <NavBar />
    </View>
  );
}

export default function App() {
  const [frauncesLoaded] = useFraunces({
    Fraunces_600SemiBold,
    Fraunces_700Bold,
  });
  const [workSansLoaded] = useWorkSans({
    WorkSans_400Regular,
    WorkSans_500Medium,
    WorkSans_600SemiBold,
  });

  const fontsLoaded = frauncesLoaded && workSansLoaded;

  const onLayout = useCallback(async () => {
    if (fontsLoaded) {
      await SplashScreen.hideAsync().catch(() => undefined);
    }
  }, [fontsLoaded]);

  useEffect(() => {
    if (fontsLoaded) {
      SplashScreen.hideAsync().catch(() => undefined);
    }
  }, [fontsLoaded]);

  if (!fontsLoaded) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.safe} edges={['top']} onLayout={onLayout}>
        <StatusBar style="dark" />
        <AppProvider>
          <ScreenRouter />
        </AppProvider>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
  errorBanner: {
    backgroundColor: '#F2E4D5',
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xs,
  },
  errorText: {
    ...text.meta,
    color: colors.text,
  },
});
