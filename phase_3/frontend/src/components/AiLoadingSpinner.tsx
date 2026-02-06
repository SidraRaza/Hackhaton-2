import React from 'react';

interface AiLoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

const AiLoadingSpinner: React.FC<AiLoadingSpinnerProps> = ({
  size = 'md',
  message = 'AI assistant is loading...',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const messageSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div className={`relative ${sizeClasses[size]}`}>
        {/* Outer ring */}
        <div className={`${sizeClasses[size]} border-2 border-muted rounded-full`}></div>

        {/* Animated inner spinner */}
        <div
          className={`absolute top-0 left-0 ${sizeClasses[size]} border-2 border-transparent border-t-primary rounded-full animate-spin`}
        ></div>
      </div>

      {message && (
        <p className={`mt-2 text-muted-foreground ${messageSizeClasses[size]}`}>
          {message}
        </p>
      )}
    </div>
  );
};

export default AiLoadingSpinner;