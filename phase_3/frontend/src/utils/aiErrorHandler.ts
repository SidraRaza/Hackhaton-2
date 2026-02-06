// AI Service Error Handler Utility
export class AIErrorHandler {
  /**
   * Handles different types of AI service errors
   * @param error The error object from the AI service call
   * @returns A user-friendly error message
   */
  static handleAIError(error: any): string {
    if (!error) {
      return 'An unknown error occurred with the AI service.';
    }

    // Network errors
    if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
      return 'Unable to connect to the AI service. Please check your internet connection.';
    }

    // Timeout errors
    if (error.code === 'TIMEOUT' || error.message.includes('timeout')) {
      return 'The AI service is taking too long to respond. Please try again.';
    }

    // API limit exceeded
    if (error.status === 429) {
      return 'Too many requests to the AI service. Please wait before trying again.';
    }

    // Unauthorized access
    if (error.status === 401) {
      return 'Authentication required to access the AI service. Please log in.';
    }

    // Service unavailable
    if (error.status === 503 || error.status === 502) {
      return 'The AI service is temporarily unavailable. Please try again later.';
    }

    // Rate limit exceeded
    if (error.status === 429) {
      return 'Rate limit exceeded. Please wait before sending another message.';
    }

    // Other HTTP errors
    if (error.status && error.status >= 400 && error.status < 600) {
      return `AI service error (${error.status}). Please try again later.`;
    }

    // Error message exists
    if (error.message) {
      if (typeof error.message === 'string') {
        if (error.message.toLowerCase().includes('quota')) {
          return 'AI service quota exceeded. Please try again later.';
        }
        if (error.message.toLowerCase().includes('invalid') || error.message.toLowerCase().includes('malformed')) {
          return 'Invalid request to AI service. Please try again.';
        }
      }
      return error.message;
    }

    // Fallback
    return 'An error occurred with the AI service. Please try again.';
  }

  /**
   * Checks if an error indicates that the AI service is unavailable
   * @param error The error object
   * @returns True if the service is unavailable, false otherwise
   */
  static isServiceUnavailable(error: any): boolean {
    if (!error) return false;

    // Network errors
    if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
      return true;
    }

    // Service unavailable
    if (error.status === 503 || error.status === 502) {
      return true;
    }

    // Timeout errors
    if (error.code === 'TIMEOUT' || error.message?.includes('timeout')) {
      return true;
    }

    return false;
  }

  /**
   * Logs AI service errors for debugging
   * @param error The error object
   * @param context Additional context about where the error occurred
   */
  static logError(error: any, context: string = ''): void {
    console.error(`AI Service Error${context ? ` in ${context}` : ''}:`, {
      message: error?.message,
      status: error?.status,
      code: error?.code,
      stack: error?.stack,
      timestamp: new Date().toISOString(),
    });
  }
}