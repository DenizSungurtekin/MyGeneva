const WEEKDAYS = ['dim', 'lun', 'mar', 'mer', 'jeu', 'ven', 'sam'];
const WEEKDAYS_LONG = [
  'dimanche',
  'lundi',
  'mardi',
  'mercredi',
  'jeudi',
  'vendredi',
  'samedi',
];
const MONTHS = [
  'janvier',
  'février',
  'mars',
  'avril',
  'mai',
  'juin',
  'juillet',
  'août',
  'septembre',
  'octobre',
  'novembre',
  'décembre',
];

export function toISODate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

export function addDays(d: Date, days: number): Date {
  const copy = new Date(d);
  copy.setDate(copy.getDate() + days);
  return copy;
}

export function shortDayLabel(d: Date): string {
  return WEEKDAYS[d.getDay()];
}

export function longDayLabel(d: Date): string {
  return `${WEEKDAYS_LONG[d.getDay()]} ${d.getDate()} ${MONTHS[d.getMonth()]}`;
}

export function shortTime(iso: string): string {
  const d = new Date(iso);
  const h = String(d.getHours()).padStart(2, '0');
  const m = String(d.getMinutes()).padStart(2, '0');
  return `${h}h${m}`;
}

export function timeRange(startIso: string, endIso: string | null): string {
  if (!endIso) return shortTime(startIso);
  return `${shortTime(startIso)} – ${shortTime(endIso)}`;
}

export function buildDayStrip(around: Date, before: number, after: number): Date[] {
  const days: Date[] = [];
  for (let i = -before; i <= after; i += 1) {
    days.push(addDays(around, i));
  }
  return days;
}
