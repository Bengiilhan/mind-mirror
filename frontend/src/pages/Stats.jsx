import MoodChart from "../components/Stats/MoodChart";
import DistortionChart from "../components/Stats/DistortionChart";

export default function Stats() {
  return (
    <div className="max-w-3xl mx-auto mt-8 p-4 bg-white dark:bg-gray-800 rounded shadow-lg">
      <h2 className="text-2xl font-bold mb-4">İstatistikler</h2>
      <MoodChart />
      <DistortionChart />
    </div>
  );
}
