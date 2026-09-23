// Palette validée sur le prototype (design-reference.md §1).
export const colors = {
  background: '#FAF6F0',
  card: '#FFFFFF',
  border: '#E5DACB',
  text: '#1F1B16',
  textMuted: '#6B6153',
  accentJournee: '#C1622D',
  accentSoiree: '#2F4858',
  accentRestaurant: '#4B7A6F',
  placeholderEvent: '#EFE3D3',
  placeholderRestaurant: '#E4EBE8',
  overlay: 'rgba(31, 27, 22, 0.35)',
} as const;

export type CategoryKey = 'journee' | 'soiree' | 'restaurant';

export const categoryAccent: Record<CategoryKey, string> = {
  journee: colors.accentJournee,
  soiree: colors.accentSoiree,
  restaurant: colors.accentRestaurant,
};

export const categoryLabel: Record<CategoryKey, string> = {
  journee: 'Journée',
  soiree: 'Soirée',
  restaurant: 'Restaurant',
};
