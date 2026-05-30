/**
 * Read-only list of a user's past goals (achieved or abandoned) — FR-G-5.
 *
 * Purely presentational: the page owns the data fetch. Each row shows the
 * start → target span, the unit, and an outcome chip (Achieved / Abandoned)
 * derived from `is_achieved`.
 */

import { Box, Chip, List, ListItem, ListItemText, Paper, Typography } from '@mui/material';

import type { GoalRecord } from '../api/goal-client';

interface GoalHistoryListProps {
  /** Past goals (non-active), newest first. */
  goals: GoalRecord[];
}

function outcomeLabel(goal: GoalRecord): string {
  return goal.is_achieved ? 'Achieved' : 'Abandoned';
}

export function GoalHistoryList({ goals }: GoalHistoryListProps) {
  if (goals.length === 0) {
    return (
      <Paper elevation={0} sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">No past goals yet.</Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={1}>
      <List aria-label="Goal history" disablePadding>
        {goals.map((goal) => (
          <ListItem
            key={goal.goal_id}
            secondaryAction={
              <Chip
                size="small"
                color={goal.is_achieved ? 'success' : 'default'}
                label={outcomeLabel(goal)}
              />
            }
            divider
          >
            <ListItemText
              primary={
                <Box component="span">
                  {goal.start_value} → {goal.target_value} {goal.target_unit}
                </Box>
              }
              secondary={goal.goal_type === 'lose' ? 'Lose weight' : 'Gain weight'}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}
