import { TextStyle } from 'react-native';

import { CategoryKey } from './colors';

export type ThemeMode = 'light' | 'dark';

export interface ThemeColors {
  background: string;
  canvas: string;
  card: string;
  soft: string;
  border: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  navInactive: string;
  accentJournee: string;
  favoriteHeart: string;
  accentSoiree: string;
  accentRestaurant: string;
  placeholderEvent: string;
  placeholderEventIcon: string;
  placeholderRestaurant: string;
  placeholderRestaurantIcon: string;
  lieuCard: string;
  ctaText: string;
  overlay: string;
  overlayCircle: string;
  // Active selection pill (day picker, category tabs). Light uses terracotta
  // for a warmer feel; dark keeps the plain text/background inversion which
  // already reads well on the very dark canvas.
  activePillBg: string;
  activePillText: string;
}

export interface ThemeFonts {
  display: string;
  displayBold: string;
  bodyRegular: string;
  bodyMedium: string;
  bodySemi: string;
}

export interface ThemeText {
  h1: TextStyle;
  h2: TextStyle;
  h3: TextStyle;
  body: TextStyle;
  bodyStrong: TextStyle;
  meta: TextStyle;
  metaStrong: TextStyle;
  eyebrow: TextStyle;
  button: TextStyle;
}

export interface Theme {
  mode: ThemeMode;
  colors: ThemeColors;
  fonts: ThemeFonts;
  text: ThemeText;
  categoryAccent: Record<CategoryKey, string>;
  statusBarStyle: 'light' | 'dark';
}

const lightColors: ThemeColors = {
  background: '#FAF6F0',
  canvas: '#EDE6DA',
  card: '#FFFFFF',
  soft: '#F0E9DD',
  border: '#E5DACB',
  text: '#1F1B16',
  textSecondary: '#3A342B',
  textMuted: '#6B6153',
  navInactive: '#A79C8B',
  accentJournee: '#C1622D',
  favoriteHeart: '#C1622D',
  accentSoiree: '#2F4858',
  accentRestaurant: '#4B7A6F',
  placeholderEvent: '#EFE3D3',
  placeholderEventIcon: '#B7A98D',
  placeholderRestaurant: '#E4EBE8',
  placeholderRestaurantIcon: '#9FB3AC',
  lieuCard: '#E9E2D2',
  ctaText: '#FFFFFF',
  overlay: 'rgba(31, 27, 22, 0.35)',
  overlayCircle: 'rgba(255, 255, 255, 0.92)',
  activePillBg: '#C1622D',
  activePillText: '#FFFFFF',
};

const darkColors: ThemeColors = {
  background: '#17181C',
  canvas: '#101114',
  card: '#1E2024',
  soft: '#262930',
  border: '#2F323A',
  text: '#F2F3F5',
  textSecondary: '#D6D9DE',
  textMuted: '#9AA0AC',
  navInactive: '#5C6270',
  accentJournee: '#E8A33D',
  favoriteHeart: '#E8607A',
  accentSoiree: '#5C7FA6',
  accentRestaurant: '#F0A202',
  placeholderEvent: '#2A2118',
  placeholderEventIcon: '#5A4A34',
  placeholderRestaurant: '#1D242B',
  placeholderRestaurantIcon: '#3C505F',
  lieuCard: '#1E2024',
  ctaText: '#17181C',
  overlay: 'rgba(0, 0, 0, 0.55)',
  overlayCircle: 'rgba(30, 32, 36, 0.92)',
  // Dark keeps the inversion (bright text over dark bg → dark bg over bright bg).
  activePillBg: '#F2F3F5',
  activePillText: '#17181C',
};

const lightFonts: ThemeFonts = {
  display: 'Fraunces_600SemiBold',
  displayBold: 'Fraunces_700Bold',
  bodyRegular: 'WorkSans_400Regular',
  bodyMedium: 'WorkSans_500Medium',
  bodySemi: 'WorkSans_600SemiBold',
};

const darkFonts: ThemeFonts = {
  display: 'Epilogue_600SemiBold',
  displayBold: 'Epilogue_700Bold',
  bodyRegular: 'HankenGrotesk_400Regular',
  bodyMedium: 'HankenGrotesk_500Medium',
  bodySemi: 'HankenGrotesk_600SemiBold',
};

function buildText(colors: ThemeColors, fonts: ThemeFonts): ThemeText {
  return {
    h1: {
      fontFamily: fonts.display,
      fontSize: 28,
      color: colors.text,
      letterSpacing: -0.3,
    },
    h2: {
      fontFamily: fonts.display,
      fontSize: 22,
      color: colors.text,
      letterSpacing: -0.2,
    },
    h3: {
      fontFamily: fonts.display,
      fontSize: 18,
      color: colors.text,
    },
    body: {
      fontFamily: fonts.bodyRegular,
      fontSize: 15,
      color: colors.text,
      lineHeight: 22,
    },
    bodyStrong: {
      fontFamily: fonts.bodySemi,
      fontSize: 15,
      color: colors.text,
      lineHeight: 22,
    },
    meta: {
      fontFamily: fonts.bodyMedium,
      fontSize: 13,
      color: colors.textMuted,
    },
    metaStrong: {
      fontFamily: fonts.bodySemi,
      fontSize: 13,
      color: colors.textMuted,
    },
    eyebrow: {
      fontFamily: fonts.bodySemi,
      fontSize: 11,
      color: colors.textMuted,
      letterSpacing: 1,
      textTransform: 'uppercase',
    },
    button: {
      fontFamily: fonts.bodySemi,
      fontSize: 15,
      color: colors.ctaText,
    },
  };
}

export const lightTheme: Theme = {
  mode: 'light',
  colors: lightColors,
  fonts: lightFonts,
  text: buildText(lightColors, lightFonts),
  categoryAccent: {
    journee: lightColors.accentJournee,
    soiree: lightColors.accentSoiree,
    restaurant: lightColors.accentRestaurant,
  },
  statusBarStyle: 'dark',
};

export const darkTheme: Theme = {
  mode: 'dark',
  colors: darkColors,
  fonts: darkFonts,
  text: buildText(darkColors, darkFonts),
  categoryAccent: {
    journee: darkColors.accentJournee,
    soiree: darkColors.accentSoiree,
    restaurant: darkColors.accentRestaurant,
  },
  statusBarStyle: 'light',
};
