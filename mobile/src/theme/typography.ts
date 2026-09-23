import { TextStyle } from 'react-native';

import { colors } from './colors';

// Poids Fraunces validés : 560–650 (display) → on utilise 600 par défaut.
// Poids Work Sans : 400–600.
export const fonts = {
  display: 'Fraunces_600SemiBold',
  displayBold: 'Fraunces_700Bold',
  bodyRegular: 'WorkSans_400Regular',
  bodyMedium: 'WorkSans_500Medium',
  bodySemi: 'WorkSans_600SemiBold',
} as const;

export const text: Record<string, TextStyle> = {
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
    color: colors.card,
  },
};
