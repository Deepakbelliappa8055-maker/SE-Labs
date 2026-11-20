# Lab 4 – VibeCoding: High-Low Card Predictor

Repo assigned: `55_card_predictor`

## Changes
1. **Bug fix:** cards were compared by `rank_str` (text), so `"3" > "10"` and `"K" > "A"`. Now compared by `numeric_rank`.
2. **Win streak multiplier:** each correct guess earns 10 × (streak + 1) points, up to ×5; a wrong guess costs 10 points and resets the streak.
3. **Tie rule:** equal ranks show a yellow **PUSH** and keep score and streak.
4. **Side-by-side reveal:** previous and new card are shown together for 1.2 s; clicks are ignored during the reveal.
5. Suit symbols use a font that contains ♥ ♦ ♣ ♠ so they no longer render as boxes.

## Files
- `55_card_predictor/` – updated code (`python main.py`)
- `Before.mp4` / `After.mp4` – 10-second gameplay before and after the changes
- `LLM_Prompt.pdf` – LLM chat history
