"""Word-problem families -> reel specs. Every number in a narration line is computed here, never typed by hand.
Each family function f(v) (v = 0..4) returns:
  dict(title=..., subtitle=..., tags=(..), headline=<file title>, beats=[dict(say=..., steps=[html..], stamp=(text,color)|None, answer=text|None), ...])
The last beat is always the call-to-action (added by add_cta)."""
import math
from fractions import Fraction

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def w(n):
    n = int(n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    if n < 1000:
        return ONES[n // 100] + " hundred" + (" " + w(n % 100) if n % 100 else "")
    if n < 1000000:
        return w(n // 1000) + " thousand" + (" " + w(n % 1000) if n % 1000 else "")
    return w(n // 1000000) + " million" + (" " + w(n % 1000000) if n % 1000000 else "")


def sp(x):
    """spoken number: words if whole, else plain decimal"""
    x = float(x)
    return w(int(x)) if x == int(x) else f"{x:g}"


def money(c):
    """cents -> spoken amount"""
    d, r = divmod(int(c), 100)
    if d == 0:
        return f"{w(r)} cents"
    s = f"{w(d)} dollar{'s' if d != 1 else ''}"
    return s + (f" {w(r)}" if r else "")


def usd(c):
    d, r = divmod(int(c), 100)
    return f"${d}.{r:02d}" if r else f"${d}"


def Y(t):
    return f'<span class="y">{t}</span>'


def G(t):
    return f'<span class="g">{t}</span>'


def P(t):
    return f'<span class="p">{t}</span>'


def C(t):
    return f'<span class="c">{t}</span>'


def R_(t):
    return f'<span class="r">{t}</span>'


def B(say, steps=(), stamp=None, answer=None):
    return dict(say=say, steps=list(steps), stamp=stamp, answer=answer)

ICON = {"bat": "bat", "ball": "ball", "pen": "pen", "eraser": "eraser", "burger": "burger", "fries": "fries", "phone": "phone", "case": "case",
        "sandwich": "sandwich", "drink": "drink", "widgets": "gear", "pizzas": "pizza", "cookies": "cookie", "phones": "phone", "shirts": "shirt"}
CRITTER = {"frog": (125, 255, 138), "snail": (255, 190, 120), "ant": (200, 90, 90), "monkey": (200, 150, 90), "beetle": (120, 150, 255)}
FARM = {"sheep": (240, 240, 250), "cows": (230, 200, 160), "chickens": (255, 240, 200), "goats": (210, 210, 220), "horses": (190, 140, 100)}


def _fin(sp, scene, loc, keys):
    P = {}
    for k in keys:
        v = loc[k]
        P[{"Bv": "B"}.get(k, k)] = float(v) if isinstance(v, Fraction) else v
    if scene == "batball":
        P["icon_big"], P["icon_small"] = ICON.get(P["big"], "tag"), ICON.get(P["small"], "tag")
    if scene == "widgets":
        P["item_icon"] = ICON.get(P["thing"], "gear")
    if scene == "frog":
        P["col"] = CRITTER.get(P["animal"], (125, 255, 138))
    if scene == "allbut":
        P["col"] = FARM.get(P["animal"], (240, 240, 250))
    sp["scene"], sp["params"] = scene, P
    return sp


WRONG = ("WRONG", "#ff5c8a")


# ------------------------------------------------------------------ 1 bat & ball
def f_batball(v):
    items = [("bat", "ball"), ("pen", "eraser"), ("burger", "fries"), ("phone", "case"), ("sandwich", "drink")][v]
    s = [5, 10, 15, 20, 25][v]
    D = [100, 200, 300, 500, 1000][v]
    T = D + 2 * s
    big, small = items
    _sp = dict(
        title=f"The {big.title()} & {small.title()} Trap", subtitle=f"{usd(T)} total · the {big} costs {usd(D)} more", tags=("WORD PROBLEM", "ALGEBRA"),
        headline=f"The {big.title()} And {small.title()} Riddle Most People Get Wrong",
        beats=[
            B(f"A {big} and a {small} cost {money(T)} together. The {big} costs {money(D)} more than the {small}. How much is the {small}?",
              [f"{big} + {small} = {Y(usd(T))}", f"{big} = {small} + {Y(usd(D))}"]),
            B(f"Your brain says {money(T - D)}. But that's wrong.", [f"your brain: {small} = {P(usd(T - D))}"], stamp=WRONG),
            B(f"If the {small} cost {money(T - D)}, the {big} would cost {money(T - D + D)}. Together that's {money(T - D + T - D + D)}, not {money(T)}.",
              [f"{usd(T - D)} + {usd(T - D + D)} = {R_(usd(2 * (T - D) + D))}  ≠ {usd(T)}"]),
            B(f"Let the {small} be x. Then the {big} is x plus {money(D)}. So two x plus {money(D)} equals {money(T)}.",
              [f"x + (x + {usd(D)}) = {usd(T)}", f"2x = {usd(T - D)}"]),
            B(f"Two x is {money(T - D)}, so x is {money(s)}. The {small} costs {money(s)}.", [f"x = {G(usd(s))}"], answer=usd(s)),
            B(f"Check it. The {big} is {money(s + D)}. {money(s)} plus {money(s + D)} is {money(T)}.", [f"{usd(s)} + {usd(s + D)} = {G(usd(T))} ✓"]),
        ])
    return _fin(_sp, 'batball', locals(), ['s', 'D', 'T', 'big', 'small'])


# ------------------------------------------------------------------ 2 doubling
def f_lily(v):
    thing, place, N = [("lily pads", "the lake", 48), ("algae", "the pond", 30), ("mold", "the loaf of bread", 20), ("weeds", "the garden", 36),
                       ("moss", "the stone wall", 60)][v]
    _sp = dict(
        title="The Doubling Trap", subtitle=f"doubles daily · full on day {N} · when was it half?", tags=("WORD PROBLEM", "EXPONENTIAL"),
        headline=f"The {thing.title()} Riddle That Tricks Everyone",
        beats=[
            B(f"The {thing} on {place} double in size every day. It takes {w(N)} days to cover all of it. On which day was it half covered?",
              [f"×2 every day", f"full on day {Y(N)}"]),
            B(f"Most people say day {w(N // 2)}. Half of {w(N)}.", [f"{N} ÷ 2 = {R_(N // 2)} ?"], stamp=WRONG),
            B(f"But it doubles every day. So the day before it was full, it was half as big.", [f"day {N} = full", f"day {N - 1} = {Y('half')}"]),
            B(f"Half covered on day {w(N - 1)}. And one day before that, just a quarter.", [f"day {N - 1} → 1/2", f"day {N - 2} → 1/4"], answer=f"DAY {N - 1}"),
            B(f"It goes from half to totally full in a single day. That's exponential growth.", [f"half → full = {Y('1 day')}"]),
        ])
    return _fin(_sp, 'lily', locals(), ['N', 'thing', 'place'])


# ------------------------------------------------------------------ 3 widgets
def f_widgets(v):
    n = [5, 3, 6, 8, 4][v]
    thing, mach = [("widgets", "machines"), ("pizzas", "ovens"), ("cookies", "mixers"), ("phones", "robots"), ("shirts", "presses")][v]
    _sp = dict(
        title="The Machine Puzzle", subtitle=f"{n} machines · {n} minutes · {n} {thing}", tags=("WORD PROBLEM", "RATES"),
        headline=f"{n} Machines Make {n} {thing.title()} - How Long For 100",
        beats=[
            B(f"It takes {w(n)} {mach} {w(n)} minutes to make {w(n)} {thing}. How long would it take {w(100)} {mach} to make {w(100)} {thing}?",
              [f"{n} {mach} → {n} min → {n} {thing}"]),
            B(f"Most people say {w(100)} minutes. That's wrong.", [f"your brain: {R_('100 min')}"], stamp=WRONG),
            B(f"Look at one machine. One machine makes one {thing[:-1]} in {w(n)} minutes.", [f"1 machine → 1 item → {Y(str(n) + ' min')}"]),
            B(f"So {w(100)} machines make {w(100)} {thing} in the same {w(n)} minutes.", [f"100 machines → 100 items → {G(str(n) + ' min')}"], answer=f"{n} MIN"),
            B(f"Adding machines doesn't change how long one {thing[:-1]} takes. The answer is {w(n)} minutes.", []),
        ])
    return _fin(_sp, 'widgets', locals(), ['n', 'thing', 'mach'])


# ------------------------------------------------------------------ 4 average speed
def f_avgspeed(v):
    a, b = [(30, 60), (40, 60), (20, 30), (60, 90), (50, 75)][v]
    avg = Fraction(2 * a * b, a + b)
    sa = f"{float(avg):g}"
    simple = (a + b) / 2
    _sp = dict(
        title="The Round Trip Trap", subtitle=f"there at {a} · back at {b} · average speed?", tags=("WORD PROBLEM", "SPEED"),
        headline=f"The Round Trip Riddle - {a} And {b} Miles Per Hour",
        beats=[
            B(f"You drive to a town at {w(a)} miles per hour. Then you drive back the same road at {w(b)} miles per hour. What's your average speed?",
              [f"there: {Y(a)} mph", f"back: {Y(b)} mph"]),
            B(f"Most people say {sp(simple)} miles per hour. The average of {w(a)} and {w(b)}.",
              [f"({a} + {b}) ÷ 2 = {R_(f'{simple:g}')} ?"], stamp=WRONG),
            B(f"But you spend more time at the slower speed. So the average has to be lower. Let the road be {w(a * b)} miles one way.", [f"one way = {Y(a * b)} mi"]),
            B(f"There takes {w(b)} hours. Back takes {w(a)} hours. That's {w(a + b)} hours for {w(2 * a * b)} miles.",
              [f"there = {b} h, back = {a} h", f"{2 * a * b} mi ÷ {a + b} h"]),
            B(f"{w(2 * a * b)} miles in {w(a + b)} hours is {sp(avg)} miles per hour.", [f"average = {G(sa + ' mph')}"], answer=f"{sa} MPH"),
        ])
    return _fin(_sp, 'avgspeed', locals(), ['a', 'b', 'avg'])


# ------------------------------------------------------------------ 5 handshakes
def f_handshake(v):
    n = [5, 8, 10, 12, 20][v]
    ctx = ["friends at a dinner", "players before a match", "guests at a party", "people at a meeting", "students on the first day"][v]
    tot = n * (n - 1) // 2
    _sp = dict(
        title="The Handshake Problem", subtitle=f"{n} people · everyone shakes everyone's hand once", tags=("WORD PROBLEM", "COUNTING"),
        headline=f"{n} People Shake Hands Once - How Many Handshakes",
        beats=[
            B(f"{w(n).capitalize()} {ctx}. Everyone shakes hands with everyone else exactly once. How many handshakes happen?", [f"{Y(n)} people", "each pair shakes once"]),
            B(f"Each person shakes {w(n - 1)} hands. {w(n).capitalize()} people times {w(n - 1)} is {w(n * (n - 1))}.", [f"{n} × {n - 1} = {P(n * (n - 1))}"]),
            B(f"But that counts every handshake twice, once from each side.", [f"each handshake counted {R_('twice')}"], stamp=("TWICE", "#ffd84d")),
            B(f"So divide by two. {w(n * (n - 1))} divided by two is {w(tot)}.", [f"{n * (n - 1)} ÷ 2 = {G(tot)}"], answer=f"{tot}"),
            B(f"{w(tot).capitalize()} handshakes. A shortcut: n times n minus one, over two.", []),
        ])
    return _fin(_sp, 'handshake', locals(), ['n', 'tot'])


# ------------------------------------------------------------------ 6 percent up & down
def f_percent(v):
    p = [10, 20, 30, 40, 50][v]
    item, price = [("jacket", 100), ("phone", 500), ("bike", 200), ("laptop", 1000), ("watch", 400)][v]
    up = price * (100 + p) // 100
    down = up * (100 - p) // 100
    _sp = dict(
        title="The Percent Trap", subtitle=f"+{p}% then -{p}% · back to the start?", tags=("WORD PROBLEM", "PERCENT"),
        headline=f"A {item.title()} Goes Up {p}% Then Down {p}% - What's The Price",
        beats=[
            B(f"A {item} costs {w(price)} dollars. The shop raises the price by {w(p)} percent. Then it cuts the new price by {w(p)} percent. What does it cost now?",
              [f"start = {Y('$' + str(price))}", f"+{p}% then −{p}%"]),
            B(f"Most people say it's back to {w(price)} dollars. But that's wrong.", [f"your brain: {R_('$' + str(price))}"], stamp=WRONG),
            B(f"Up {w(p)} percent makes it {w(up)} dollars.", [f"{price} × {100 + p}% = {Y('$' + str(up))}"]),
            B(f"Now take {w(p)} percent off {w(up)}. That's a bigger amount than before. The price drops to {w(down)} dollars.",
              [f"{up} × {100 - p}% = {G('$' + str(down))}"], answer=f"${down}"),
            B(f"You end up {w(price - down)} dollars below the start. The percentages apply to different amounts.", []),
        ])
    return _fin(_sp, 'percent', locals(), ['p', 'item', 'price', 'up', 'down'])


# ------------------------------------------------------------------ 7 fence posts
def f_fence(v):
    L, s = [(100, 10), (60, 5), (200, 20), (90, 15), (150, 25)][v]
    gaps = L // s
    _sp = dict(
        title="The Fence Post Trap", subtitle=f"{L} m fence · a post every {s} m", tags=("WORD PROBLEM", "COUNTING"),
        headline=f"A {L} Metre Fence With A Post Every {s} Metres - How Many Posts",
        beats=[
            B(f"A straight fence is {w(L)} metres long. You put a post every {w(s)} metres, including both ends. How many posts do you need?", [f"{Y(L)} m fence", f"post every {Y(s)} m"]),
            B(f"Most people divide. {w(L)} divided by {w(s)} is {w(gaps)}.", [f"{L} ÷ {s} = {R_(gaps)} ?"], stamp=WRONG),
            B(f"But that counts the gaps between posts, not the posts. Picture a short fence with just two posts. That's one gap.", [f"posts = gaps + {Y(1)}"]),
            B(f"So {w(gaps)} gaps need {w(gaps + 1)} posts.", [f"{gaps} + 1 = {G(gaps + 1)}"], answer=f"{gaps + 1} POSTS"),
            B(f"You always need one more post than gaps.", []),
        ])
    return _fin(_sp, 'fence', locals(), ['L', 's', 'gaps'])


# ------------------------------------------------------------------ 8 frog in well
def f_frog(v):
    d, a, b = [(10, 3, 2), (20, 5, 4), (12, 4, 2), (30, 7, 4), (15, 5, 3)][v]
    days = math.ceil((d - a) / (a - b)) + 1
    animal, place = [("frog", "a well"), ("snail", "a garden pipe"), ("ant", "a bucket"), ("monkey", "a pit"), ("beetle", "a deep hole")][v]
    _sp = dict(
        title="The Climbing Puzzle", subtitle=f"{d} m deep · up {a} · back {b}", tags=("WORD PROBLEM", "LOGIC"),
        headline=f"A {animal.title()} Climbs {a} Metres A Day And Slips {b} - How Many Days",
        beats=[
            B(f"A {animal} is at the bottom of {place}, {w(d)} metres deep. Each day it climbs {w(a)} metres. Each night it slips back {w(b)}. How many days to get out?",
              [f"depth {Y(d)} m", f"up {Y(a)} m / back {Y(b)} m"]),
            B(f"Most people say each day gains {w(a - b)} metre{'s' if a - b != 1 else ''}. So {w(math.ceil(d / (a - b)))} days.", [f"{d} ÷ {a - b} = {R_(math.ceil(d / (a - b)))} ?"], stamp=WRONG),
            B(f"But on the last day it climbs out and never slips back. So the last climb is free.", [f"last day: no slip"]),
            B(f"After {w(days - 1)} days it has gained {w((days - 1) * (a - b))} metres. The next day it climbs {w(a)} more and reaches the top.",
              [f"{days - 1} days × {a - b} = {Y((days - 1) * (a - b))} m", f"+ {a} = {G((days - 1) * (a - b) + a)} m ≥ {d}"]),
            B(f"So it takes {w(days)} days.", [f"answer = {G(days)} days"], answer=f"{days} DAYS"),
        ])
    return _fin(_sp, 'frog', locals(), ['d', 'a', 'b', 'days', 'animal'])


# ------------------------------------------------------------------ 9 work rate
def f_work(v):
    a, b = [(6, 3), (4, 12), (10, 15), (12, 6), (20, 30)][v]
    tg = Fraction(a * b, a + b)
    tgs = f"{float(tg):g}"
    job = ["paint a room", "mow a field", "fill a pool", "stack the shelves", "write a report"][v]
    _sp = dict(
        title="The Teamwork Puzzle", subtitle=f"{a} hours alone · {b} hours alone · together?", tags=("WORD PROBLEM", "RATES"),
        headline=f"Alone It Takes {a} Hours, Alone It Takes {b} - How Long Together",
        beats=[
            B(f"Sam can {job} in {w(a)} hours. Alex can do the same job in {w(b)} hours. How long does it take them working together?", [f"Sam: {Y(a)} h", f"Alex: {Y(b)} h"]),
            B(f"Don't just average the times. Work in rates, jobs per hour.", [f"rate = 1 ÷ time"]),
            B(f"Sam does one over {w(a)} of the job each hour. Alex does one over {w(b)}.", [f"Sam = 1/{a} per hour", f"Alex = 1/{b} per hour"]),
            B(f"Together they do {w(b)} plus {w(a)} over {w(a * b)} of the job each hour. That's {w(a + b)} over {w(a * b)}.", [f"1/{a} + 1/{b} = {Y(f'{a + b}/{a * b}')}"]),
            B(f"Flip it. The whole job takes {w(a * b)} over {w(a + b)} hours, which is {sp(tg)} hours.", [f"time = {G(tgs + ' h')}"], answer=f"{tgs} HOURS"),
        ])
    return _fin(_sp, 'work', locals(), ['a', 'b', 'tg'])


# ------------------------------------------------------------------ 10 watermelon
def f_water(v):
    m, p1, p2 = [(100, 99, 98), (200, 98, 96), (100, 99, 96), (100, 95, 90), (100, 90, 80)][v]
    solid = Fraction(m * (100 - p1), 100)
    new = solid / Fraction(100 - p2, 100)
    ns = f"{float(new):g}"
    item = ["watermelon", "bag of grapes", "pile of fruit", "stack of mushrooms", "box of cucumbers"][v]
    _sp = dict(
        title="The Dehydration Trap", subtitle=f"{m} kg · {p1}% water → {p2}% water", tags=("WORD PROBLEM", "PERCENT"),
        headline=f"A {m} Kilo {item.title()} Is {p1} Percent Water - Dries To {p2} Percent",
        beats=[
            B(f"A {item} weighs {w(m)} kilos and is {w(p1)} percent water. It sits in the sun and dries until it is {w(p2)} percent water. How much does it weigh now?",
              [f"{Y(m)} kg · {p1}% water", f"later: {p2}% water"]),
            B(f"Most people say it barely changes. A little under {w(m)} kilos.", [f"your brain: ~{R_(m - 1)} kg"], stamp=WRONG),
            B(f"Look at the solid part, the stuff that isn't water. It starts as {w(100 - p1)} percent of {w(m)}, which is {sp(solid)} kilos.", [f"solid = {m} × {100 - p1}% = {Y(f'{float(solid):g}')} kg"]),
            B(f"That solid part never changes. Later it has to be {w(100 - p2)} percent of the new weight.", [f"{f'{float(solid):g}'} = {100 - p2}% × new"]),
            B(f"So the new weight is {sp(solid)} divided by {w(100 - p2)} percent. That's {sp(new)} kilos.", [f"new = {G(ns + ' kg')}"], answer=f"{ns} KG"),
        ])
    return _fin(_sp, 'water', locals(), ['m', 'p1', 'p2', 'solid', 'new'])


# ------------------------------------------------------------------ 11 clock angle
def f_clock(v):
    h, m = [(3, 30), (2, 20), (4, 10), (7, 30), (12, 20)][v]
    ang = abs(30 * (h % 12) - 5.5 * m)
    ang = min(ang, 360 - ang)
    angs = f"{ang:g}"
    _sp = dict(
        title="The Clock Angle Puzzle", subtitle=f"{h}:{m:02d} · angle between the hands?", tags=("PUZZLE", "GEOMETRY"),
        headline=f"What's The Angle Between The Clock Hands At {h}:{m:02d}",
        beats=[
            B(f"It's {w(h)} {w(m) if m else 'o clock'}. What's the angle between the hour hand and the minute hand?", [f"time = {Y(f'{h}:{m:02d}')}"]),
            B(f"The minute hand moves {w(6)} degrees every minute. At {w(m)} minutes it's at {w(6 * m)} degrees.", [f"minute hand = 6° × {m} = {C(6 * m)}°"]),
            B(f"The hour hand moves {w(30)} degrees per hour, and half a degree every minute. At {w(h)} {w(m)} it's at {sp(30 * h + 0.5 * m)} degrees.",
              [f"hour hand = 30° × {h} + 0.5° × {m} = {P(f'{30 * h + 0.5 * m:g}')}°"]),
            B(f"The gap between them is {sp(ang)} degrees.", [f"|{6 * m} − {30 * h + 0.5 * m:g}| = {G(angs + '°')}"], answer=f"{angs}°"),
            B(f"Most people forget the hour hand creeps forward as the minutes pass.", []),
        ])
    return _fin(_sp, 'clock', locals(), ['h', 'm', 'ang'])


# ------------------------------------------------------------------ 12 all but n
def f_allbut(v):
    tot, n = [(17, 9), (25, 8), (30, 12), (50, 7), (100, 15)][v]
    animal = ["sheep", "cows", "chickens", "goats", "horses"][v]
    _sp = dict(
        title="The Trick Question", subtitle=f"{tot} {animal} · all but {n} run away", tags=("RIDDLE", "WORD PROBLEM"),
        headline=f"A Farmer Has {tot} {animal.title()} - All But {n} Run Away - How Many Are Left",
        beats=[
            B(f"A farmer has {w(tot)} {animal}. All but {w(n)} run away. How many {animal} does the farmer have left?", [f"{Y(tot)} {animal}", f"all but {Y(n)} run away"]),
            B(f"Most people subtract. {w(tot)} minus {w(n)} is {w(tot - n)}.", [f"{tot} − {n} = {R_(tot - n)} ?"], stamp=WRONG),
            B(f"But read it again. All but {w(n)} run away. That means {w(n)} stay.", [f"all but {n} → {Y(n)} stay"]),
            B(f"The farmer has {w(n)} {animal} left.", [f"left = {G(n)}"], answer=f"{n}"),
            B(f"The trick is in the wording. Read slowly.", []),
        ])
    return _fin(_sp, 'allbut', locals(), ['tot', 'n', 'animal'])


# ------------------------------------------------------------------ 13 socks
def f_socks(v):
    c = [2, 3, 4, 5, 6][v]
    cols = ["black and white", "red, green and blue", "red, green, blue and yellow", "five different colours", "six different colours"][v]
    _sp = dict(
        title="The Sock Drawer Puzzle", subtitle=f"{c} colours · in the dark", tags=("PUZZLE", "LOGIC"),
        headline=f"{c} Colours Of Socks In The Dark - How Many To Grab For A Pair",
        beats=[
            B(f"A drawer is full of socks in {cols}. The lights are off. How many socks must you grab to be sure you have a matching pair?", [f"{Y(c)} colours", "grab in the dark"]),
            B(f"Most people say {w(c * 2)}. Or they guess a big number.", [f"your brain: {R_(c * 2)} ?"], stamp=WRONG),
            B(f"Think about the worst luck. You grab one sock of each colour. That's {w(c)} socks and no pair yet.", [f"worst case: {Y(c)} socks, all different"]),
            B(f"Now the next sock has to match one of them. So {w(c + 1)} socks guarantees a pair.", [f"{c} + 1 = {G(c + 1)}"], answer=f"{c + 1} SOCKS"),
            B(f"Always one more than the number of colours. That's the pigeonhole principle.", []),
        ])
    return _fin(_sp, 'socks', locals(), ['c'])


# ------------------------------------------------------------------ 14 chessboard
def f_wheat(v):
    n = [8, 10, 12, 16, 20][v]
    tot = 2 ** n - 1
    _sp = dict(
        title="The Doubling Reward", subtitle=f"1 grain, then double every square · {n} squares", tags=("WORD PROBLEM", "EXPONENTIAL"),
        headline=f"One Grain Doubled On {n} Squares - How Many Grains In Total",
        beats=[
            B(f"A king puts one grain of rice on the first square of a board. On each next square he doubles it. How many grains are there in total after {w(n)} squares?",
              ["square 1 = 1 grain", "each square ×2"]),
            B(f"Most people guess a few hundred. That's wrong.", [], stamp=WRONG),
            B(f"Square {w(n)} alone holds {w(2 ** (n - 1))} grains. Doubling is explosive.", [f"square {n} = 2^{n - 1} = {Y(2 ** (n - 1))}"]),
            B(f"Add every square and you get {w(tot)} grains.", [f"total = 2^{n} − 1 = {G(tot)}"], answer=f"{tot}"),
            B(f"Each square holds one more than all the squares before it put together.", []),
        ])
    return _fin(_sp, 'wheat', locals(), ['n', 'tot'])


# ------------------------------------------------------------------ 15 discount order
def f_discount(v):
    d, c = [(20, 10), (25, 20), (30, 10), (40, 20), (50, 10)][v]
    price = [100, 200, 100, 200, 100][v]
    A = price * (100 - d) // 100 - c
    Bv = (price - c) * (100 - d) // 100
    _sp = dict(
        title="The Coupon Order Puzzle", subtitle=f"{d}% off and a ${c} coupon · which order?", tags=("WORD PROBLEM", "PERCENT"),
        headline=f"{d} Percent Off And A ${c} Coupon - Does The Order Matter",
        beats=[
            B(f"A jacket costs {w(price)} dollars. You have {w(d)} percent off and a {w(c)} dollar coupon. Does it matter which one the cashier applies first?",
              [f"price {Y('$' + str(price))}", f"{d}% off + ${c} coupon"]),
            B(f"Most people say no, it's the same. Let's check.", [], stamp=("CHECK", "#ffd84d")),
            B(f"Percent first. {w(price)} minus {w(d)} percent is {w(price * (100 - d) // 100)}. Then {w(c)} off is {w(A)} dollars.", [f"{price} × {100 - d}% − {c} = {Y('$' + str(A))}"]),
            B(f"Coupon first. {w(price)} minus {w(c)} is {w(price - c)}. Then {w(d)} percent off is {w(Bv)} dollars.", [f"({price} − {c}) × {100 - d}% = {G('$' + str(Bv))}"]),
            B(f"Percent off first is cheaper, by {w(Bv - A)} dollars. Take the discount first, then the coupon.", [f"saving = {G('$' + str(Bv - A))}"], answer=f"${Bv - A} CHEAPER"),
        ])
    return _fin(_sp, 'discount', locals(), ['d', 'c', 'price', 'A', 'Bv'])


# ------------------------------------------------------------------ 16 race position
def f_race(v):
    pos = [2, 3, 4, 5, 10][v]
    ords = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 9: "ninth", 10: "tenth", 11: "eleventh"}
    _sp = dict(
        title="The Race Riddle", subtitle=f"you pass the runner in {ords[pos]} place", tags=("RIDDLE", "LOGIC"),
        headline=f"You Overtake The Runner In {ords[pos].title()} Place - What Place Are You In",
        beats=[
            B(f"You're running a race. You overtake the runner in {ords[pos]} place. What place are you in now?", [f"you pass {Y(ords[pos])} place"]),
            B(f"Most people say {ords[pos - 1] if pos > 1 else 'first'} place. That's wrong.", [f"your brain: {R_(ords[pos - 1])}"], stamp=WRONG),
            B(f"Picture it. The person you passed was {ords[pos]}. You take their spot.", [f"you take {Y(ords[pos])} spot"]),
            B(f"You're now in {ords[pos]} place. And the person you passed drops to {ords[pos + 1] if pos + 1 in ords else 'next'} place.".replace("next place", "the next place"),
              [f"you = {G(ords[pos])}"], answer=f"{ords[pos].upper()} PLACE"),
            B(f"To be {ords[pos - 1]}, you'd have to pass the person ahead of them.", []),
        ])
    return _fin(_sp, 'race', locals(), ['pos'])


# ------------------------------------------------------------------ 17 ages
def f_age(v):
    k, tot = [(4, 50), (3, 48), (5, 60), (4, 45), (6, 49)][v]
    s = tot // (k + 1)
    f_ = s * k
    _sp = dict(
        title="The Age Puzzle", subtitle=f"father is {k}× son · together {tot}", tags=("WORD PROBLEM", "ALGEBRA"),
        headline=f"A Father Is {k} Times His Son's Age - Together They Are {tot}",
        beats=[
            B(f"A father is {w(k)} times as old as his son. Together their ages add up to {w(tot)}. How old is the son?", [f"father = {Y(str(k) + ' × son')}", f"sum = {Y(tot)}"]),
            B(f"Let the son's age be x. Then the father is {w(k)} x.", [f"son = x", f"father = {k}x"]),
            B(f"Together that's x plus {w(k)} x, which is {w(k + 1)} x.", [f"x + {k}x = {P(str(k + 1) + 'x')}"]),
            B(f"{w(k + 1).capitalize()} x equals {w(tot)}. So x is {w(s)}.", [f"{k + 1}x = {tot}", f"x = {G(s)}"], answer=f"SON = {s}"),
            B(f"The son is {w(s)} and the father is {w(f_)}. {w(s)} plus {w(f_)} is {w(tot)}.", [f"{s} + {f_} = {G(tot)} ✓"]),
        ])
    return _fin(_sp, 'age', locals(), ['k', 'tot', 's'])


# ------------------------------------------------------------------ 18 missing dollar
def f_missing(v):
    p, Rm = [(10, 25), (20, 55), (15, 40), (30, 85), (12, 31)][v]
    T = 3 * p
    ref = T - Rm
    each = (ref - 2) // 3
    paid = 3 * (p - each)
    _sp = dict(
        title="The Missing Dollar", subtitle=f"3 friends · ${T} room · where did $1 go?", tags=("RIDDLE", "WORD PROBLEM"),
        headline=f"The Missing Dollar Riddle - ${T} Hotel Room Version",
        beats=[
            B(f"Three friends rent a hotel room for {w(T)} dollars. Each pays {w(p)}.", [f"3 × {Y('$' + str(p))} = {Y('$' + str(T))}"]),
            B(f"Later the clerk says the room is only {w(Rm)} dollars. The bellboy takes back {w(ref)} dollars.", [f"room = {Y('$' + str(Rm))}", f"refund = {G('$' + str(ref))}"]),
            B(f"He keeps {w(2)} dollars, and gives each friend {w(each)} dollar{'s' if each != 1 else ''} back.", [f"bellboy keeps {P('$2')}", f"each friend +{G('$' + str(each))}"]),
            B(f"So each friend paid {w(p - each)} dollars. Three times {w(p - each)} is {w(paid)}. Add the bellboy's {w(2)}: {w(paid + 2)}.", [f"3 × {p - each} = {Y(paid)}", f"{paid} + 2 = {R_(paid + 2)} ?"]),
            B(f"Where did the missing {w(T - paid - 2) if T - paid - 2 > 0 else 'one'} dollar go? Nowhere. The question adds the wrong numbers.", [f"{paid} already includes the bellboy's 2"], stamp=("TRICK", "#ffd84d")),
            B(f"The friends paid {w(paid)}. That's {w(Rm)} for the room plus {w(2)} for the bellboy. Add the refund {w(ref - 2)} and you're back at {w(T)}.",
              [f"{Rm} + 2 = {G(paid)}", f"{paid} + {ref - 2} = {G(T)} ✓"], answer="NOTHING MISSING"),
        ])
    return _fin(_sp, 'missing', locals(), ['p', 'Rm', 'ref', 'each'])


# ------------------------------------------------------------------ 19 trains & fly
def f_fly(v):
    D, s1, s2, fl = [(120, 40, 20, 90), (150, 30, 20, 60), (200, 60, 40, 80), (90, 25, 20, 60), (60, 10, 20, 45)][v]
    t = Fraction(D, s1 + s2)
    ts = f"{float(t):g}"
    dist = fl * t
    ds = f"{float(dist):g}"
    _sp = dict(
        title="The Trains & the Fly", subtitle=f"{D} mi apart · trains {s1} & {s2} mph · fly {fl} mph", tags=("WORD PROBLEM", "SPEED & TIME"),
        headline=f"Two Trains And A Fly - {D} Miles Apart",
        beats=[
            B(f"Two trains are {w(D)} miles apart, driving straight toward each other. One goes {w(s1)} miles per hour, the other {w(s2)}.", [f"gap {Y(D)} mi", f"speeds {Y(s1)} + {Y(s2)} mph"]),
            B(f"A fly zooms back and forth between them at {w(fl)} miles per hour, until they collide. How far does the fly travel?", [f"fly = {Y(fl)} mph"]),
            B(f"Don't add up infinite zig-zags. Ask one simple question. How long until the trains meet?", [f"time to meet = ?"], stamp=("THINK", "#ffd84d")),
            B(f"They close the gap at {w(s1 + s2)} miles per hour combined. So they meet in {w(D)} over {w(s1 + s2)}, which is {sp(t)} hours.", [f"closing speed = {Y(s1 + s2)} mph", f"{D} ÷ {s1 + s2} = {G(ts + ' h')}"]),
            B(f"The fly flies the whole time. {w(fl)} miles per hour for {sp(t)} hours is {sp(dist)} miles.", [f"{fl} × {ts} = {G(ds + ' mi')}"], answer=f"{ds} MILES"),
        ])
    return _fin(_sp, 'fly', locals(), ['D', 's1', 's2', 'fl', 't', 'dist'])


# ------------------------------------------------------------------ 20 gauss logs
def f_logs(v):
    n = [10, 12, 15, 20, 100][v]
    tot = n * (n + 1) // 2
    thing = ["logs", "bricks", "oranges", "cans", "coins"][v]
    _sp = dict(
        title="The Stacking Trick", subtitle=f"{n} at the bottom, one fewer each row", tags=("WORD PROBLEM", "PATTERNS"),
        headline=f"A Stack Of {thing.title()} - {n} On The Bottom Row - How Many In Total",
        beats=[
            B(f"A stack of {thing} has {w(n)} on the bottom row, then {w(n - 1)}, then {w(n - 2)}, all the way up to just one on top. How many {thing} are in the stack?",
              [f"rows: {Y(n)}, {n - 1}, {n - 2}, … , 1"]),
            B(f"You could add them one by one. But there's a trick.", [], stamp=("TRICK", "#ffd84d")),
            B(f"Pair the top with the bottom. One plus {w(n)} is {w(n + 1)}. Two plus {w(n - 1)} is also {w(n + 1)}.", [f"1 + {n} = {Y(n + 1)}", f"2 + {n - 1} = {Y(n + 1)}"]),
            B(f"There are {w(n // 2) if n % 2 == 0 else w(n) + ' over two'} such pairs. So the total is {w(n)} times {w(n + 1)}, divided by two.", [f"{n} × {n + 1} ÷ 2"]),
            B(f"That's {w(tot)} {thing}.", [f"total = {G(tot)}"], answer=f"{tot}"),
        ])
    return _fin(_sp, 'logs', locals(), ['n', 'tot', 'thing'])


# ------------------------------------------------------------------ 21 pizza cuts
def f_pizza(v):
    n = [3, 4, 5, 6, 7][v]
    pieces = n * (n + 1) // 2 + 1
    _sp = dict(
        title="The Pizza Cut Puzzle", subtitle=f"{n} straight cuts · most pieces?", tags=("PUZZLE", "PATTERNS"),
        headline=f"{n} Straight Cuts Of A Pizza - What's The Most Pieces",
        beats=[
            B(f"You have a pizza and {w(n)} straight cuts. What's the most pieces you can make?", [f"cuts = {Y(n)}"]),
            B(f"Most people say {w(2 * n)}. Cutting through the middle every time.", [f"your brain: {R_(2 * n)}"], stamp=WRONG),
            B(f"To get the most, every new cut must cross all the old cuts, in different places. Each new cut adds one piece for every line it crosses, plus one.",
              [f"new cut adds (cuts so far + 1) pieces"]),
            B(f"So the pieces go one, two, four, seven, eleven. The pattern adds one more each time.", [f"1, 2, 4, 7, 11, 16, 22, 29 …"]),
            B(f"With {w(n)} cuts, the most you can get is {w(pieces)} pieces.", [f"{n}×{n + 1} ÷ 2 + 1 = {G(pieces)}"], answer=f"{pieces} PIECES"),
        ])
    return _fin(_sp, 'pizza', locals(), ['n', 'pieces'])


# ------------------------------------------------------------------ 22 birthday paradox
def f_birthday(v):
    n = [23, 30, 40, 50, 57][v]
    q = 1.0
    for i in range(n):
        q *= (365 - i) / 365
    p = (1 - q) * 100
    ps = f"{p:.0f}" if p < 99 else f"{p:.1f}"
    place = ["a classroom", "a football team squad", "a wedding party", "an office floor", "a school bus"][v]
    _sp = dict(
        title="The Birthday Paradox", subtitle=f"{n} people · two share a birthday?", tags=("PROBABILITY", "PUZZLE"),
        headline=f"{n} People In A Room - Chance Two Share A Birthday",
        beats=[
            B(f"There are {w(n)} people in {place}. What are the chances that two of them share the same birthday?", [f"people = {Y(n)}", "days in a year = 365"]),
            B(f"Most people say the chance is tiny. There are {w(365)} days and only {w(n)} people.", [f"your brain: {R_('tiny')}"], stamp=WRONG),
            B(f"But you're not checking one person. You're checking every pair. With {w(n)} people that's {w(n * (n - 1) // 2)} pairs.", [f"{n} × {n - 1} ÷ 2 = {Y(n * (n - 1) // 2)} pairs"]),
            B(f"Work out the chance that nobody matches, and flip it. The chance of at least one match is about {w(int(round(p)))} percent.", [f"chance ≈ {G(ps + '%')}"], answer=f"{ps}%"),
            B(f"Pairs grow much faster than people. That's why it feels impossible.", []),
        ])
    return _fin(_sp, 'birthday', locals(), ['n', 'p', 'ps'])


# ------------------------------------------------------------------ 23 monty hall
def f_monty(v):
    n = [3, 4, 5, 10, 100][v]
    sw = Fraction(n - 1, n)
    _sp = dict(
        title="The Door Puzzle", subtitle=f"{n} doors · 1 car · stay or switch?", tags=("PROBABILITY", "PUZZLE"),
        headline=f"The Monty Hall Problem With {n} Doors - Stay Or Switch",
        beats=[
            B(f"A game show has {w(n)} doors. Behind one is a car, behind the rest are goats. You pick a door.", [f"{Y(n)} doors", f"your chance = 1/{n}"]),
            B(f"The host knows where the car is. He opens {w(n - 2)} other door{'s' if n - 2 != 1 else ''}, all goats. Now only your door and one other are closed.", [f"host opens {Y(n - 2)} goat door{'s' if n - 2 != 1 else ''}"]),
            B(f"Do you stay, or switch? Most people say it's fifty fifty.", [f"your brain: {R_('50 / 50')}"], stamp=WRONG),
            B(f"Your first pick was a {w(1)} in {w(n)} chance, and that never changes. So the other door carries the rest: {w(n - 1)} in {w(n)}.", [f"stay = 1/{n}", f"switch = {G(f'{n - 1}/{n}')}"]),
            B(f"Switching wins {w(n - 1)} out of {w(n)} times. Always switch.", [f"switch wins {G(f'{float(sw) * 100:.0f}%')}"], answer=f"SWITCH: {n - 1}/{n}"),
        ])
    return _fin(_sp, 'monty', locals(), ['n'])


FAMILIES = [f_batball, f_lily, f_widgets, f_avgspeed, f_handshake, f_percent, f_fence, f_frog, f_work, f_water, f_clock, f_allbut, f_socks, f_wheat,
            f_discount, f_race, f_age, f_missing, f_fly, f_logs, f_pizza, f_birthday, f_monty]

CTA = ["Follow for more brain teasers.", "Follow for a new puzzle every day.", "Did you get it? Follow for more.", "Follow, and try the next one.",
       "Comment your answer, then follow for more."]
CTA_TAG = ["CAN YOU SOLVE IT?", "DID YOU GET IT?", "BRAIN TEASER", "TRICKY ONE", "TEST YOUR BRAIN"]


def all_specs(count=100):
    """round-robin over families so every family appears, variants 0..4"""
    out = []
    for v in range(5):
        for f in FAMILIES:
            sp = f(v)
            sp["family"] = f.__name__
            out.append(sp)
    out = out[:count]
    seen = {}
    for i, sp in enumerate(out):
        h = sp["headline"]
        seen[h] = seen.get(h, 0) + 1
        if seen[h] > 1:
            sp["headline"] = f"{h} (Part {seen[h]})"
        sp["beats"].append(B(CTA[i % len(CTA)]))
        sp["cta_tag"] = CTA_TAG[i % len(CTA_TAG)]
        sp["id"] = f"g{i + 1:03d}"
    return out


if __name__ == "__main__":
    sp = all_specs()
    print(len(sp), "specs;", len({s["headline"] for s in sp}), "unique headlines")
    for s in sp[:3]:
        print(s["id"], s["headline"])
        for b in s["beats"]:
            print("   ", b["say"])
