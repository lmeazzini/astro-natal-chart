/**
 * Password Reset Service
 * Handles password reset requests and confirmations
 */

import { apiClient } from './api';

export interface PasswordResetRequestResponse {
  message: string;
  success: boolean;
}

export interface PasswordResetConfirmRequest {
  token: string;
  new_password: string;
  password_confirm: string;
}

class PasswordResetService {
  /**
   * Request password reset email
   */
  async requestReset(email: string): Promise<PasswordResetRequestResponse> {
    return apiClient.post<PasswordResetRequestResponse>('/api/v1/password-reset/request', {
      email,
    });
  }

  /**
   * Confirm password reset with token
   */
  async confirmReset(
    token: string,
    newPassword: string,
    passwordConfirm: string
  ): Promise<PasswordResetRequestResponse> {
    return apiClient.post<PasswordResetRequestResponse>('/api/v1/password-reset/confirm', {
      token,
      new_password: newPassword,
      password_confirm: passwordConfirm,
    });
  }
}

export const passwordResetService = new PasswordResetService();
