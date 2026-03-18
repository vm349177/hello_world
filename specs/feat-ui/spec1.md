# Feature Spec: Right-Aligned Timestamp in Recent Signups

## Goal
Improve the readability of the "Recent Signups" list by moving the submission timestamp to the right edge of each entry, keeping username/email grouped on the left.

## Current Behavior
- Each signup card stacks `username`, `email`, and the ISO timestamp vertically.
- The timestamp pushes the card taller and makes it harder to scan the column for fresh entries.

## Requirements
1. **Layout**
	- Username (bold) and email remain left-aligned, stacked.
	- Timestamp displays on the same row as the username, aligned to the right edge of the card.
	- When the viewport is narrow (<480px) fall back to stacking timestamp under username to avoid overflow.
2. **Visual Treatment**
	- Timestamp uses a subtle color (e.g., `#475569`) and `0.85rem` font to reduce hierarchy.
	- Cards keep existing padding, border, and spacing to avoid layout shifts.
3. **Data Format**
	- Preserve full ISO string for now; formatting changes (e.g., `Mar 17, 04:20 UTC`) can be tackled separately.
4. **Accessibility**
	- Ensure timestamp text color still meets WCAG AA contrast on white background.

## Implementation Notes
- Wrap username and timestamp in a flex container (`display: flex; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap;`).
- Move timestamp into its own `<span class="signup-time">` element inside the loop.
- Add a mobile media query to switch to column layout (`flex-direction: column; align-items: flex-start;`) when width < 480px.
- Reuse existing font stack; avoid introducing new variables.

## Testing
- Desktop (≥768px): confirm timestamps sit on the same line as usernames, right-aligned, with email on next line.
- Mobile (~375px): ensure layout wraps gracefully with timestamp underneath but still visually separated.
- Regression check: submit form, reload page, verify latest entry shows with new layout.
