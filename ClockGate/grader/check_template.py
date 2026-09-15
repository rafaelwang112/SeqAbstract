#!/usr/bin/env python3
"""Grade one ClockGate template directory (config.json).

Usage:
  python3 check_template.py /path/to/templates/<hide>/<costume>
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

IVERILOG = os.environ.get("IVERILOG", "iverilog")
VVP = os.environ.get("VVP", "vvp")
YOSYS = os.environ.get("YOSYS", "yosys")
FF_RE = re.compile(r"\$adffe|\$dffe|\$adff\b|\$dff\b|\$_DFFE|\$_SDFFE|\$_DFF_")
BANNED = re.compile(
    r"\b(idle|wasteful|waste|gating|clken|clk_en|clock_gate|ungated|timeout)\b",
    re.I,
)
WEAK_CHEATS = {"drop_op", "hold_q", "delete_logic", ""}


def load_cfg(tdir: Path) -> dict:
    p = tdir / "config.json"
    if not p.exists():
        raise SystemExit(f"missing {p}")
    return json.loads(p.read_text())


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stdout + p.stderr)
        raise SystemExit(f"command failed: {' '.join(cmd)}")
    return p


def sim(tdir: Path, cfg: dict, rtl: Path, tag: str) -> Path:
    out_vvp = tdir / f"_{tag}.vvp"
    vcd = tdir / f"_{tag}.vcd"
    tb = tdir / cfg["files"]["tb"]
    run(
        [IVERILOG, "-g2012", "-o", str(out_vvp), str(rtl), str(tb)],
        tdir,
    )
    dump = tdir / "dump.vcd"
    if dump.exists():
        dump.unlink()
    run([VVP, str(out_vvp)], tdir)
    if not dump.exists():
        raise SystemExit(f"no VCD from {tag}")
    dump.replace(vcd)
    return vcd


def parse_vcd(path: Path, cfg: dict):
    v = cfg["vcd"]
    want = {v["clk"], v["rst_n"], v["busy"], v["data"]}
    id_map = {}
    with path.open() as f:
        for line in f:
            if line.startswith("$enddefinitions"):
                break
            m = re.match(r"\$var\s+\w+\s+(\d+)\s+(\S+)\s+(\w+)", line)
            if m and m.group(3) in want:
                id_map[m.group(2)] = m.group(3)

    vals = {n: 0 for n in want}
    samples = []
    prev_clk = 0
    clk, rstn, busy, data = v["clk"], v["rst_n"], v["busy"], v["data"]
    with path.open() as f:
        in_dump = False
        for line in f:
            if line.startswith("$dumpvars"):
                in_dump = True
                continue
            if line.startswith("$end") and in_dump:
                in_dump = False
                continue
            if line.startswith("#") or not line.strip() or line.startswith("$"):
                continue
            line = line.strip()
            if line[0] in "01":
                sid, val = line[1:], int(line[0])
            elif line[0] in "bB":
                bits, sid = line[1:].split()
                val = int(bits.replace("x", "0").replace("z", "0"), 2)
            else:
                continue
            name = id_map.get(sid)
            if name is None:
                continue
            if name == clk:
                if prev_clk == 0 and val == 1 and vals[rstn] == 1:
                    samples.append((vals[busy], vals[data]))
                prev_clk = val
            vals[name] = val
    return samples


def stats(samples, busy_nonzero: bool):
    n = len(samples)
    busy = sum(1 for b, _ in samples if (b != 0 if busy_nonzero else b))
    toggles = 0
    prev = None
    for _, d in samples:
        if prev is not None and d != prev:
            toggles += 1
        prev = d
    return {
        "cycles": n,
        "busy": busy,
        "idle": n - busy,
        "data_toggles": toggles,
    }


def yosys_equiv(tdir: Path, gold: Path, gate: Path, top: str) -> bool:
    script = f"""
        read_verilog -sv {gold.as_posix()}
        rename {top} gold
        read_verilog -sv {gate.as_posix()}
        rename {top} gate
        prep
        miter -equiv gold gate miter
        hierarchy -top miter
        flatten
        async2sync
        sat -seq 8 -verify -prove trigger 0 -set-init-zero
    """
    p = subprocess.run(
        [YOSYS, "-p", script], cwd=tdir, capture_output=True, text=True
    )
    text = p.stdout + p.stderr
    if p.returncode != 0:
        err = [ln for ln in text.splitlines() if "ERROR" in ln]
        if err:
            print("  yosys:", err[-1])
    return p.returncode == 0


def yosys_synth(tdir: Path, rtl: str, top: str, extra: str) -> str:
    script = f"""
        read_verilog -sv {rtl}
        hierarchy -top {top}
        proc
        opt -full
        {extra}
        stat
    """
    p = subprocess.run(
        [YOSYS, "-p", script], cwd=tdir, capture_output=True, text=True
    )
    return p.stdout + p.stderr


def has_ce(text: str) -> bool:
    return bool(re.search(r"\$adffe|\$dffe|\$_DFFE|\$_SDFFE", text))


def extract_stat(text: str, top: str) -> str:
    out, grab = [], False
    for ln in text.splitlines():
        if ln.startswith(f"=== {top}"):
            grab = True
        if grab:
            out.append(ln)
        if grab and ln.strip().startswith("End of"):
            break
    return "\n".join(out[-20:])


def hide_name(tdir: Path) -> str:
    """Costume lives at templates/<hide>/<costume>/."""
    return tdir.parent.name


def other_hide_families(tdir: Path) -> list[tuple[str, str, str]]:
    """Families used in *other* hide folders (same hide's costumes do not count)."""
    root = tdir.parent.parent
    my_hide = hide_name(tdir)
    out = []
    for cfgp in root.glob("*/*/config.json"):
        other_hide = cfgp.parent.parent.name
        if other_hide.startswith("_") or other_hide == my_hide:
            continue
        other = json.loads(cfgp.read_text())
        fam = other.get("family")
        if fam:
            out.append((other.get("name", cfgp.parent.name), fam, other_hide))
    return out


def paper_quality(tdir: Path, cfg: dict, waste_txt: str) -> list[str]:
    """Bars that make a paper, not just a passing seed. Empty list = pass."""
    fails = []
    name = cfg.get("name", tdir.name)
    fam = (cfg.get("family") or "").strip()
    hide = (cfg.get("hide_one_liner") or "").strip()
    cheat = (cfg.get("cheat_kind") or "").strip()
    br = cfg.get("instance_busy_range")

    if not fam:
        fails.append("missing config.family (one class name, e.g. identity_binop_zero)")
    if len(hide) < 20:
        fails.append("missing/short config.hide_one_liner (must say the hide in one sentence)")
    card = tdir / "CARD.md"
    if not card.exists():
        fails.append("missing CARD.md")
    elif hide and hide not in card.read_text():
        fails.append("CARD.md must contain hide_one_liner so you can teach it without chat logs")

    hid = hide_name(tdir)
    if fam and fam != hid:
        fails.append(
            f"config.family {fam!r} must match hide folder {hid!r}"
        )
    if fam:
        for oname, ofam, ohide in other_hide_families(tdir):
            if ofam == fam:
                fails.append(
                    f"clone family {fam!r} already used by {oname} in hide {ohide} "
                    "(not another op-0 / same hide class)"
                )

    if cheat in WEAK_CHEATS:
        fails.append(
            f"cheat_kind={cheat!r} is too weak; need a clever cheat "
            "(not only drop the operator). Yash should invent it."
        )

    if not (isinstance(br, list) and len(br) == 2):
        fails.append("missing instance_busy_range [lo, hi] for generator (target 0.05–0.40)")
    else:
        lo, hi = br
        if lo < 0.04 or hi > 0.45 or lo >= hi:
            fails.append("instance_busy_range must sit in ~5–40% busy, not a fixed 1/16 forever")

    if BANNED.search(waste_txt):
        fails.append("waste RTL has hint words (idle/waste/gate/clken/...)")
    if re.search(r"//|/\*", waste_txt):
        fails.append("waste RTL has comments — labels for the model")

    return fails


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: check_template.py <template_dir>")
    tdir = Path(sys.argv[1]).resolve()
    cfg = load_cfg(tdir)
    top = cfg["top"]
    files = cfg["files"]
    waste, gold, cheat = (
        tdir / files["waste"],
        tdir / files["gold"],
        tdir / files["cheat"],
    )
    bn = cfg["vcd"].get("busy_nonzero", True)

    print(f"=== template {cfg.get('name', tdir.name)} ===\n")

    st_w = stats(parse_vcd(sim(tdir, cfg, waste, "waste"), cfg), bn)
    st_g = stats(parse_vcd(sim(tdir, cfg, gold, "gated"), cfg), bn)

    print("=== sim wasteful RTL ===")
    print(f"  stimulus: {st_w['cycles']} cycles, busy {st_w['busy']}, idle {st_w['idle']}")
    print(f"  data toggles: {st_w['data_toggles']}")
    print(f"  this RTL clocks the flop: EVERY cycle ({st_w['cycles']})")
    print("=== sim gated RTL ===")
    print(f"  stimulus: {st_g['cycles']} cycles, busy {st_g['busy']}, idle {st_g['idle']}")
    print(f"  data toggles: {st_g['data_toggles']}")
    print(f"  this RTL clocks the flop: only when busy ({st_g['busy']})")

    planted = 1.0 - (st_w["busy"] / st_w["cycles"]) if st_w["cycles"] else 0
    print(f"\nplanted clock-duty savings: {planted:.1%}")
    print(f"  wasteful clocks: {st_w['cycles']} (100%)")
    print(f"  gated clocks:    {st_w['busy']} ({st_w['busy']/st_w['cycles']:.1%})")
    print(f"  data toggles waste={st_w['data_toggles']} gated={st_g['data_toggles']}")

    print("\n=== equiv: waste vs gold (must PASS) ===")
    ok_fix = yosys_equiv(tdir, waste, gold, top)
    print("PASS" if ok_fix else "FAIL")
    print("=== equiv: waste vs cheat (must FAIL) ===")
    ok_broken = yosys_equiv(tdir, waste, cheat, top)
    print("FAIL (good)" if not ok_broken else "PASS (BAD — grader missed a cheat)")
    print("=== equiv: waste vs waste (must PASS) ===")
    ok_noop = yosys_equiv(tdir, waste, waste, top)
    print("PASS" if ok_noop else "FAIL")

    waste_txt = waste.read_text()
    honest_shape = all(s not in waste_txt for s in cfg.get("waste_forbidden_substrings", []))
    data_match = st_w["data_toggles"] == st_g["data_toggles"]
    big_gap = planted >= cfg.get("min_savings", 0.5)

    print("\n===== synth honesty =====")
    waste_ce = gated_ce = False
    for title, rtl, extra in [
        ("WASTE proc+opt", files["waste"], ""),
        ("WASTE + opt_dff -sat", files["waste"], "opt_dff -sat"),
        ("GOLD proc+opt", files["gold"], ""),
        ("GOLD + opt_dff -sat", files["gold"], "opt_dff -sat"),
    ]:
        text = yosys_synth(tdir, rtl, top, extra)
        ce = has_ce(text)
        print(f"\n----- {title} -----")
        print(extract_stat(text, top) or "(no stat)")
        print("clock-enable inferred:", ce)
        if title.startswith("WASTE") and ce:
            waste_ce = True
        if title.startswith("GOLD") and ce:
            gated_ce = True

    print("\n=== template card (technical) ===")
    print(f"shape hides enable:     {honest_shape}")
    print(f"idle real (>= min):     {big_gap} ({planted:.1%})")
    print(f"gold equivalent:        {ok_fix}")
    print(f"data toggles match:     {data_match}")
    print(f"cheat caught:           {not ok_broken}")
    print(f"noop equivalent:        {ok_noop}")
    print(f"waste has no CE:        {not waste_ce}")
    print(f"gold has CE:            {gated_ce}")

    ok = (
        honest_shape
        and big_gap
        and ok_fix
        and data_match
        and (not ok_broken)
        and ok_noop
        and (not waste_ce)
        and gated_ce
    )
    print("\nTEMPLATE", "OK" if ok else "NOT OK")

    pq = paper_quality(tdir, cfg, waste_txt)
    print("\n=== paper quality ===")
    print(f"family:          {cfg.get('family', '(missing)')}")
    print(f"hide_one_liner:  {cfg.get('hide_one_liner', '(missing)')}")
    print(f"cheat_kind:      {cfg.get('cheat_kind', '(missing)')}")
    if pq:
        for f in pq:
            print(f"  FAIL: {f}")
        print("PAPER QUALITY NOT OK")
    else:
        print("PAPER QUALITY OK")

    return 0 if ok and not pq else 1


if __name__ == "__main__":
    sys.exit(main())
