import React, { useState } from "react";
import Card from "../UI/Card";
import Button from "../UI/Button";
import Badge from "../UI/Badge";
import Modal from "../UI/Modal";
import FeedbackCard from "./FeedbackCard";

const EntryList = ({ entries, onDelete, onUpdate, isLoading = false }) => {
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const getMoodColor = (score) => {
    if (score >= 4) return "success";
    if (score >= 3) return "info";
    if (score >= 2) return "warning";
    return "error";
  };

  const getMoodText = (score) => {
    const moods = {
      1: "Çok Kötü",
      2: "Kötü", 
      3: "Orta",
      4: "İyi",
      5: "Çok İyi"
    };
    return moods[score] || "Belirtilmemiş";
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded w-1/4"></div>
                <div className="h-6 bg-neutral-200 dark:bg-neutral-700 rounded w-16"></div>
              </div>
              <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded w-3/4"></div>
              <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded w-1/2"></div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (!entries || entries.length === 0) {
    return (
      <Card className="text-center py-12">
        <div className="text-neutral-500 dark:text-neutral-400">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-lg font-medium mb-2">Henüz günlük yazısı yok</p>
          <p className="text-sm">İlk günlük yazınızı yazmaya başlayın!</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {entries.map((entry) => (
        <Card key={entry.id} className="hover:shadow-lg transition-shadow">
          <div className="flex justify-between items-start mb-3">
            <div className="flex items-center space-x-2">
              <Badge variant={getMoodColor(entry.mood_score)}>
                {getMoodText(entry.mood_score)}
              </Badge>
              <span className="text-sm text-neutral-500 dark:text-neutral-400">
                {formatDate(entry.created_at)}
              </span>
            </div>
            <div className="flex space-x-2">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => {
                  setSelectedEntry(entry);
                  setIsModalOpen(true);
                }}
              >
                Görüntüle
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => onUpdate(entry)}
              >
                Düzenle
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => onDelete(entry.id)}
                className="text-error-600 hover:text-error-700"
              >
                Sil
              </Button>
            </div>
          </div>
          
          <p className="text-neutral-700 dark:text-neutral-300 line-clamp-3">
            {entry.text.length > 200 
              ? `${entry.text.substring(0, 200)}...` 
              : entry.text
            }
          </p>
        </Card>
      ))}

      {/* Entry Detail Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Günlük Yazısı Detayı"
        size="lg"
      >
        {selectedEntry && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Badge variant={getMoodColor(selectedEntry.mood_score)}>
                {getMoodText(selectedEntry.mood_score)}
              </Badge>
              <span className="text-sm text-neutral-500 dark:text-neutral-400">
                {formatDate(selectedEntry.created_at)}
              </span>
            </div>
            
            <div className="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4">
              <p className="text-neutral-700 dark:text-neutral-300 whitespace-pre-wrap">
                {selectedEntry.text}
              </p>
            </div>

            {selectedEntry.analysis && (
              <div className="border-t border-neutral-200 dark:border-neutral-700 pt-4">
        
                <FeedbackCard 
                  analysis={selectedEntry.analysis} 
                  userContext={selectedEntry.text}
                />
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default EntryList;