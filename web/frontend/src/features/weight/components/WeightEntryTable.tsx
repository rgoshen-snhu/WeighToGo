/**
 * Data table for displaying the user's weight history.
 *
 * Renders a list of weight entries with Date, Weight, Notes, and Actions
 * columns. Each row has an Edit link and a Delete button.
 */

import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import {
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { Link } from 'react-router-dom';
import type { WeightEntryRecord } from '../api/weight-client';
import { formatObservationDate } from '../../../lib/format';

interface WeightEntryTableProps {
  entries: WeightEntryRecord[];
  /** Called with the entry_id when the user clicks Delete on a row. */
  onDelete: (entryId: number) => void;
}

/**
 * Accessible data table for the weight history list.
 *
 * When entries is empty a brief text message is displayed instead of an empty
 * table (the page itself handles the full EmptyState CTA).
 */
export function WeightEntryTable({ entries, onDelete }: WeightEntryTableProps) {
  if (entries.length === 0) {
    return (
      <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
        No entries to display.
      </Typography>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table aria-label="Weight entry history">
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell align="right">Weight</TableCell>
            <TableCell>Notes</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {entries.map((entry) => (
            <TableRow key={entry.entry_id} hover>
              <TableCell>{formatObservationDate(entry.observation_date)}</TableCell>
              <TableCell align="right">
                {entry.weight_value} {entry.weight_unit}
              </TableCell>
              <TableCell>{entry.notes ?? '—'}</TableCell>
              <TableCell align="center">
                <Button
                  component={Link}
                  to={`/weight/${entry.entry_id}/edit`}
                  aria-label={`Edit entry from ${entry.observation_date}`}
                  variant="outlined"
                  startIcon={<EditIcon />}
                  sx={{ mr: 1 }}
                >
                  Edit
                </Button>
                <Button
                  onClick={() => onDelete(entry.entry_id)}
                  aria-label={`Delete entry from ${entry.observation_date}`}
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
