export function formatIdr(amount: number): string {
  const formatted = new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
  }).format(Math.round(amount));
  return `Rp ${formatted}`;
}

export function formatShortHash(hex: string, head = 10, tail = 8): string {
  if (hex.length <= head + tail + 3) return hex;
  return `${hex.slice(0, head)}...${hex.slice(-tail)}`;
}

export function formatPct(val: number, decimals = 1): string {
  return `${val.toFixed(decimals)}%`;
}
