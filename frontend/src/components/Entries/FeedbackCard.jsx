import React, { useState } from "react";
import Card from "../UI/Card";
import Badge from "../UI/Badge";
import Button from "../UI/Button";
import TherapyTechniques from "../TherapyTechniques";

const FeedbackCard = ({ analysis, isLoading = false, userContext = "" }) => {
  const [showTechniques, setShowTechniques] = useState(false);
  const [selectedDistortion, setSelectedDistortion] = useState(null);
  if (isLoading) {
    return (
      <Card className="animate-pulse">
        <div className="space-y-3">
          <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded w-1/4"></div>
          <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded w-3/4"></div>
          <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded w-1/2"></div>
        </div>
      </Card>
    );
  }

  if (!analysis || !analysis.distortions) return null;

  const getDistortionColor = (type) => {
    const colors = {
      "Felaketleştirme": "error",
      "Aşırı Genelleme": "warning",
      "Zihin Okuma": "info",
      "Etiketleme": "error",
      "Kişiselleştirme": "info"
    };
    return colors[type] || "default";
  };

  return (
    <Card className="space-y-6">
      <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
        AI Analiz Sonucu
      </h3>

      {analysis.distortions.length > 0 && (
        <div className="space-y-4">
          {analysis.distortions.map((d, index) => (
            <div
              key={index}
              className="p-4 border border-neutral-200 dark:border-neutral-700 rounded-lg bg-neutral-50 dark:bg-neutral-800 space-y-2"
            >
              <div className="flex justify-between items-start">
                <Badge variant={getDistortionColor(d.type)}>{d.type}</Badge>
                <Button
                  onClick={() => {
                    setSelectedDistortion(d.type);
                    setShowTechniques(true);
                  }}
                  variant="secondary"
                  size="sm"
                >
                  💡 Teknikler
                </Button>
              </div>
              <p className="text-sm text-neutral-700 dark:text-neutral-300">
                <strong>İfade:</strong> {d.sentence}
              </p>
              <p className="text-sm text-neutral-700 dark:text-neutral-300">
                <strong>Açıklama:</strong> {d.explanation}
              </p>
              <p className="text-sm text-neutral-700 dark:text-neutral-300">
                <strong>Alternatif:</strong> {d.alternative}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* RAG Techniques Modal */}
      {showTechniques && selectedDistortion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-neutral-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <TherapyTechniques
                distortionType={selectedDistortion}
                userContext={userContext}
                onClose={() => {
                  setShowTechniques(false);
                  setSelectedDistortion(null);
                }}
              />
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};

export default FeedbackCard;
