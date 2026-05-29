import { z } from 'zod';

const localDateStr = (d = new Date()): string => {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};

const isNotFuture = (dateStr: string): boolean => dateStr <= localDateStr();

export const weightEntrySchema = z.object({
  weight_value: z.coerce
    .number()
    .positive('Weight must be greater than 0.')
    .max(1500, 'Weight must be 1500 or less.'),
  weight_unit: z.enum(['lbs', 'kg'] as const, { message: 'Select lbs or kg.' }),
  observation_date: z
    .string()
    .refine(isNotFuture, { message: 'Observation date cannot be in the future.' }),
  notes: z.string().max(500, 'Notes must be 500 characters or fewer.').optional(),
});

export type WeightEntryFormValues = z.infer<typeof weightEntrySchema>;
