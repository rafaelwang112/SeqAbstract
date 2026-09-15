# idle_shift — template card

**hide:** `identity_binop_zero`  
**costume:** `idle_shift` (same hide as buried_enable, `<< 0` instead of `+ 0`)  
**hide_one_liner:** Flop always does q<<amt; shift by 0 does not change q but still clocks.

| | |
|---|---|
| Waste | `q <= q << amt` always |
| Gold | `if (amt != 0) q <= q << amt` |
| Cheat | `if (amt > 1)` — looks gated, misses `amt == 1` |

Not a fourth hide. Paper count is hide folders.

**Grade:** `python3 ClockGate/grader/check_template.py ClockGate/templates/identity_binop_zero/idle_shift`
