export function parseTimeToSeconds(timeStr: string): number {
  const [h = 0, m = 0, s = 0] = timeStr.split(":").map(Number);
  return h * 3600 + m * 60 + s;
}

export interface SkuSales {
  sku: string;
  name: string;
  quantity: number;
  revenue: number;
  rackId: string;
}
