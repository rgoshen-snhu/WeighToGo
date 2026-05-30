import { z } from 'zod';

export const achievementSchema = z.object({
  achievement_id: z.number(),
  goal_id: z.number(),
  achievement_type: z.enum(['goal_reached', 'milestone', 'streak']),
  threshold: z.union([z.string(), z.number()]).nullable(),
  earned_at: z.string(),
});

export const achievementListSchema = z.object({
  items: z.array(achievementSchema),
});

export type AchievementRecord = z.infer<typeof achievementSchema>;
export type AchievementListResponse = z.infer<typeof achievementListSchema>;

/**
 * Parse an achievement threshold to a number for display, or `null` when it is
 * absent or malformed. The schema allows a null threshold (only `goal_reached`
 * legitimately uses it); guarding here keeps a bad milestone/streak row from
 * rendering "NaN" to the user.
 */
export function parseThreshold(threshold: string | number | null): number | null {
  if (threshold === null) return null;
  const value = typeof threshold === 'number' ? threshold : parseFloat(threshold);
  return Number.isNaN(value) ? null : value;
}
