import React from "react";

const Badge = ({ 
  children, 
  variant = "default", 
  size = "default", 
  className = "" 
}) => {
  const baseClasses = "inline-flex items-center font-medium";
  
  const sizeClasses = {
    small: "px-2 py-1 text-xs rounded-xl",
    default: "px-3 py-1.5 text-sm rounded-2xl"
  };
  
  const variantClasses = {
    success: "bg-success-100 text-success-600",
    warning: "bg-warning-100 text-warning-600", 
    error: "bg-error-100 text-error-600",
    info: "bg-primary-100 text-primary-600",
    default: "bg-neutral-100 text-neutral-600"
  };

  return (
    <span className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
};

export default Badge; 