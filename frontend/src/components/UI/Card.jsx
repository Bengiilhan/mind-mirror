export default function Card({ children, className = "" }) {
  return (
    <div className={`bg-white dark:bg-neutral-800 rounded-2xl shadow-md p-6 border border-neutral-200 ${className}`}>
      {children}
    </div>
  );
} 