import { useState, useEffect } from "react";
import EntryList from "../components/Entries/EntryList";
import LoadingSkeleton from "../components/UI/LoadingSkeleton";

export default function Archive() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEntries = async () => {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/entries/", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const data = await res.json();
      setEntries(data);
      setLoading(false);
    };
    fetchEntries();
  }, []);

  return (
    <div className="max-w-2xl mx-auto mt-8 p-4 bg-white dark:bg-gray-800 rounded shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Geçmiş Yazılar</h2>
      {loading ? <LoadingSkeleton /> : <EntryList entries={entries} />}
    </div>
  );
}
