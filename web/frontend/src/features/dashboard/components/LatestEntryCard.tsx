import { Card, CardContent, Skeleton, Typography } from '@mui/material';
import type { WeightEntryRecord } from '../../weight/api/weight-client';
import { usePreferences } from '../../../contexts/PreferencesContext';
import { formatObservationDate, formatWeightInPreferredUnit } from '../../../lib/format';
import type { WeightUnit } from '../../../lib/unit-conversion';

interface LatestEntryCardProps {
  entry: WeightEntryRecord | null | undefined;
  isLoading: boolean;
}

/** Card displaying the user's most recent weight entry. */
export function LatestEntryCard({ entry, isLoading }: LatestEntryCardProps) {
  const { preferences } = usePreferences();
  const preferredUnit = preferences.weightUnit;
  return (
    <Card>
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Latest Entry
        </Typography>
        {isLoading ? (
          <Skeleton variant="text" width="60%" />
        ) : entry ? (
          <>
            <Typography variant="h5">
              {formatWeightInPreferredUnit(
                entry.weight_value,
                entry.weight_unit as WeightUnit,
                preferredUnit,
              )}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatObservationDate(entry.observation_date)}
            </Typography>
          </>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No entries yet.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
