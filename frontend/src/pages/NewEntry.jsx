import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/UI/Card";
import Button from "../components/UI/Button";
import Input from "../components/UI/Input";
import FeedbackCard from "../components/Entries/FeedbackCard";
import LoadingSkeleton from "../components/UI/LoadingSkeleton";

export default function NewEntry() {
  const [text, setText] = useState("");
  const [moodScore, setMoodScore] = useState(3);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
  e.preventDefault();
  console.log("🚀 Form submit başladı");
  
  if (!text.trim()) {
    setError("Lütfen bir günlük yazısı girin.");
    return;
  }

  console.log("📝 Yazı uzunluğu:", text.length);
  setIsAnalyzing(true);
  setError("");

  try {
    console.log("🔑 Token kontrol ediliyor...");
    const token = localStorage.getItem("token");
    console.log("🔑 Token var mı:", !!token);

    console.log("🌐 API çağrısı yapılıyor...");
    const response = await fetch("http://localhost:8000/entries/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`, // ✅ Token ekle
      },
      body: JSON.stringify({
        text: text.trim(),
        mood_score: moodScore,
      }),
    });

    console.log("📡 Response status:", response.status);
    
    if (!response.ok) {
      console.log("❌ Response error:", response.statusText);
      throw new Error("Günlük yazısı kaydedilemedi");
    }

    console.log("✅ Response başarılı, JSON parse ediliyor...");
    const data = await response.json(); // response → entry objesi

    // Gerçek analiz sonucunu al:
    console.log("🔍 Backend'den gelen analiz sonucu:", data.analysis);
    setAnalysis(data.analysis); // ✅ backend'den gelen JSON
    setIsAnalyzing(false);
  } catch (err) {
    console.log("💥 Hata oluştu:", err.message);
    setError(err.message || "Bir hata oluştu.");
    setIsAnalyzing(false);
  }
};


  const getMoodEmoji = (score) => {
    const emojis = ["😢", "😕", "😐", "🙂", "😊"];
    return emojis[score - 1] || "😐";
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
          Yeni Günlük Yazısı
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          Bugün nasıl hissediyorsunuz? Düşüncelerinizi paylaşın ve AI analizi alın.
        </p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Mood Score */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Bugünkü duygudurumunuz (1-5 arası):
            </label>
            <div className="flex items-center justify-between max-w-md mx-auto">
              {[1, 2, 3, 4, 5].map((score) => (
                <button
                  key={score}
                  type="button"
                  onClick={() => setMoodScore(score)}
                  className={`flex flex-col items-center p-3 rounded-xl transition-all ${
                    moodScore === score
                      ? "bg-primary-100 text-primary-600 scale-110"
                      : "text-neutral-400 hover:text-neutral-600"
                  }`}
                >
                  <span className="text-2xl mb-1">{getMoodEmoji(score)}</span>
                  <span className="text-xs font-medium">{score}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Text Input */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Günlük yazınız:
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Bugün yaşadıklarınızı, düşüncelerinizi ve duygularınızı buraya yazın..."
              className="w-full h-48 p-4 border border-neutral-300 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 resize-none"
              required
            />
          </div>

          {error && (
            <div className="text-error-600 text-sm text-center p-3 bg-error-50 dark:bg-error-900/20 rounded-lg">
              {error}
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="ghost"
              onClick={() => navigate("/archive")}
            >
              İptal
            </Button>
            <Button
              type="submit"
              disabled={isAnalyzing || !text.trim()}
              className="min-w-[120px]"
            >
              {isAnalyzing ? "Analiz Ediliyor..." : "Kaydet ve Analiz Et"}
            </Button>
          </div>
        </form>
      </Card>

      {/* Analysis Results */}
      {isAnalyzing && (
        <LoadingSkeleton />
      )}

      {analysis && !isAnalyzing && (
        <FeedbackCard analysis={analysis} userContext={text} />
      )}
    </div>
  );
} 