/**
 * Amplitude Analytics service for frontend event tracking.
 *
 * This service provides a simple wrapper around the Amplitude Browser SDK
 * for tracking user events and product analytics.
 *
 * Features:
 * - Event tracking with properties
 * - User identification and properties
 * - Session Replay for debugging and UX analysis
 */

import * as amplitude from '@amplitude/analytics-browser';
import { sessionReplayPlugin } from '@amplitude/plugin-session-replay-browser';

const AMPLITUDE_API_KEY = import.meta.env.VITE_AMPLITUDE_API_KEY || '';
const AMPLITUDE_ENABLED = import.meta.env.VITE_AMPLITUDE_ENABLED === 'true';
const SESSION_REPLAY_SAMPLE_RATE = parseFloat(
  import.meta.env.VITE_SESSION_REPLAY_SAMPLE_RATE || '1'
);

class AmplitudeService {
  private initialized = false;

  constructor() {
    if (AMPLITUDE_ENABLED && AMPLITUDE_API_KEY) {
      // Add Session Replay plugin before initialization
      const sessionReplay = sessionReplayPlugin({
        sampleRate: SESSION_REPLAY_SAMPLE_RATE,
      });
      amplitude.add(sessionReplay);

      amplitude.init(AMPLITUDE_API_KEY, {
        defaultTracking: {
          sessions: true,
          pageViews: true,
          formInteractions: false,
          fileDownloads: false,
        },
      });
      this.initialized = true;
      console.log(
        `[Amplitude] Analytics initialized with Session Replay (sample rate: ${SESSION_REPLAY_SAMPLE_RATE})`
      );
    } else {
      console.log('[Amplitude] Analytics disabled');
    }
  }

  /**
   * Track an event with Amplitude.
   *
   * @param eventName - Name of the event (e.g., "chart_created")
   * @param eventProperties - Optional event properties
   */
  track(
    eventName: string,
    eventProperties?: Record<string, string | number | boolean | string[]>
  ): void {
    if (!this.initialized) return;

    try {
      amplitude.track(eventName, eventProperties);
      console.debug(`[Amplitude] Event tracked: ${eventName}`);
    } catch (error) {
      console.error(`[Amplitude] Failed to track event '${eventName}':`, error);
    }
  }

  /**
   * Identify a user and set user properties.
   *
   * @param userId - User identifier
   * @param userProperties - Optional user properties
   */
  identify(
    userId: string,
    userProperties?: Record<string, string | number | boolean | string[]>
  ): void {
    if (!this.initialized) return;

    try {
      const identifyEvent = new amplitude.Identify();

      if (userProperties) {
        Object.entries(userProperties).forEach(([key, value]) => {
          identifyEvent.set(key, value);
        });
      }

      amplitude.setUserId(userId);
      amplitude.identify(identifyEvent);
      console.debug(`[Amplitude] User identified: ${userId}`);
    } catch (error) {
      console.error(`[Amplitude] Failed to identify user '${userId}':`, error);
    }
  }

  /**
   * Clear user identity (e.g., on logout).
   */
  reset(): void {
    if (!this.initialized) return;

    try {
      amplitude.reset();
      console.debug('[Amplitude] User identity reset');
    } catch (error) {
      console.error('[Amplitude] Failed to reset user identity:', error);
    }
  }

  /**
   * Flush pending events (useful for testing and page navigation).
   */
  async flush(): Promise<void> {
    if (!this.initialized) return Promise.resolve();

    try {
      await amplitude.flush();
    } catch (error) {
      console.error('[Amplitude] Failed to flush events:', error);
    }
  }
}

// Global instance
export const amplitudeService = new AmplitudeService();
