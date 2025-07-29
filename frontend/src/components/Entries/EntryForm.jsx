import { useState } from 'react';

export default function EntryForm({ onSubmit, initialData }) {
  const [text, setText] = useState(initialData?.text || '');
  const [moodScore, setMoodScore] = useState(initialData?.mood_score || '');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ text, mood_score, user_id: 1 })
    setText('');
    setMoodScore('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 border p-4 rounded">
      <div>
        <label htmlFor="entry-text" className="block mb-1 font-bold">Günlük Yazısı</label>
        <textarea
          id="entry-text"
          className="w-full border rounded p-2"
          value={text}
          onChange={e => setText(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="mood-score" className="block mb-1 font-bold">Duygu Puanı</label>
        <input
          id="mood-score"
          type="number"
          min="1"
          max="10"
          className="w-full border rounded p-2"
          value={moodScore}
          onChange={e => setMoodScore(e.target.value)}
          required
        />
      </div>
      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
        {initialData ? 'Güncelle' : 'Ekle'}
      </button>
    </form>
  );
} 