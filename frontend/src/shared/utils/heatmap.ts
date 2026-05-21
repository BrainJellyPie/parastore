// Max-normalize an integer count grid into [0, 1]. Non-zero cells map into
// [0.3, 1.0] (base 0.3 + 0.7 proportional) so they remain visible under
// HeatmapOverlay; zero cells stay 0.
export function normalizeHeatmap(data: number[][]): number[][] {
  let max = 0;
  for (const row of data) {
    for (const v of row) {
      if (v > max) max = v;
    }
  }
  if (max <= 0) return data;
  return data.map((row) => row.map((v) => (v > 0 ? 0.3 + 0.7 * (v / max) : 0)));
}
