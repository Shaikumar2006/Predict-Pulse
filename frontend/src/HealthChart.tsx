import { LineChart, Line, XAxis, YAxis, ReferenceArea, ResponsiveContainer, Tooltip } from "recharts";

type Point = { index: number; healthScore: number };

function HealthChart({ points }: { points: Point[] }) {
  return (
    <div className="bg-card border border-border p-5">
      <p className="text-primary font-semibold mb-3">Health over time</p>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={points}>
          <ReferenceArea y1={70} y2={100} fill="#22C55E" fillOpacity={0.06} />
          <ReferenceArea y1={55} y2={70} fill="#F59E0B" fillOpacity={0.08} />
          <ReferenceArea y1={0} y2={55} fill="#EF4444" fillOpacity={0.06} />
          <XAxis dataKey="index" stroke="#94A3B8" tick={{ fontSize: 11, fontFamily: "IBM Plex Mono" }} />
          <YAxis domain={[0, 100]} stroke="#94A3B8" tick={{ fontSize: 11, fontFamily: "IBM Plex Mono" }} />
          <Tooltip contentStyle={{ backgroundColor: "#111A24", border: "1px solid #22303D", color: "#F1F5F9", fontFamily: "IBM Plex Mono", fontSize: 12 }} />
          <Line type="monotone" dataKey="healthScore" stroke="#38BDF8" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default HealthChart;