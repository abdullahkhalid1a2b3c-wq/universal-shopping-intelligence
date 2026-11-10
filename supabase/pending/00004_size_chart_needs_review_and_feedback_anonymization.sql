-- Migration 00004: Size Chart Needs Review Flag & Feedback Anonymization
-- 1. Adds 'needs_review' boolean flag to size_charts for automated feedback-driven quality checks.
-- 2. Relaxes NOT NULL constraint on fit_feedback.user_id to allow anonymized feedback retention upon account deletion.

-- 1. Add needs_review column to size_charts
ALTER TABLE public.size_charts
ADD COLUMN IF NOT EXISTS needs_review BOOLEAN NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_size_charts_needs_review
ON public.size_charts (needs_review)
WHERE needs_review = true;

-- 2. Allow user_id to be NULL in fit_feedback for Right to be Forgotten anonymization
ALTER TABLE public.fit_feedback
ALTER COLUMN user_id DROP NOT NULL;

-- 3. Update foreign key to SET NULL on delete so anonymized feedback is preserved when account is removed
ALTER TABLE public.fit_feedback
DROP CONSTRAINT IF EXISTS fit_feedback_user_id_fkey,
ADD CONSTRAINT fit_feedback_user_id_fkey
    FOREIGN KEY (user_id)
    REFERENCES auth.users(id)
    ON DELETE SET NULL;

