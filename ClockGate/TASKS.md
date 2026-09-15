# ClockGate — task list

**Ollie (R1) · Yash (R2) · Tony (R3) · Raf (R4)**

Run everything from the repo root, inside WSL, after `source ~/oss-cad-suite/environment`.

```bash
python3 ClockGate/grader/check_template.py ClockGate/templates/<hide>/<costume>
```

---

## Where we are

**Exists**

- 3 hides, 4 costumes, all TEMPLATE OK + PAPER QUALITY OK

  | Hide | Costume | Waste → gold |
  |---|---|---|
  | `identity_binop_zero` | `buried_enable` | `acc + delta` → `if (delta != 0)` |
  | `identity_binop_zero` | `idle_shift` | `q << amt` → `if (amt != 0)` |
  | `stable_copy` | `unused_result` | `q <= din` → `if (din != q)` |
  | `stable_compute` | `redundant_recompute` | `p <= a*b` → `if ((a*b) != p)` |

- Shared grader: `ClockGate/grader/check_template.py`
- Per-costume `verify.py` and `synth_check.py`

**Does not exist**

- Generator / instances (0 so far)
- Claude baseline log
- Any trained model
- Design Compiler or watt numbers

---

## Rules everyone follows

1. **The grader does not get loosened.** If a costume fails uniqueness, hide class, or cheat strength, either change the hide, leave it failing, or file it under the existing hide folder. No skip flags.
2. `config.family` equals the hide folder name. Costumes of one hide share that family.
3. A second costume is not a second hide. Three hides, four costumes.
4. The model only ever sees the wasteful `.sv`. Gold never goes in a prompt.
5. Say "clock-duty on the planted flop," not watts.

---

## Ollie (R1) — corpus and hides

- [ ] Decide hide 4: spec `already_at_bound` (saturating counter) or an idle-FSM hide, or declare 3 hides final. Candidate must pass the grader unchanged, including `opt_dff -sat` leaving `$adff` on the waste.
- [ ] Write the generator spec: what randomizes (signal names, bit widths, busy percentage inside `instance_busy_range`), and what must stay fixed so the hide survives.
- [ ] Keep every `CARD.md` `hide_one_liner` in sync with `config.json`.
- [ ] Rebuild the missing `ClockGate/docs/PROJECT.md` or repoint the root `README.md`.

## Yash (R2) — adversarial and verification

- [ ] For each of the 4 costumes, write a **new cheat** that looks correct and is not in `{drop_op, hold_q, delete_logic}`. Goal is to find one that the grader wrongly passes.
- [ ] Independently confirm the waste has **no** clock-enable cell after `proc; opt -full; opt_dff -sat` on all 4. Any costume where Yosys infers CE on the waste gets dumped, not patched.
- [ ] Sanity-check the equivalence setup: is `sat -seq 8 -set-init-zero` deep enough for `stable_compute`, where the product takes a cycle to settle?
- [ ] Report anything you think is the same hide wearing two names.

**Done when:** every costume has at least one clever cheat that the grader correctly rejects, and you've written down any hole you found.

## Tony (R3) — literature and Claude baseline

- [ ] **Kill query.** Find any paper that trains or fine-tunes a small model on *generated clock-gating rewrites*. Qwen-for-Verilog-generation does not count. Write down the search terms and the result either way.
- [ ] Check whether AutoGate (arXiv 2606.17461) has a public repo, and whether any part of it is runnable without commercial licenses.
- [ ] Run Claude on all 4 waste files — **waste only, never gold** — and log each attempt against the grader. Pass/fail per costume, number of turns.

**Done when:** we have a Claude baseline table and a documented answer on whether the gap still exists.

## Raf (R4) — automation

- [ ] Headless runner that walks `ClockGate/templates/`, runs the grader on every costume, and prints one pass/fail table.
- [ ] Make it exit non-zero on any failure so it can gate a commit.
- [ ] Capture the clock-duty number per costume into that table instead of reading it out of the log by hand.

**Done when:** one command validates the whole corpus and prints a table we can paste into the paper.

---

## Open decisions (need the whole team)

1. **Eval metric.** One number for "Claude won" vs "Qwen won": grader pass rate, clock-cycle savings, turns, or cost. Pick before anyone runs a baseline.
2. **Holdout plan.** Current thinking is train on hides 1 and 2, hold out hide 3. Is `stable_compute` different enough from `stable_copy` to count as a real holdout, or is that one class?
3. **Scope.** Corpus, then SFT, then RL is three phases and phase 1 is not finished. Do we drop RL this semester?
4. **Publication target and deadline.** Workshop, conference, or class project. This decides how much of the list above actually has to land.
