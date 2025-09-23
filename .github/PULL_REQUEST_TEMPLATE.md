# Pull Request Template

<!-- PR Title: Use Conventional Commits (e.g., "fix: correct time calculation in FoodAppCustomer") -->

## Description

<!-- Clearly describe the purpose of this PR. What problem does it solve? -->

**Changes:**

- [ ] Fixes #[ISSUE_NUMBER] (link to issue or code review feedback)
- [ ] Implements: _Briefly describe the feature/fix (e.g., "Refactor Customer
  classes to eliminate DRY violations")_

## Related Issue

<!-- Link to the GitHub issue or code review discussion (e.g., "Addresses code review feedback: DRY violations in Customer classes") -->

- Related to #[ISSUE_NUMBER]
- Flowchart/Design Doc: [Link if applicable]

## Changes Made

<!-- Bullet-point list of key changes -->

- Example:
  - Refactored shared logic in `InHouseCustomer` and `FoodAppCustomer` into base
    `Customer` class.
  - Injected `Config` instance into classes instead of using static variables.

## Testing

<!-- Steps to verify your changes work as intended -->

1. Ran `pytest tests/` and confirmed all tests pass.
1. Tested simulation with [specific scenario, e.g., "50 customers"].
1. Verified [specific behavior, e.g., "No queue overflows occur"].

## Screenshots/Notes

<!-- Add screenshots, logs, or design notes if relevant -->

- Before/After logs:
