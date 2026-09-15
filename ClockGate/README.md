# ClockGate

Train a model to **write the `if (en)`** so synthesis can clock-gate. Not a post-synth bug hunt. Not ICG insertion.

Wasteful RTL in → equivalent rewrite with a visible enable → synth infers the gate.

Read [`docs/PROJECT.md`](docs/PROJECT.md) (“What this is”).

```
templates/   hide / costume (see docs/PROJECT.md “How the pieces nest”)
grader/      check_template.py
generator/   instance stamper (later)
corpus/      train / eval / holdout instances (later)
papers/      PDFs and reading notes
runs/        tool logs
```
