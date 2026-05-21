const PERSONA_PALETTE = [
  "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA502", "#A29BFE",
  "#2ED573", "#FF6B81", "#5352ED", "#FFBE76", "#C56CF0",
  "#1DD1A1", "#FECA57", "#FF7F50", "#6C5CE7", "#26DE81",
  "#F368E0", "#00D2D3", "#E17055", "#0ABDE3", "#F97F51",
];

function hash31(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export function colorForCustomer(customerId: string): string {
  return PERSONA_PALETTE[hash31(customerId) % PERSONA_PALETTE.length]!;
}
