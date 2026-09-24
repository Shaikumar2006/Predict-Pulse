type Trend = { text: string; isGood: boolean };

type KpiCardProps = {
  label: string;
  value: string;
  accentColor?: string;
  hero?: boolean;
  trend?: Trend | null;
};

function KpiCard({ label, value, accentColor = "#38BDF8", hero = false, trend }: KpiCardProps) {
  if (hero) {
    return (
      <div className="border-l-4 pl-5 py-2" style={{ borderColor: accentColor }}>
        <p className="text-secondary text-sm mb-1">{label}</p>
        <p className="font-mono text-5xl font-semibold" style={{ color: accentColor }}>{value}</p>
        {trend && <p className={`text-xs mt-2 font-medium ${trend.isGood ? "text-healthy" : "text-critical"}`}>{trend.text}</p>}
      </div>
    );
  }

  return (
    <div className="bg-card border-l-4 py-4 px-5" style={{ borderColor: accentColor }}>
      <p className="text-secondary text-sm mb-1">{label}</p>
      <p className="font-mono text-2xl font-semibold text-primary">{value}</p>
      {trend && <p className={`text-xs mt-2 font-medium ${trend.isGood ? "text-healthy" : "text-critical"}`}>{trend.text}</p>}
    </div>
  );
}

export default KpiCard;