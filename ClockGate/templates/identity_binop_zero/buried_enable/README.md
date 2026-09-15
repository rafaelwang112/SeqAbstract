# Power spike seed — buried-enable accumulator

This is **one template**, not a hunt. ~40 lines of RTL.
Idle is planted. The code shape hides it from auto clock-gating.

## What is planted

`delta` is 0 on most cycles. Adding 0 does not change `acc`.
The wasteful code still **assigns `acc` every cycle**, so synthesis
sees no clock-enable. A human / LLM has to notice "adding 0 is idle"
and rewrite it to `if (delta != 0)`.

## Files

| File | Role |
|---|---|
| `acc_waste.sv` | what the model would see |
| `acc_gated.sv` | answer key (never shown to the model) |
| `tb_acc.sv` | stimulus: `delta` nonzero ~1/16 cycles |
| `verify.py` | the three grader tests |

## How to verify (WSL)

```bash
cd /mnt/c/Users/spank/OneDrive/Desktop/USC/580_Publication
python3 ClockGate/grader/check_template.py ClockGate/templates/identity_binop_zero/buried_enable
```

Needs `iverilog` + `yosys` on PATH (oss-cad-suite).
