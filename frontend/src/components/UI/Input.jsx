export default function Input({ className = "", ...props }) {
  return (
    <input
      className={`w-full p-3 border border-neutral-200 rounded-lg bg-white dark:bg-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500 transition ${className}`}
      {...props}
    />
  );
} 