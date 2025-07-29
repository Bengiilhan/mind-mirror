import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { date: "2024-06-01", mood: 2 },
  { date: "2024-06-02", mood: 3 },
  { date: "2024-06-03", mood: 4 },
  { date: "2024-06-04", mood: 5 },
  { date: "2024-06-05", mood: 3 },
  { date: "2024-06-06", mood: 4 },
];

export default function MoodChart() {
  return (
    <div className="mb-8">
      <h3 className="font-semibold mb-2">Duygudurum Değişimi</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" stroke="#888" />
          <YAxis domain={[1, 5]} stroke="#888" />
          <Tooltip contentStyle={{ background: '#fff', borderRadius: 8 }} />
          <Line type="monotone" dataKey="mood" stroke="#2563eb" strokeWidth={3} dot={{ r: 5 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
} 