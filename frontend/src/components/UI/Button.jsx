export default function Button({ children, variant = "primary", className = "", ...props }) {
  const base = "font-medium transition focus:outline-none focus:ring-2 focus:ring-primary-500";
  const variants = {
    primary: "bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg px-6 py-3 shadow hover:opacity-90",
    secondary: "bg-neutral-100 text-neutral-700 rounded-lg px-6 py-3 shadow hover:bg-neutral-200",
    ghost: "bg-transparent text-neutral-500 rounded-lg px-6 py-3 hover:bg-neutral-100"
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
} 