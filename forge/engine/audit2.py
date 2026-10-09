import sys, math, importlib
def audit(cls):
    s = cls(); issues = []
    miss = nan = oob = 0; prev = 0.0; drop = 0.0; vmax = 0.0; vmin_hits = 0
    steps = 0
    while True:
        end = s.step(1 / 60); steps += 1
        for attr in ("balls", "grains", "sw"):
            v = getattr(s, attr, None)
            if isinstance(v, list):
                for b in v:
                    if not isinstance(b, (list, tuple)) or len(b) < 4: continue
                    x, y = b[0], b[1]
                    if x != x or y != y or abs(x) > 1e5: nan += 1
                    elif not (-80 < x < 1160 and -80 < y < 2000): oob += 1
        if hasattr(s, "audit_missed") and s.done_at is None:
            miss += s.audit_missed()
        if hasattr(s, "balls") and getattr(s, "MOTION", None) in ("bounce", "home", "cannon"):
            for b in s.balls:
                sp = math.hypot(b[2], b[3]); vmax = max(vmax, sp)
                if abs(sp - s.SPEED) > 0.12 * s.SPEED and s.done_at is None: vmin_hits += 1
        drop = max(drop, prev - s.p); prev = s.p
        if end or s.t > 120: break
    n = cls.__name__
    if s.done_at is None: issues.append("NEVER COMPLETES")
    elif not (50 <= s.t <= 87): issues.append(f"length {s.t:.0f}s")
    left = 0
    if hasattr(s, "el"): left = sum(1 for e in s.el if e[4])
    if hasattr(s, "leftovers"): left = s.leftovers()
    if s.done_at is not None and left: issues.append(f"{left} LEFTOVERS at complete")
    if miss > 20: issues.append(f"{miss} missed-collision frames")
    if nan: issues.append(f"NaN/huge {nan}")
    if oob: issues.append(f"out-of-bounds {oob}")
    if drop > 0.02: issues.append(f"progress dropped {drop:.2f}")
    if vmin_hits > 30: issues.append(f"speed deviates from constant {vmin_hits}")
    return n, round(s.t, 1), issues, miss
if __name__ == "__main__":
    mod = importlib.import_module(sys.argv[1])
    for name in sys.argv[2:]:
        print(*audit(getattr(mod, name)), flush=True)
