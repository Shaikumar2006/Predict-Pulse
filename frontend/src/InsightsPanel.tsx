type Contribution = { label: string; pctAboveBaseline: number };

type InsightsPanelProps = {
  daysToCritical: number | null;
  contributions: Contribution[];
};

function InsightsPanel({ daysToCritical, contributions }: InsightsPanelProps) {
  const sorted = [...contributions].sort((a, b) => b.pctAboveBaseline - a.pctAboveBaseline);

  return (
    <div className="border-l-4 border-ai bg-card py-5 px-5">
      <p className="text-ai font-semibold mb-3">Predictive intelligence</p>

      {daysToCritical !== null && (
        <p className="text-primary text-sm mb-4">
          {daysToCritical === 0
            ? "Already at or above the critical threshold based on current readings."
            : `Trend-based estimate: ~${daysToCritical.toFixed(1)} days to critical threshold if current trend continues.`}
        </p>
      )}

      <p className="text-secondary text-sm mb-2">Contributing factors, vs. healthy baseline</p>
      <div className="space-y-2">
        {sorted.map((c) => (
          <div key={c.label}>
            <div className="flex justify-between text-sm text-primary mb-1">
              <span>{c.label}</span>
              <span className={`font-mono ${c.pctAboveBaseline > 0 ? "text-critical" : "text-healthy"}`}>
                {c.pctAboveBaseline > 0 ? "+" : ""}{c.pctAboveBaseline}%
              </span>
            </div>
            <div className="w-full bg-border h-1.5">
              <div className="bg-ai h-1.5" style={{ width: `${Math.min(100, Math.abs(c.pctAboveBaseline))}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default InsightsPanel;