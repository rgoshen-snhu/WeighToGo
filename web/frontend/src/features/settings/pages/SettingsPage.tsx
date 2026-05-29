/**
 * Settings page — replaces SettingsPlaceholderPage (DDR-0008, FR-P-1, FR-P-3).
 *
 * Two-section card layout (Units, Notifications) within the existing PageLayout shell.
 * Changes persist immediately on interaction; aria-live region announces "Preferences saved"
 * only after the mutation succeeds (not on optimistic start).
 */

import { Box, Card, CardContent, Container, Typography } from '@mui/material';
import { useCallback, useEffect, useRef, useState } from 'react';

import { usePreferences } from '../../../contexts/PreferencesContext';
import { useUpdatePreference } from '../hooks/useUpdatePreference';
import { NotificationTogglesControl } from '../components/NotificationTogglesControl';
import { UnitPreferenceControl } from '../components/UnitPreferenceControl';

const SAVE_FEEDBACK_MS = 2000;

export function SettingsPage() {
  const { preferences } = usePreferences();
  const { mutate } = useUpdatePreference();
  const [saveMessage, setSaveMessage] = useState('');
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showSaved = useCallback(() => {
    setSaveMessage('Preferences saved');
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setSaveMessage(''), SAVE_FEEDBACK_MS);
  }, []);

  useEffect(
    () => () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    },
    [],
  );

  const handleUnitChange = useCallback(
    (unit: 'lbs' | 'kg') => {
      mutate({ key: 'weight_unit', value: unit }, { onSuccess: showSaved });
    },
    [mutate, showSaved],
  );

  const handleToggleChange = useCallback(
    (key: 'notify_achievement' | 'notify_milestone' | 'notify_streak', value: boolean) => {
      mutate({ key, value }, { onSuccess: showSaved });
    },
    [mutate, showSaved],
  );

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <UnitPreferenceControl value={preferences.weightUnit} onChange={handleUnitChange} />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <NotificationTogglesControl
            notifyAchievement={preferences.notifyAchievement}
            notifyMilestone={preferences.notifyMilestone}
            notifyStreak={preferences.notifyStreak}
            onChange={handleToggleChange}
          />
        </CardContent>
      </Card>

      {/* Polite live region for save confirmation (WCAG 2.1 AA SC 4.1.3) */}
      <Box aria-live="polite" aria-atomic="true" sx={{ mt: 2, minHeight: '1.5em' }}>
        <Typography variant="body2" color="text.secondary">
          {saveMessage}
        </Typography>
      </Box>
    </Container>
  );
}
