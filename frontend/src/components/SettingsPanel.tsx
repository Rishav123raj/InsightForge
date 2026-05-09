import { useState } from 'react';
import type { AssistantSettings, UserRole } from '../types/api';

interface SettingsPanelProps {
  settings: AssistantSettings;
  onChange: (settings: AssistantSettings) => void;
}

const roles: UserRole[] = ['analyst', 'leadership', 'marketing'];

export function SettingsPanel({
  settings,
  onChange,
}: SettingsPanelProps) {

  const [isLoading, setIsLoading] = useState(false);

  const [authError, setAuthError] = useState('');

  const validateApiKey = async () => {

    try {

      setIsLoading(true);

      setAuthError('');

      const response = await fetch(
        `${settings.apiBaseUrl}/api/analytics/best-titles?year=${settings.year}`,
        {
          method: 'GET',

          headers: {
            'x-api-key': settings.apiKey,
            'x-user-role': settings.role,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Invalid API key');
      }

      // SUCCESS

      onChange({
        ...settings,
        isAuthenticated: true,
      });

    } catch (error) {

      // FAILURE

      onChange({
        ...settings,
        isAuthenticated: false,
      });

      setAuthError('Invalid API key');

    } finally {

      setIsLoading(false);

    }
  };

  return (

    <section className="panel settings-panel">

      <div className="panel__header">
        <h2>Filters & access</h2>
      </div>

      <label>

        Backend API base URL

        <input
          value={settings.apiBaseUrl}

          onChange={(event) =>
            onChange({
              ...settings,
              apiBaseUrl: event.target.value
            })
          }

          placeholder="http://127.0.0.1:8000"
        />

      </label>

      <label>

        Internal assistant API key

        <div className="api-key-input">

          <input
            type="password"

            value={settings.apiKey}

            disabled={settings.isAuthenticated}

            onChange={(event) =>
              onChange({
                ...settings,
                apiKey: event.target.value,
              })
            }

            placeholder="Enter API key"
          />

          {!settings.isAuthenticated ? (

            <button
              type="button"

              className="connect-btn"

              onClick={validateApiKey}

              disabled={
                isLoading || !settings.apiKey.trim()
              }
            >
              {isLoading ? 'Checking...' : 'Connect'}
            </button>

          ) : (

            <button
              type="button"

              className="unlock-btn"

              onClick={() =>
                onChange({
                  ...settings,
                  isAuthenticated: false,
                  apiKey: '',
                })
              }
            >
              Unlock
            </button>

          )}

        </div>

        {settings.isAuthenticated && (
          <small className="auth-success">
            Authenticated successfully
          </small>
        )}

        {authError && (
          <small className="auth-error">
            {authError}
          </small>
        )}

      </label>

      <div className="field-grid">

        <label>

          Role

          <select
            value={settings.role}

            onChange={(event) =>
              onChange({
                ...settings,
                role: event.target.value as UserRole
              })
            }
          >

            {roles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}

          </select>

        </label>

        <label>

          Year

          <input
            type="number"

            value={settings.year}

            onChange={(event) =>
              onChange({
                ...settings,
                year: Number(event.target.value)
              })
            }
          />

        </label>

        <label>

          Month

          <input
            type="month"

            value={settings.month}

            onChange={(event) =>
              onChange({
                ...settings,
                month: event.target.value
              })
            }
          />

        </label>

      </div>

    </section>
  );
}