import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { type: "Felaketleştirme", count: 3 },
  { type: "Aşırı Genelleme", count: 2 },
  { type: "Kişiselleştirme", count: 1 },
  { type: "Zihin Okuma", count: 2 },
];

export default function DistortionChart() {
  return (
    <div className="mb-8">
      <h3 className="font-semibold mb-2">Çarpıtma Türleri Sıklığı</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="type" stroke="#888" />
          <YAxis allowDecimals={false} stroke="#888" />
          <Tooltip contentStyle={{ background: '#fff', borderRadius: 8 }} />
          <Bar dataKey="count" fill="#2563eb" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
} 