# buried_enable — template card

**hide:** `identity_binop_zero`  
**costume:** `buried_enable` (canonical: add-0)  
**hide_one_liner:** Flop always does acc+delta; adding 0 does not change acc but still clocks.

| | |
|---|---|
| Waste | `acc <= acc + delta` every cycle |
| Gold | `if (delta != 0) acc <= acc + delta` |
| Cheat | `if (delta > 1)` — looks gated, misses `delta == 1` |
| Stimulus | seed 1/16 busy; instances randomize 5–40% |

**Grade:** `python3 ClockGate/grader/check_template.py ClockGate/templates/identity_binop_zero/buried_enable`
