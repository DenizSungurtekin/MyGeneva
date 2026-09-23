export function formatRating(rating: number | null, count: number | null): string {
  if (rating == null) return 'Non noté';
  const stars = rating.toFixed(1);
  if (count == null) return stars;
  const suffix = count > 999 ? `${(count / 1000).toFixed(1).replace('.0', '')}k` : String(count);
  return `${stars} · ${suffix} avis`;
}
