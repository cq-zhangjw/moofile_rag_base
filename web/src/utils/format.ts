// 格式化工具
export function formatBytes(bytes: number): string {
  if (!bytes && bytes !== 0) return '–';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(bytes >= 100 * 1024 * 1024 ? 0 : 1) + ' MB';
  return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB';
}

export function relativeTime(iso: string, locale = 'en'): string {
  const now = Date.now();
  const t = new Date(iso).getTime();
  const diff = Math.max(0, now - t);
  const min = Math.floor(diff / 60000);
  const formatter = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
  if (min < 1) return formatter.format(0, 'second');
  if (min < 60) return formatter.format(-min, 'minute');
  const h = Math.floor(min / 60);
  if (h < 24) return formatter.format(-h, 'hour');
  const d = Math.floor(h / 24);
  if (d < 7) return formatter.format(-d, 'day');
  const date = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function pad2(n: number): string {
  return String(n).padStart(2, '0');
}

export function fmtDateTime(iso?: string | Date): string {
  if (!iso) return '–';
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

export function genId(prefix = 'id'): string {
  return prefix + '_' + Math.random().toString(16).slice(2, 10);
}
