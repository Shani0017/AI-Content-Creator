import sys, time
from forge import paths, renderer, families
sp = families.all_specs(115)
want = sys.argv[1].split(",")
for nm in want:
    s = next(x for x in sp if x["scene"] == nm)
    t = time.time()
    renderer.render(s, paths.OUTPUT / f"_t_{nm}.mp4")
    print(nm, round(time.time() - t), "s", flush=True)
