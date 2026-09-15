# Shared template grader

```bash
source ~/oss-cad-suite/environment
python3 ClockGate/grader/check_template.py ClockGate/templates/identity_binop_zero/buried_enable
```

Costume dir: `templates/<hide>/<costume>/` with `config.json`. Same 6-box checks, plus **paper quality** (`family` matches hide folder and is unique across hides, one-line hide on CARD, no hint comments, clever cheat, instance busy 5–40%).

Exit 0 only if **TEMPLATE OK** and **PAPER QUALITY OK**.

Do **not** point this at LLM-dumped RTL until a human has written waste/gold/cheat/tb and the run prints TEMPLATE OK.
