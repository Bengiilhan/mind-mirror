import React, { useEffect } from "react";
import Badge from "./Badge";

const Toast = ({ 
  message, 
  type = "info", 
  duration = 5000, 
  onClose, 
  className = "" 
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const typeConfig = {
    success: {
      icon: "✓",
      bgColor: "bg-success-50 border-success-200",
      textColor: "text-success-800",
      iconColor: "text-success-600"
    },
    error: {
      icon: "✕", 
      bgColor: "bg-error-50 border-error-200",
      textColor: "text-error-800",
      iconColor: "text-error-600"
    },
    warning: {
      icon: "⚠",
      bgColor: "bg-warning-50 border-warning-200", 
      textColor: "text-warning-800",
      iconColor: "text-warning-600"
    },
    info: {
      icon: "ℹ",
      bgColor: "bg-primary-50 border-primary-200",
      textColor: "text-primary-800", 
      iconColor: "text-primary-600"
    }
  };

  const config = typeConfig[type];

  return (
    <div className={`fixed top-4 right-4 z-toast max-w-sm w-full ${className}`}>
      <div className={`${config.bgColor} border rounded-xl shadow-lg p-4 flex items-start space-x-3`}>
        <div className={`${config.iconColor} text-lg font-bold flex-shrink-0`}>
          {config.icon}
        </div>
        <div className={`${config.textColor} flex-1 text-sm`}>
          {message}
        </div>
        <button
          onClick={onClose}
          className="text-neutral-400 hover:text-neutral-600 flex-shrink-0"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Toast; 