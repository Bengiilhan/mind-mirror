import React from 'react';
import FeedbackCard from './Entries/FeedbackCard';

export default function TestRAG() {
  // Test analiz sonucu
  const testAnalysis = {
    distortions: [
      {
        type: "Felaketleştirme",
        sentence: "İşimi kaybedeceğimi düşünüyorum",
        explanation: "Gelecekte olabilecek en kötü senaryoyu düşünüyorsunuz",
        alternative: "İşimi kaybetme ihtimali var ama bu kesin değil"
      },
      {
        type: "Genelleme",
        sentence: "Herkes beni sevmiyor",
        explanation: "Tek bir olaydan genel sonuç çıkarıyorsunuz",
        alternative: "Bazı kişiler size karşı olumsuz olabilir ama bu herkes için geçerli değil"
      }
    ],
    overall_mood: "kötü"
  };

  const testContext = "Bugün iş yerinde çok kötü bir gün geçirdim. Patronum bana kızdı ve ben artık işimi kaybedeceğimi düşünüyorum. Herkes beni sevmiyor ve ben hiçbir şeyi doğru yapamıyorum.";

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">RAG Test Sayfası</h1>
      <div className="mb-4">
        <h2 className="text-lg font-semibold mb-2">Test Analiz Sonucu:</h2>
        <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
          {JSON.stringify(testAnalysis, null, 2)}
        </pre>
      </div>
      
      <div className="mb-4">
        <h2 className="text-lg font-semibold mb-2">Test Kullanıcı Bağlamı:</h2>
        <p className="bg-gray-100 p-4 rounded">{testContext}</p>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-2">FeedbackCard Test:</h2>
        <FeedbackCard 
          analysis={testAnalysis} 
          userContext={testContext}
        />
      </div>
    </div>
  );
}
