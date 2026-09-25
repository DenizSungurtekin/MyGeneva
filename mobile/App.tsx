import {
  Epilogue_600SemiBold,
  Epilogue_700Bold,
  useFonts as useEpilogue,
} from '@expo-google-fonts/epilogue';
import {
  Fraunces_600SemiBold,
  Fraunces_700Bold,
  useFonts as useFraunces,
} from '@expo-google-fonts/fraunces';
import {
  HankenGrotesk_400Regular,
  HankenGrotesk_500Medium,
  HankenGrotesk_600SemiBold,
  useFonts as useHankenGrotesk,
} from '@expo-google-fonts/hanken-grotesk';
import {
  WorkSans_400Regular,
  WorkSans_500Medium,
  WorkSans_600SemiBold,
  useFonts as useWorkSans,
} from '@expo-google-fonts/work-sans';
import { StatusBar } from 'expo-status-bar';
import React, { useCallback, useEffect, useMemo } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as SplashScreen from 'expo-splash-screen';

import { NavBar } from './src/components/NavBar';
import { DetailScreen } from './src/screens/DetailScreen';
import { FavoritesScreen } from './src/screens/FavoritesScreen';
import { HomeScreen } from './src/screens/HomeScreen';
import { ListScreen } from './src/screens/ListScreen';
import { AppProvider, useApp } from './src/state/AppContext';
import { spacing, ThemeProvider, useTheme } from './src/theme';

SplashScreen.preventAutoHideAsync().catch(() => {
  // If it's already hidden, that's fine.
});

function ScreenRouter() {
  const { screen, error } = useApp();
  const { theme } = useTheme();
  const styles = useMemo(
    () =>
      StyleSheet.create({
        root: {
          flex: 1,
          backgroundColor: theme.colors.background,
        },
        errorBanner: {
          backgroundColor: theme.colors.soft,
          borderBottomColor: theme.colors.border,
          borderBottomWidth: 1,
          paddingHorizontal: spacing.lg,
          paddingVertical: spacing.xs,
        },
        errorText: {
          ...theme.text.meta,
          color: theme.colors.text,
        },
      }),
    [theme],
  );
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

function Shell() {
  const { theme } = useTheme();
  const styles = useMemo(
    () =>
      StyleSheet.create({
        safe: {
          flex: 1,
          backgroundColor: theme.colors.background,
        },
      }),
    [theme],
  );
  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <StatusBar style={theme.statusBarStyle} />
      <AppProvider>
        <ScreenRouter />
      </AppProvider>
    </SafeAreaView>
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
  const [epilogueLoaded] = useEpilogue({
    Epilogue_600SemiBold,
    Epilogue_700Bold,
  });
  const [hankenLoaded] = useHankenGrotesk({
    HankenGrotesk_400Regular,
    HankenGrotesk_500Medium,
    HankenGrotesk_600SemiBold,
  });

  const fontsLoaded = frauncesLoaded && workSansLoaded && epilogueLoaded && hankenLoaded;

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
      <ThemeProvider initialMode="light">
        <View style={{ flex: 1 }} onLayout={onLayout}>
          <Shell />
        </View>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
