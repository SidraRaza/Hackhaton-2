import { AssistantConfig } from '../lib/types';

class AssistantConfigService {
  private static readonly STORAGE_KEY = 'assistant-config';

  // Get assistant configuration from storage or return default
  static getConfig(): AssistantConfig {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        return {
          ...parsed,
          lastConnectionCheck: new Date(parsed.lastConnectionCheck),
        };
      } catch (error) {
        console.warn('Failed to parse assistant config from localStorage, using defaults');
      }
    }

    // Return default configuration
    return {
      id: 'assistant-default-config',
      serviceEndpoint: process.env.NEXT_PUBLIC_AI_SERVICE_ENDPOINT || 'https://api.openai.com/v1/chat/completions',
      isAvailable: true,
      displayPreferences: {},
      lastConnectionCheck: new Date(),
      status: 'online',
    };
  }

  // Save assistant configuration to storage
  static saveConfig(config: Partial<AssistantConfig>): AssistantConfig {
    const currentConfig = this.getConfig();
    const updatedConfig: AssistantConfig = {
      ...currentConfig,
      ...config,
      lastConnectionCheck: config.lastConnectionCheck || new Date(),
    };

    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(updatedConfig));
    return updatedConfig;
  }

  // Check if the AI service is available
  static async checkServiceAvailability(): Promise<boolean> {
    const config = this.getConfig();

    try {
      // Update the last connection check time
      this.saveConfig({
        lastConnectionCheck: new Date(),
        status: 'online'
      });

      // In a real implementation, this would make an actual API call to check availability
      // For now, we'll simulate the check
      const response = await fetch(config.serviceEndpoint, {
        method: 'GET', // This would typically be a HEAD request or a specific health check endpoint
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const isAvailable = response.ok;
      this.saveConfig({
        isAvailable,
        status: isAvailable ? 'online' : 'error'
      });

      return isAvailable;
    } catch (error) {
      console.error('AI service availability check failed:', error);
      this.saveConfig({
        isAvailable: false,
        status: 'error'
      });
      return false;
    }
  }

  // Update service endpoint
  static updateServiceEndpoint(endpoint: string): AssistantConfig {
    return this.saveConfig({ serviceEndpoint: endpoint });
  }

  // Update display preferences
  static updateDisplayPreferences(preferences: Record<string, any>): AssistantConfig {
    const config = this.getConfig();
    return this.saveConfig({
      displayPreferences: { ...config.displayPreferences, ...preferences }
    });
  }

  // Get the current status of the assistant
  static getStatus(): 'online' | 'offline' | 'error' {
    const config = this.getConfig();
    return config.status;
  }

  // Check if assistant is available
  static isAvailable(): boolean {
    const config = this.getConfig();
    return config.isAvailable;
  }

  // Reset to default configuration
  static resetToDefault(): AssistantConfig {
    const defaultConfig: AssistantConfig = {
      id: 'assistant-default-config',
      serviceEndpoint: process.env.NEXT_PUBLIC_AI_SERVICE_ENDPOINT || 'https://api.openai.com/v1/chat/completions',
      isAvailable: true,
      displayPreferences: {},
      lastConnectionCheck: new Date(),
      status: 'online',
    };

    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(defaultConfig));
    return defaultConfig;
  }
}

export default AssistantConfigService;