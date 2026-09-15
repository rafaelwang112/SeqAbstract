# ClockGate — Questions for the Team

## Part 1: My Original Questions

1. What dataset will we need & what data was used in the paper?
2. What tools will we need vs what tools were used in the paper?
3. Is the paper's end goal to compare Claude vs Local LLM efficiency?
4. A benchmark making & a paper is an idea — what really is the benchmark gonna be here?
5. Is this a strong research idea? If not, what are the loopholes?

---

## Part 2: Claude's Answers to These Questions

**1. What dataset will we need, and what did the AutoGate paper use?**
AutoGate didn't build a training dataset — it evaluated on existing real designs: small ones from CVDP/OpenCores/OpenTitan, plus NVDLA, BlackParrot, and two proprietary designs, using Claude Opus 4.7 to write synthetic testbenches. There's no reusable corpus to inherit from them.

For ClockGate, "dataset" means something built from scratch: hand-certified "costumes" (waste + gold + cheat + testbench per hide), then a generator stamps out randomized "instances" from those costumes to hit the 250–500 target. This is the actual novel deliverable — AutoGate has nothing like it.

**2. What tools do we need vs. what did the paper use?**
AutoGate leans on commercial infrastructure: a 3nm-class commercial synthesis library, commercial formal equivalence checking, PrimePower for gate-level power (SAIF traces), plus ML clustering on waveform toggling data.

ClockGate deliberately avoids almost all of that — it uses Yosys/SymbiYosys (open-source, via oss-cad-suite) for equivalence + synthesis checking, Python grader scripts, and eventually Qwen + RL tooling (GRPO-style). ClockGate skips waveform/toggling analysis entirely by planting the waste directly instead of discovering it from traces — the biggest tooling divergence from AutoGate.

**3. Is the paper's end goal to compare Claude vs. a local LLM?**
No. AutoGate benchmarks its agentic framework (using Claude as the rewriting engine) against two other RTL optimization methods, POET and ROVER — all three given the same Claude token budget. There's no local-model comparison in the paper.

The Claude-vs-fine-tuned-Qwen comparison is ClockGate's own contribution, not something borrowed from AutoGate. Worth being precise about this with the team so nobody thinks it's replicating a result AutoGate already reported.

**4. What is the benchmark actually going to be?**
The benchmark = the certified corpus itself, structured as hide → costume → instance, each instance being a piece of wasteful Verilog. The task given to a model (Claude or fine-tuned Qwen) is: rewrite this so the enable is exposed, without hand-inserting the clock-gate cell. Grading is automatic — Yosys equivalence check on the gold rewrite, failure on a "cheat" rewrite, verification the waste truly had no `if`-gated enable. Score = clocked-cycle savings after resynthesis.

**5. Is this a strong research idea, or what are the loopholes?**
Genuinely defensible, but with real risk points worth flagging to the team:

- **Strength**: the gap is real — AutoGate has no public, trainable, reusable corpus and no small on-prem model. That's a legitimate thing to ship that they explicitly didn't.
- **Risk — scale/diversity**: only 3 hides right now. If the held-out set ends up being close variants of the training hides, the "generalization" claim is weak.
- **Risk — no real power validation**: AutoGate measures actual watts on real chips via commercial power analysis. ClockGate's grader checks equivalence + structural presence of a clock-enable, not measured power — a proxy, not the real thing.
- **Risk — task may be too easy for Claude**: these are small, template-shaped rewrites. If Claude solves all 4 costumes near-perfectly zero-shot, the comparison table might just show "Qwen catches up to a ceiling" rather than something dramatic. Worth running the Claude baseline early.
- **Risk — reward hacking**: having someone explicitly try to cheat the grader is smart practice, but it also signals the grader is the single point of failure — a trained model optimizing against it could find degenerate tricks that pass equivalence but don't reflect real skill.

---

## Part 3: Additional Questions Claude thought I Might Have Missed (with explanations)

**1. Train/holdout leakage**
*What "holdout" means:* You train on some examples (the hides you have now), then test on new examples the model has never seen, to check if it actually learned the skill instead of memorizing.
*The worry:* Right now the hides are `identity_binop_zero` (things like `+0` or `<<0` that do nothing) and `stable_copy`/`stable_compute` (assigning the same value repeatedly). If the "new" held-out hide is basically the same trick in a different costume, the test isn't really checking generalization.
*Ask the team:* How different will the holdout hides actually be from what we train on? Are we sure they're not just the same trick in disguise?

**2. Generator correctness**
*What the generator is:* A tool (not yet built) that takes one certified example and auto-creates many randomized copies — different variable names, bit-widths, busy percentages — to scale from 4 examples to hundreds.
*The worry:* Randomizing automatically can break things two ways: (a) the copy is no longer functionally equivalent to the original, or (b) the copy becomes too easy, so easy that Yosys would catch the clock-gating opportunity anyway without any rewrite — making it a useless training example.
*Ask the team:* When the generator makes random copies, how do we make sure each one is still correct, and still hard enough to be a useful example?

**3. Eval metric**
*What this means:* When comparing "Claude vs. our trained Qwen," you need one clear number to declare a winner. Candidates: pass/fail on the grader, amount of clock power/cycles saved, number of tries/turns, or cost (tokens/compute).
*The worry:* If this isn't decided ahead of time, everyone might measure differently and the final comparison won't be fair or consistent.
*Ask the team:* What single number are we going to use to say "Qwen won" or "Claude won"? Should we decide that now?

**4. Timeline realism**
*What this means:* The corpus (250–500 examples) still needs to be built, then the model needs fine-tuning (SFT), then possibly reinforcement learning (RL) on top. That's three big phases, and phase 1 hasn't started yet.
*Ask the team:* Do we actually have time this semester to build the corpus AND fine-tune AND do RL, or should we scope down?

**5. Kill-query due diligence**
*What "kill query" means:* The project doc says if someone finds a paper that already trains a small model on generated clock-gating rewrites, that kills the project's novelty — someone beat us to it.
*The worry:* Has anyone actually done a thorough search for that paper, or is everyone assuming it doesn't exist?
*Ask the team:* Has someone actually done a real search to make sure nobody's already published this exact idea?

**6. Publication target**
*What this means:* Where is this actually being aimed — a workshop, a full conference, or just a class project? Different targets have different deadlines and different bars for completeness.
*Ask the team:* What are we actually aiming to publish this as, and by when? That'll decide how much of the checklist we really need to finish.


phase 1 — Claude baseline on the four costumes you already have
Cheap and high-information. You learn whether the task is hard enough to be a benchmark at all, and you learn what failure looks like, which tells you what a harder hide should do. If Claude is at 100%, you redesign hides now instead of after mass generation.

Phase 2 — hides and generator
Decide whether hide 4 exists (already_at_bound or an idle FSM) or whether three is final. Then build the generator.

The generator must self-validate. Every stamped instance runs through the grader and gets thrown away if it fails — otherwise you get two silent failure modes: instances that aren't equivalent anymore, and instances so easy that Yosys already gates them without any rewrite. Both poison training data and neither is visible by eye at 1000 files.

One honest thing about the 700-1200 target: that's good SFT volume, but instance count isn't diversity. A thousand clones of four costumes is still four costumes, and a reviewer will say so. Volume comes from instances; the claim comes from hides and the holdout. Quote both numbers separately and never let "1200 examples" stand in for "one class of problem."

Phase 3 — training
SFT on training hides only, LoRA on a 3B-8B Coder model. GRPO or RL on the grader reward is the stretch goal, and your own notes already question whether three phases fit in one semester. My read: plan to ship SFT, treat RL as optional, and say so to the professor rather than discovering it in November.

Phase 4 — eval and write-up
Qwen versus Claude on the held-out hide, one metric, same harness for both. That table is the paper.