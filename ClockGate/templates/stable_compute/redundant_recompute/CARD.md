# redundant_recompute — template card

**hide:** `stable_compute`  
**costume:** `redundant_recompute`  
**hide_one_liner:** Flop always stores a*b; when a and b are unchanged the product already sits in p but still clocks.

| | |
|---|---|
| Waste | `p <= a * b` every cycle |
| Gold | `if ((a * b) != p) p <= a * b` |
| Cheat | `if (a != 0)` — looks gated, misses a going to 0 with leftover p |
| Stimulus | seed 1/16 busy; instances randomize 5–40% |

This is not add-0 and not a wire copy. Identity comes from **recomputing a function of held inputs**.

**Grade:** `python3 ClockGate/grader/check_template.py ClockGate/templates/stable_compute/redundant_recompute`
