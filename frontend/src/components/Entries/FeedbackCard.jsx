import React from "react";
import Card from "../UI/Card";
import Badge from "../UI/Badge";

const FeedbackCard = ({ analysis, isLoading = false }) => {
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
              <Badge variant={getDistortionColor(d.type)}>{d.type}</Badge>
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
    </Card>
  );
};

export default FeedbackCard;
