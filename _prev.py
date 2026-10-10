import sys
from PIL import Image
from forge import families, scenes, renderer
th = renderer.THEMES["midnight"]
specs = {}
for sp in families.all_specs(115):
    specs.setdefault(sp["scene"], sp)
names = sys.argv[1].split(",") if len(sys.argv) > 1 else list(specs)
Ts = [float(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else "0.9,1.9,2.9,3.9,4.9".split(","))]
out = sys.argv[3] if len(sys.argv) > 3 else "_prev.png"
S = 0.36
W, H = 1080, 700
sheet = Image.new("RGB", (int(W * S) * len(Ts), int(H * S) * len(names)), (10, 14, 34))
for r, nm in enumerate(names):
    sp = specs[nm]
    for k, T in enumerate(Ts):
        im = Image.new("RGB", (W, 1100), (22, 20, 52))
        scenes.draw(im, nm, T, th, sp["params"])
        im = im.crop((0, 330, W, 330 + H)).resize((int(W * S), int(H * S)), Image.LANCZOS)
        sheet.paste(im, (k * int(W * S), r * int(H * S)))
sheet.save(out)
print("saved", out, sheet.size)
