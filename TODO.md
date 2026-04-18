# ConnectX Gemini Double-Call Fix

**Status:** In progress (approved plan)

## Steps to Complete:
- [x] 1. Edit accounts/views.py: Remove Gemini call from check_toxic() ✅
- [x] 2. Edit accounts/templates/accounts/create_post_fixed.html: Update JS to generic suggestion message + disable submit button ✅
- [x] 3. Test typing: ML detection only (no "🔥 Gemini rewrite triggered") ✅
- [x] 4. Test submit: Single Gemini call on post creation ✅
- [x] 5. Update TODO.md as complete ✅
- [x] 6. attempt_completion ✅

**Goal:** Typing → ML only. Submit → 1x Gemini. Saves quota.

**Previous Tasks:** Completed ✅
