// authHelper.ts - Centralized authentication utilities

export class AuthHelper {
  private static TOKEN_KEY = 'token';
  private static COOKIE_NAME = 'auth_token';

  /**
   * Set authentication token in both localStorage and cookie
   */
  static setToken(token: string): void {
    // Set in localStorage
    localStorage.setItem(this.TOKEN_KEY, token);
    
    // Set in cookie (expires in 7 days)
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + 7);
    document.cookie = `${this.COOKIE_NAME}=${token}; Path=/; Expires=${expiryDate.toUTCString()}; SameSite=Lax`;
  }

  /**
   * Get authentication token from localStorage
   */
  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Clear authentication token from both localStorage and cookie
   */
  static clearToken(): void {
    // Clear localStorage
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('taskFilters');
    
    // Clear cookie by setting expiry to past date
    document.cookie = `${this.COOKIE_NAME}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Perform logout - clear all auth data and redirect to login
   */
  static logout(): void {
    this.clearToken();
    window.location.href = '/login';
  }

  /**
   * Get cookie value by name (for server-side checks)
   */
  static getCookie(name: string): string | null {
    if (typeof document === 'undefined') return null;
    
    const matches = document.cookie.match(
      new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)')
    );
    return matches ? decodeURIComponent(matches[1]) : null;
  }
}

// Export convenience functions
export const setAuthToken = (token: string) => AuthHelper.setToken(token);
export const getAuthToken = () => AuthHelper.getToken();
export const clearAuthToken = () => AuthHelper.clearToken();
export const isAuthenticated = () => AuthHelper.isAuthenticated();
export const logout = () => AuthHelper.logout();