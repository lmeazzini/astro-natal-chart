/**
 * Tests for Amplitude Analytics service (frontend).
 */

import { describe, it, expect, vi, beforeEach, Mock } from 'vitest';
import * as amplitude from '@amplitude/analytics-browser';

// Mock the session replay plugin
vi.mock('@amplitude/plugin-session-replay-browser', () => ({
  sessionReplayPlugin: vi.fn(() => ({})),
}));

// Mock the amplitude module
vi.mock('@amplitude/analytics-browser', () => ({
  init: vi.fn(),
  track: vi.fn(),
  setUserId: vi.fn(),
  identify: vi.fn(),
  reset: vi.fn(),
  flush: vi.fn(() => Promise.resolve()),
  add: vi.fn(),
  Identify: vi.fn().mockImplementation(() => ({
    set: vi.fn(),
  })),
}));

describe('AmplitudeService', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();

    // Clear module cache to reset service instance
    vi.resetModules();

    // Reset environment variables
    delete import.meta.env.VITE_AMPLITUDE_API_KEY;
    delete import.meta.env.VITE_AMPLITUDE_ENABLED;
  });

  describe('Initialization', () => {
    it('should not initialize when disabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'false';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      // Re-import to trigger initialization
      await import('../amplitude');

      expect(amplitude.init).not.toHaveBeenCalled();
    });

    it('should not initialize when API key is missing', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = '';

      await import('../amplitude');

      expect(amplitude.init).not.toHaveBeenCalled();
    });

    it('should initialize when enabled with valid API key', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-api-key';

      await import('../amplitude');

      expect(amplitude.init).toHaveBeenCalledWith('test-api-key', {
        defaultTracking: {
          sessions: true,
          pageViews: true,
          formInteractions: false,
          fileDownloads: false,
        },
      });
    });
  });

  describe('track()', () => {
    it('should not track events when disabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'false';
      const { amplitudeService } = await import('../amplitude');

      amplitudeService.track('test_event');

      expect(amplitude.track).not.toHaveBeenCalled();
    });

    it('should track events when enabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      const { amplitudeService } = await import('../amplitude');

      amplitudeService.track('button_clicked', { button_name: 'submit' });

      expect(amplitude.track).toHaveBeenCalledWith('button_clicked', {
        button_name: 'submit',
      });
    });

    it('should handle tracking errors gracefully', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      (amplitude.track as Mock).mockImplementationOnce(() => {
        throw new Error('Network error');
      });

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { amplitudeService } = await import('../amplitude');

      // Should not throw
      amplitudeService.track('test_event');

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('identify()', () => {
    it('should not identify users when disabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'false';
      const { amplitudeService } = await import('../amplitude');

      amplitudeService.identify('user123', { plan: 'premium' });

      expect(amplitude.setUserId).not.toHaveBeenCalled();
      expect(amplitude.identify).not.toHaveBeenCalled();
    });

    it('should identify users when enabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      const mockIdentify = {
        set: vi.fn(),
      };
      (amplitude.Identify as Mock).mockReturnValueOnce(mockIdentify);

      const { amplitudeService } = await import('../amplitude');

      amplitudeService.identify('user123', { plan: 'premium', locale: 'pt-BR' });

      expect(amplitude.setUserId).toHaveBeenCalledWith('user123');
      expect(mockIdentify.set).toHaveBeenCalledWith('plan', 'premium');
      expect(mockIdentify.set).toHaveBeenCalledWith('locale', 'pt-BR');
      expect(amplitude.identify).toHaveBeenCalledWith(mockIdentify);
    });

    it('should identify users without properties', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      const mockIdentify = {
        set: vi.fn(),
      };
      (amplitude.Identify as Mock).mockReturnValueOnce(mockIdentify);

      const { amplitudeService } = await import('../amplitude');

      amplitudeService.identify('user123');

      expect(amplitude.setUserId).toHaveBeenCalledWith('user123');
      expect(mockIdentify.set).not.toHaveBeenCalled();
      expect(amplitude.identify).toHaveBeenCalledWith(mockIdentify);
    });

    it('should handle identification errors gracefully', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      (amplitude.setUserId as Mock).mockImplementationOnce(() => {
        throw new Error('Network error');
      });

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { amplitudeService } = await import('../amplitude');

      // Should not throw
      amplitudeService.identify('user123');

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('reset()', () => {
    it('should not reset when disabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'false';
      const { amplitudeService } = await import('../amplitude');

      amplitudeService.reset();

      expect(amplitude.reset).not.toHaveBeenCalled();
    });

    it('should reset user identity when enabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      const { amplitudeService } = await import('../amplitude');

      amplitudeService.reset();

      expect(amplitude.reset).toHaveBeenCalled();
    });

    it('should handle reset errors gracefully', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      (amplitude.reset as Mock).mockImplementationOnce(() => {
        throw new Error('Network error');
      });

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { amplitudeService } = await import('../amplitude');

      // Should not throw
      amplitudeService.reset();

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('flush()', () => {
    it('should resolve immediately when disabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'false';
      const { amplitudeService } = await import('../amplitude');

      await amplitudeService.flush();

      expect(amplitude.flush).not.toHaveBeenCalled();
    });

    it('should flush events when enabled', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      const { amplitudeService } = await import('../amplitude');

      await amplitudeService.flush();

      expect(amplitude.flush).toHaveBeenCalled();
    });

    it('should handle flush errors gracefully', async () => {
      import.meta.env.VITE_AMPLITUDE_ENABLED = 'true';
      import.meta.env.VITE_AMPLITUDE_API_KEY = 'test-key';

      (amplitude.flush as Mock).mockImplementationOnce(() => {
        throw new Error('Network error');
      });

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { amplitudeService } = await import('../amplitude');

      // Should not throw
      await amplitudeService.flush();

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });
});
