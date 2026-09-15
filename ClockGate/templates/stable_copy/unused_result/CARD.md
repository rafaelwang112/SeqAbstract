# unused_result — template card

**hide:** `stable_copy`  
**costume:** `unused_result`  
**hide_one_liner:** Flop always loads din; when din already equals q the write does nothing but still clocks.

| | |
|---|---|
| Waste | `q <= din` every cycle |
| Gold | `if (din != q) q <= din` |
| Cheat | `if (din > q)` — looks gated, misses din falling |
| Stimulus | seed 1/16 busy; instances randomize 5–40% |

This is not add-0. Identity comes from a **held bus**, not an operator identity element.

**Grade:** `python3 ClockGate/grader/check_template.py ClockGate/templates/stable_copy/unused_result`
