"""Interview problems 77-100 (algorithms, expected value, puzzles). Numbers verified below."""
import math, itertools, random
from fractions import Fraction as Fr
from iq_helpers import *

# --- verification ---
def catalan(n):
    return math.comb(2 * n, n) // (n + 1)
assert catalan(5) == 42
assert math.comb(8, 4) == 70
assert Fr(53, 5) == Fr(53, 5) and abs(float(Fr(53, 5)) - 10.6) < 1e-9          # expected position of first ace (n+1)/(k+1)
assert Fr(sum(max(a, b) for a in range(1, 7) for b in range(1, 7)), 36) == Fr(161, 36)
assert 2 ** 4 - 2 == 14                                              # expected tosses for HHH = 2^(n+1) - 2
assert Fr(1, 2) * Fr(5) + Fr(1, 2) * Fr(7, 2) == Fr(17, 4)           # reroll die once
assert sum(sum(int(c) for c in str(n)) for n in range(1, 1001)) == 13501
assert abs(1 / (2 * math.pi) - 0.159) < 0.001
# tiny simulation for the semicircle probability 3/4
random.seed(1)
hits = 0
for _ in range(100000):
    a = sorted(random.random() * 360 for _ in range(3))
    gaps = [a[1] - a[0], a[2] - a[1], 360 - (a[2] - a[0])]
    hits += max(gaps) > 180
assert abs(hits / 100000 - 0.75) < 0.01


PROBLEMS = [
    prob(77, "Google", "ALGORITHMS", "The Midpoint Overflow Bug", "(low + high) / 2",
         "A famous bug sat in a standard library for almost ten years. One line, and it only breaks on huge arrays.", "THE 9-YEAR\nBINARY SEARCH BUG",
         "In binary search, the line mid equals low plus high, divided by two, looks perfectly fine. Why can it be a bug, and how do you fix it?",
         [H("mid = (low + high) / 2"), ROW(["low", "high"], cols={0: "c", 1: "c"}, w=240, h=120, size=54, y=640), F("what could go wrong?", "y", 0.7)],
         [S("Integers have a maximum, about two billion for thirty two bits. Add two large indexes and the sum exceeds it.", [EQ(["low = 1.5 billion", "high = 1.6 billion", "sum = 3.1 billion  >  2.1 billion"], ["w", "w", "r"], size=48)]),
          S("The sum wraps around to a negative number. Then mid is negative and the program crashes or loops.", [EQ(["3.1 billion → −1.19 billion", "mid < 0 → crash"], ["r", "r"], size=58)]),
          S("The fix: compute low plus half of the gap. Since high minus low is always safe, nothing overflows.", [EQ(["mid = low + (high − low) / 2"], ["g"], size=52)])],
         "low + (high−low)/2", "Compute the midpoint from the difference, not the sum."),

    prob(78, "Google", "SYSTEMS", "Row Major Versus Column Major", "Same loops, ten times slower",
         "Two loops do identical work. One is ten times slower. Why?", "SAME WORK,\n10× SLOWER",
         "You sum every element of a big two dimensional array. Looping rows then columns is much faster than columns then rows. Why?",
         [H("sum a 2D array"), GRID(4, 4, cell=100, fill={"0,0": "c", "0,1": "c", "0,2": "c", "0,3": "c"}, reveal=False, y=660), F("rows first or columns first?", "y", 0.7)],
         [S("The arithmetic is the same either way. The difference is how memory is laid out and read.", [EQ(["same additions, different order"], ["c"], size=54)]),
          S("Arrays are stored row after row in memory. Reading along a row visits neighbouring addresses.", [ROW([1, 2, 3, 4, 5, 6, 7, 8], w=100, h=100, size=50, y=640, hl=[0, 1, 2, 3]), F("row 1 sits together in memory", "c", 0.7)]),
          S("The CPU loads a whole cache line of sixty four bytes at a time. Walking along a row uses every byte it loaded.", [EQ(["1 cache line = 64 bytes", "row walk: all used"], ["w", "g"], size=58)]),
          S("Walking down a column jumps a whole row each step, so nearly every access loads a new cache line and wastes the rest.", [EQ(["column walk: 1 useful value", "per cache line load"], ["r", "r"], size=56)])],
         "CACHE LINES", "Walk memory in order. Spatial locality wins."),

    prob(79, "Microsoft", "SYSTEMS", "Deadlock Four Conditions", "Two threads, two locks",
         "Two threads, two locks, and a program that just stops. What makes a deadlock possible?", "DEADLOCK",
         "What four conditions must all hold for a deadlock to happen, and how do you break one?",
         [H("thread A holds 1, wants 2"), ROW(["thread A", "thread B"], cols={0: "c", 1: "y"}, w=300, h=120, size=48, y=640), F("thread B holds 2, wants 1", "r", 0.7)],
         [S("Thread A holds lock one and waits for lock two. Thread B holds lock two and waits for lock one. Both wait forever.", [NODES(["A", "lock 1", "B", "lock 2"], edges=[(1, 0), (0, 3), (3, 2), (2, 1)], layout="circle", r=50, hl=[0, 2])]),
          S("Four conditions are needed together. Mutual exclusion, hold and wait, no preemption, and circular wait.", [EQ(["mutual exclusion", "hold and wait", "no preemption", "circular wait"], ["c", "y", "p", "r"], size=52)]),
          S("Break just one. The easiest is circular wait: always take locks in the same global order.", [EQ(["lock order: always 1 then 2", "→ no circle → no deadlock"], ["y", "g"], size=54)])],
         "LOCK ORDER", "Always acquire locks in a fixed order."),

    prob(80, "Amazon", "ALGORITHMS", "Queue From Two Stacks", "Amortized O(1)",
         "Build a queue using only two stacks. The cost works out to constant time per operation.", "QUEUE FROM\n2 STACKS",
         "How can you implement a queue using only two stacks, with constant amortized time per operation?",
         [H("stack: last in, first out"), ROW(["in stack", "out stack"], cols={0: "c", 1: "y"}, w=330, h=120, size=48, y=640), F("make a queue (first in, first out)", "y", 0.7)],
         [S("Push every new item onto the in stack. That just stores the arrivals.", [EQ(["enqueue(x) → push on IN"], ["c"], size=60)]),
          S("To dequeue, pop from the out stack. If it's empty, pour all of the in stack into it. That reverses the order.", [EQ(["IN: 1 2 3  (top = 3)", "pour → OUT: 3 2 1  (top = 1)"], ["c", "y"], size=50)]),
          S("Now the oldest item is on top of the out stack. Each item is moved at most once, so the average cost is constant.", [EQ(["each item: 1 push + 1 pour + 1 pop", "amortized O(1)"], ["w", "g"], size=54)])],
         "AMORTIZED O(1)", "Constant time on average."),

    prob(81, "Amazon", "ALGORITHMS", "Stack With Constant Time Minimum", "min() in O(1)",
         "A stack that tells you its minimum instantly, without scanning.", "MIN STACK",
         "Design a stack that supports push, pop and getting the minimum, all in constant time.",
         [H("push / pop / min"), ROW([5, 3, 7, 3, 8], w=130, h=110, size=60, y=640), F("min in O(1)?", "y", 0.7)],
         [S("Scanning for the minimum each time is linear. Remembering one minimum fails when you pop it.", [EQ(["one variable: popping the min", "loses the next min"], ["r", "r"], size=54)], stamp="WRONG"),
          S("Keep a second stack. With each push, also push the minimum seen so far onto it.", [EQ(["push 5 → mins: 5", "push 3 → mins: 5, 3", "push 7 → mins: 5, 3, 3"], ["w", "w", "w"], size=50)]),
          S("To pop, pop both stacks together. The top of the second stack is always the current minimum.", [EQ(["pop 7 → mins: 5, 3", "min = top = 3"], ["w", "g"], size=60)])],
         "TWO STACKS", "A parallel stack of running minimums."),

    prob(82, "Google", "ALGORITHMS", "Kth Largest Element", "Heap of size k",
         "Find the kth largest among a billion numbers, without sorting them all.", "KTH LARGEST\nOF A BILLION",
         "How do you find the kth largest number in a huge stream, using memory proportional to k and about n log k time?",
         [H("n numbers, find the k-th largest"), ROW(["n = 1 billion", "k = 10"], cols={0: "y", 1: "c"}, w=360, h=120, size=40, y=640), F("without sorting everything", "y", 0.7)],
         [S("Sorting costs n log n and needs all the data. For a billion numbers that's slow and heavy.", [EQ(["sort: O(n log n)"], ["r"], size=66)]),
          S("Keep a min heap of size k. It always holds the k largest numbers seen so far, smallest on top.", [ROW([30, 45, 50, 90, 70], w=130, h=110, size=54, y=640, hl=[0]), F("smallest of the top k sits on top", "y", 0.7)]),
          S("For each new number, if it beats the top of the heap, swap them. Each update costs log k.", [EQ(["x > top → pop, push x", "cost log k"], ["c", "y"], size=58)]),
          S("After one pass the top of the heap is the kth largest. Time n log k, memory k.", [EQ(["O(n log k) time", "O(k) memory"], ["g", "g"], size=66)])],
         "MIN HEAP OF SIZE k", "A min heap of size k."),

    prob(83, "Google", "COUNTING", "Binary Trees Catalan Number", "How many BSTs on 5 keys?",
         "How many different binary search trees can you build from five keys?", "HOW MANY\nTREES?",
         "How many structurally different binary search trees can you build with five distinct keys?",
         [H("keys 1, 2, 3, 4, 5"), NODES(["3", "1", "4"], edges=[(0, 1), (0, 2)], xy=[(0.5, 0.2), (0.25, 0.7), (0.75, 0.7)], r=44), F("how many different shapes?", "y", 0.7)],
         [S("Choose a root. Say the root is key three. Then keys one and two go left, four and five go right.", [EQ(["root = 3", "left: {1,2}   right: {4,5}"], ["y", "c"], size=56)]),
          S("The number of trees with n keys is the sum over roots of left count times right count.", [EQ(["T(n) = Σ T(i) · T(n−1−i)"], ["y"], size=54)]),
          S("T of zero is one, T one is one, T two is two, T three is five, T four is fourteen.", [ROW([1, 1, 2, 5, 14], w=140, h=110, size=60, y=640, hl=[4]), F("the Catalan numbers", "c", 0.7)]),
          S("T of five adds up to forty two.", [EQ(["14 + 5 + 4 + 5 + 14 = 42"], ["g"], size=70)])],
         "42", "Forty two. The fifth Catalan number."),

    prob(84, "Apple", "BIT TRICKS", "Gray Code", "One bit changes at a time",
         "Count in binary so that only one bit ever changes between neighbours.", "GRAY CODE",
         "How do you list all two bit numbers so that consecutive numbers differ by exactly one bit, and how do you generate it for any n?",
         [H("00, 01, 10, 11 → 10 changes 2 bits"), ROW(["00", "01", "11", "10"], w=170, h=110, size=56, y=640, cols={0: "g", 1: "g", 2: "g", 3: "g"}), F("one bit changes each step", "g", 0.7)],
         [S("In ordinary binary, going from one to two flips two bits at once. That causes glitches in hardware like encoders.", [EQ(["01 → 10 flips 2 bits"], ["r"], size=60)]),
          S("Reflect and prefix. Take the list zero, one. Mirror it to get one, zero. Prefix zero on the first half, one on the second.", [EQ(["0, 1", "mirror: 1, 0", "00, 01, 11, 10"], ["c", "c", "g"], size=56)]),
          S("Repeat for three bits. The same trick works for any n. Or use the formula: n xor n shifted right by one.", [EQ(["gray(n) = n ⊕ (n >> 1)"], ["g"], size=60)])],
         "n ⊕ (n >> 1)", "One line of code gives the Gray code."),

    prob(85, "Amazon", "COUNTING", "Paths In A Grid", "Right and down only",
         "A robot can only move right or down across a grid. How many different routes are there?", "ROBOT\nON A GRID",
         "A robot starts at the top left of a five by five grid of squares and can only move right or down. How many different paths lead to the bottom right?",
         [H("only right or down"), GRID(5, 5, cell=100, fill={"0,0": "c", "4,4": "g"}, reveal=False, y=690), F("how many paths?", "y", 0.7)],
         [S("Every path is a sequence of moves. To go across a five by five grid you need exactly four rights and four downs.", [EQ(["4 rights + 4 downs", "= 8 moves"], ["c", "y"], size=64)]),
          S("A path is decided by which four of the eight moves are rights. The downs fill the rest.", [ROW(["R", "D", "R", "R", "D", "D", "R", "D"], w=100, h=100, size=54, y=640, cols={0: "c", 2: "c", 3: "c", 6: "c"})]),
          S("That's eight choose four, eight factorial over four factorial squared.", [EQ(["C(8, 4) = 8! / (4! · 4!)", "= 70"], ["w", "g"], size=64)])],
         "70 PATHS", "Seventy paths."),

    prob(86, "Microsoft", "ALGORITHMS", "Dutch National Flag", "Sort 0s, 1s and 2s in one pass",
         "Sort an array of zeros, ones and twos in a single pass with no extra memory.", "SORT 0, 1, 2\nIN ONE PASS",
         "An array contains only zeros, ones and twos. How do you sort it in one pass with constant extra memory?",
         [H("2, 0, 2, 1, 1, 0"), ROW([2, 0, 2, 1, 1, 0], w=130, h=110, size=60, y=640, cols={0: "r", 1: "g", 2: "r", 3: "y", 4: "y", 5: "g"}), F("one pass, O(1) memory", "y", 0.7)],
         [S("Counting works but takes two passes. A comparison sort takes n log n.", [EQ(["count + rewrite: 2 passes"], ["r"], size=60)]),
          S("Use three pointers: low, mid and high. Everything before low is zero, after high is two.", [ROW(["0s", "1s", "unknown", "2s"], cols={0: "g", 1: "y", 2: "d", 3: "r"}, w=230, h=120, size=40, y=640)]),
          S("Look at the mid element. A zero swaps to the low side, a two swaps to the high side, a one is just skipped.", [EQ(["0 → swap with low", "1 → leave", "2 → swap with high"], ["g", "y", "r"], size=54)])],
         "3 POINTERS", "Dijkstra's three way partition. One pass."),

    prob(87, "Amazon", "ALGORITHMS", "Best Time To Buy And Sell", "One pass for maximum profit",
         "Prices over time. Buy once, sell once later. What's the maximum profit?", "BUY LOW,\nSELL HIGH",
         "Given a list of daily stock prices, find the maximum profit from one buy followed by one sell, in a single pass.",
         [H("7, 1, 5, 3, 6, 4"), BARS([7, 1, 5, 3, 6, 4], labels=["d1", "d2", "d3", "d4", "d5", "d6"], base=880, maxh=300, hl=[1, 4]), F("max profit?", "y", 0.7)],
         [S("Trying every buy and sell pair works but takes quadratic time.", [EQ(["all pairs: O(n²)"], ["r"], size=66)]),
          S("Walk once. Track the lowest price so far. At each day, the best profit selling today is today minus that lowest.", [EQ(["low = min(low, price)", "best = max(best, price − low)"], ["c", "y"], size=54)]),
          S("Lowest is one on day two. Selling at six on day five gives five.", [EQ(["buy at 1, sell at 6", "profit = 5"], ["w", "g"], size=70)])],
         "5", "Maximum profit is five."),

    prob(88, "Microsoft", "ALGORITHMS", "Rotate An Array By K", "Three reversals",
         "Rotate an array by k positions in place, in linear time, with a beautiful trick.", "ROTATE AN\nARRAY",
         "How do you rotate an array of n elements to the right by k positions in place, in linear time?",
         [H("rotate right by 3"), ROW([1, 2, 3, 4, 5, 6, 7], w=110, h=100, size=54, y=640), F("in place, O(n)", "y", 0.7)],
         [S("A new array would work but uses extra memory. Shifting one position k times is slow.", [EQ(["new array: O(n) memory", "k shifts: O(n·k) time"], ["r", "r"], size=52)]),
          S("Reverse the whole array first.", [ROW([7, 6, 5, 4, 3, 2, 1], w=110, h=100, size=54, y=640, cols={0: "c", 1: "c", 2: "c"})]),
          S("Then reverse the first k elements, and the remaining n minus k separately.", [ROW([5, 6, 7, 1, 2, 3, 4], w=110, h=100, size=54, y=640, cols={0: "g", 1: "g", 2: "g"}), F("rotated right by 3", "g", 0.7)])],
         "3 REVERSALS", "Reverse all, then reverse each part."),

    prob(89, "Quant", "GAME THEORY", "Nim Game 21 Matches", "Take 1, 2 or 3 per turn",
         "A game of matches where the first player can always force a win. Can you find the rule?", "21 MATCHES",
         "There are twenty one matches. Two players take turns removing one, two or three matches. The one who takes the last match wins. You go first. How do you always win?",
         [H("take 1, 2 or 3 each turn"), ROW(list(range(1, 22)), per=11, w=76, h=76, size=34, y=620), F("last match wins", "y", 0.7)],
         [S("Work backward. If four matches remain on your opponent's turn, he takes one, two or three, and you take the rest and win.", [EQ(["4 left on his turn", "he takes k, you take 4 − k"], ["r", "g"], size=54)]),
          S("So you want to leave a multiple of four every time. Multiples of four are losing positions for the player to move.", [ROW([4, 8, 12, 16, 20], w=140, h=110, size=60, y=640, cols={0: "r", 1: "r", 2: "r", 3: "r", 4: "r"})]),
          S("From twenty one, take one to leave twenty. Whatever he takes, you take enough to make the total four.", [EQ(["21 − 1 = 20", "he takes k → you take 4 − k"], ["g", "w"], size=60)])],
         "TAKE 1 FIRST", "Take one first, then always complete the group to four."),

    prob(90, "Quant", "PROBABILITY", "First Ace In A Shuffled Deck", "Where does the first ace appear?",
         "Shuffle a deck and flip cards until you hit an ace. How many flips on average?", "FIRST ACE\nIN A DECK",
         "You shuffle a standard fifty two card deck and turn cards over one at a time. On average, which position holds the first ace?",
         [H("52 cards, 4 aces"), ROW(["A", "A", "A", "A"], cols={0: "y", 1: "y", 2: "y", 3: "y"}, w=150, h=120, size=64, y=640), F("expected position of the first ace?", "y", 0.7)],
         [S("A guess of thirteen comes from fifty two over four. That's close, but a bit too high.", [BIG("13 ?", "r", size=130)], stamp="WRONG"),
          S("The four aces split the other forty eight cards into five gaps. By symmetry each gap has the same expected size.", [EQ(["48 non-aces ÷ 5 gaps = 9.6"], ["c"], size=58)]),
          S("The first ace comes after the first gap of nine point six cards, so it's at position ten point six.", [EQ(["9.6 + 1 = 10.6"], ["g"], size=88)])],
         "10.6", "About position ten point six, which is fifty three over five."),

    prob(91, "Quant", "PROBABILITY", "Expected Maximum Of Two Dice", "Roll two dice, take the larger",
         "Roll two dice and keep the higher. What's the average?", "THE HIGHER\nOF TWO DICE",
         "You roll two fair dice and keep the larger value. What's the expected value?",
         [H("max of two dice"), ROW([3, 5, "→ 5"], w=160, h=120, size=64, y=640, cols={2: "g"}), F("expected value?", "y", 0.7)],
         [S("One die averages three and a half. Taking the max must be higher, but by how much?", [EQ(["one die: 3.5", "max of two: > 3.5"], ["c", "y"], size=60)]),
          S("Count outcomes by the max. A max of one happens in one of thirty six outcomes, two in three, three in five, four in seven, five in nine, and six in eleven.", [ROW([1, 3, 5, 7, 9, 11], w=140, h=110, size=54, y=640, hl=[5]), F("ways for max = 1, 2, ... 6", "c", 0.7)]),
          S("Weight each max by its count and divide by thirty six. That's one sixty one over thirty six.", [EQ(["(1·1 + 2·3 + 3·5 + 4·7 + 5·9 + 6·11) / 36", "= 161 / 36 ≈ 4.47"], ["w", "g"], size=46)])],
         "4.47", "About four point four seven."),

    prob(92, "Quant", "PROBABILITY", "Drunkard's Walk Distance 10", "Expected steps to drift 10 away",
         "A random walker steps left or right with equal chance. How long to reach distance ten?", "THE DRUNKARD'S\nWALK",
         "A walker starts at zero and takes steps of plus one or minus one with equal probability. On average, how many steps until he first reaches ten or minus ten?",
         [H("start at 0, stop at ±10"), NUM(-10, 10, ticks=[-10, 0, 10], marks=[(0, "start", "c"), (-10, "stop", "r"), (10, "stop", "r")], y=700), F("expected steps?", "y", 0.7)],
         [S("Many guess ten, since you need ten net steps. But random steps cancel each other out.", [BIG("10 ?", "r", size=130)], stamp="WRONG"),
          S("For a walk between minus a and plus a, the expected time is a squared. Distance grows like the square root of time.", [EQ(["E[T] = a²"], ["y"], size=80)]),
          S("With a equal to ten, that's one hundred steps.", [EQ(["10² = 100 steps"], ["g"], size=88)])],
         "100 STEPS", "One hundred steps on average."),

    prob(93, "Quant", "GEOMETRY", "Three Points On A Circle", "In the same semicircle?",
         "Throw three points at random on a circle. How likely is it that they all fall in one half?", "3 POINTS\nON A CIRCLE",
         "Three points are chosen at random on a circle. What's the probability that all three lie in the same semicircle?",
         [H("3 random points"), NODES(["P", "Q", "R"], xy=[(0.5, 0.05), (0.15, 0.8), (0.85, 0.8)], r=44, hl=[0, 1, 2]), F("all in one semicircle?", "y", 0.7)],
         [S("Fix point P. Each other point is on either side. Think of the three points separately.", [EQ(["fix P", "Q and R land anywhere"], ["c", "w"], size=60)]),
          S("For the three to be in a semicircle, one of them must be the first point clockwise with the other two within half a turn of it.", [EQ(["exactly one point is the 'leader'", "other two within 180° after it"], ["w", "c"], size=48)]),
          S("For a given point as leader, the chance both others fall in the half circle after it is one half times one half, one quarter. Three leaders, mutually exclusive.", [EQ(["3 × (1/2 × 1/2) = 3/4"], ["g"], size=70)])],
         "3/4", "Three quarters."),

    prob(94, "Quant", "PROBABILITY", "Three Heads In A Row", "Expected tosses for HHH",
         "How many coin tosses until you see three heads in a row?", "HHH",
         "You toss a fair coin until you get three heads in a row. On average, how many tosses does it take?",
         [H("until H H H"), ROW(["H", "H", "H"], cols={0: "c", 1: "c", 2: "c"}, w=170, h=130, size=80, y=640), F("expected tosses?", "y", 0.7)],
         [S("For one head it's two tosses. For two in a row it's six. The pattern isn't linear.", [EQ(["H: 2", "HH: 6", "HHH: ?"], ["w", "w", "y"], size=60)]),
          S("Each time you get a tail, you fall back to zero. After a run of k heads, it costs you an expected amount to get one more.", [EQ(["E3 = 2·E2 + 2"], ["y"], size=72)]),
          S("A general rule: waiting for n heads takes two to the n plus one, minus two.", [EQ(["2^(n+1) − 2", "n = 3 → 16 − 2"], ["w", "g"], size=64)])],
         "14 TOSSES", "Fourteen tosses on average."),

    prob(95, "Quant", "PROBABILITY", "Children Until A Boy And A Girl", "Expected family size",
         "A couple keeps having children until they have both a boy and a girl. How many on average?", "BOY AND GIRL",
         "A couple has children until they have at least one boy and at least one girl. Each child is equally likely to be either. How many children do they have on average?",
         [H("stop at one of each"), ROW(["boy", "girl"], cols={0: "c", 1: "y"}, w=260, h=120, size=54, y=640), F("expected number of children?", "y", 0.7)],
         [S("The first child is whatever it is. Now they need the opposite sex.", [EQ(["1st child: any", "now need the other"], ["w", "c"], size=60)]),
          S("Each new child is the one they need with probability one half. Waiting for a one half chance takes two tries on average.", [EQ(["wait ~ 1 / (1/2) = 2"], ["y"], size=64)]),
          S("One plus two is three.", [EQ(["1 + 2 = 3"], ["g"], size=110)])],
         "3 CHILDREN", "Three children on average."),

    prob(96, "Quant", "PROBABILITY", "Die With One Reroll", "Keep it or roll again",
         "You roll a die. You may keep it, or roll once more and must keep the second. When do you reroll?", "ROLL\nOR KEEP?",
         "You roll a die and see the result. You may take it as your payoff, or roll again and must take the second result. What's your best strategy and expected payoff?",
         [H("one optional reroll"), ROW([1, 2, 3, 4, 5, 6], w=110, h=110, size=60, y=640), F("when do you roll again?", "y", 0.7)],
         [S("A fresh roll is worth three and a half on average. So keep anything above three and a half, reroll anything below.", [EQ(["reroll value = 3.5", "keep 4, 5, 6", "reroll 1, 2, 3"], ["c", "g", "r"], size=54)]),
          S("Half the time you keep a four, five or six, averaging five. Half the time you reroll, averaging three and a half.", [EQ(["1/2 × 5 + 1/2 × 3.5"], ["w"], size=58)]),
          S("That's two point five plus one point seven five, which is four point two five.", [EQ(["2.5 + 1.75 = 4.25"], ["g"], size=80)])],
         "4.25", "Four point two five."),

    prob(97, "Top Tech", "LOGIC", "Ants On A Stick", "Collisions don't matter",
         "Ants walk along a one metre stick and bounce off each other. When is the last ant off?", "ANTS ON\nA STICK",
         "Many ants are placed at random spots on a one metre stick, each walking left or right at one metre per minute. When two meet they turn around. What's the longest time before every ant has fallen off?",
         [H("1 metre stick, 1 m/min"), ROW(["ant", "ant", "ant", "ant"], cols={0: "y", 1: "c", 2: "y", 3: "c"}, w=200, h=100, size=40, y=640), F("longest time until all fall off?", "y", 0.7)],
         [S("Tracking all the bounces looks hopeless. But there's a trick that makes collisions disappear.", [EQ(["bounces: a mess"], ["r"], size=70)]),
          S("When two ants meet and turn around, it's the same as if they passed through each other and swapped names.", [EQ(["bounce  ≡  pass through"], ["c"], size=64)]),
          S("So treat each ant as a ghost walking straight. The worst case is an ant starting at one end, walking the full metre.", [EQ(["worst ant walks 1 m at 1 m/min", "= 1 minute"], ["w", "g"], size=58)])],
         "1 MINUTE", "One minute."),

    prob(98, "Top Tech", "MATH", "Rope Around The Earth", "Add one metre, how high is the gap?",
         "A rope hugs the earth's equator. Add one metre of length. How far above the ground is it now?", "ROPE AROUND\nTHE EARTH",
         "A rope is tied tightly around the earth's equator, about forty thousand kilometres. You add one metre to its length and lift it evenly all the way around. How high above the ground is the rope?",
         [H("rope around the equator"), ROW(["40,000 km", "+ 1 m"], cols={0: "c", 1: "y"}, w=320, h=120, size=48, y=640), F("how high is the gap?", "y", 0.7)],
         [S("Most people think the gap is tiny, a hair's width, because one metre is so small compared with forty thousand kilometres.", [BIG("a hair?", "r", size=120)], stamp="WRONG"),
          S("Circumference is two pi r. Adding one metre to it adds one over two pi to the radius.", [EQ(["C = 2πr", "ΔC = 2π Δr"], ["w", "y"], size=64)]),
          S("So the rope rises by one over two pi, about sixteen centimetres. And it doesn't matter how big the circle is.", [EQ(["Δr = 1 / (2π) ≈ 0.16 m"], ["g"], size=60), F("same for a coin or the earth", "c", 0.7)])],
         "16 cm", "About sixteen centimetres, whether it's a coin or the planet."),

    prob(99, "Microsoft", "LOGIC", "Hourglasses 7 And 4 Make 9", "Measure 9 minutes",
         "A seven minute and a four minute hourglass. Measure exactly nine minutes.", "MEASURE\n9 MINUTES",
         "You have a seven minute hourglass and a four minute hourglass. How do you measure exactly nine minutes?",
         [H("7 minute and 4 minute glasses"), ROW(["7 min", "4 min"], cols={0: "y", 1: "c"}, w=280, h=130, size=54, y=640), F("measure exactly 9 minutes", "y", 0.7)],
         [S("Start both hourglasses at the same moment. At minute four the small one runs out. Flip it immediately.", [TL([("7 min", 0, 7, "y"), ("4 min", 0, 4, "c"), ("4 min flipped", 4, 8, "c")], total=9, step=1)]),
          S("At minute seven the large one is empty. The small one has one minute left. Flip the large one.", [TL([("7 min", 0, 7, "y"), ("4 min flipped", 4, 8, "c"), ("7 min flipped", 7, 9, "y")], total=9, step=1)]),
          S("At minute eight the small one runs out. The large one has run one minute, so one minute of sand has fallen. Flip it.", [TL([("4 min flipped", 4, 8, "c"), ("7 min flipped", 7, 8, "y"), ("flip: 1 min left", 8, 9, "g")], total=9, step=1)]),
          S("That last one minute of sand runs out at minute nine.", [EQ(["8 + 1 = 9 minutes"], ["g"], size=88)])],
         "9 MINUTES", "Nine minutes."),

    prob(100, "Harvard", "NUMBER THEORY", "Sum Of Digits 1 To 1000", "Add every digit",
         "Add every digit of every number from one to one thousand. There's no need to add them one by one.", "SUM OF ALL\nTHE DIGITS",
         "What is the sum of all the digits of all the numbers from one to one thousand?",
         [H("1, 2, 3, ... 1000"), EQ(["every digit added = ?"], ["y"], size=60), F("without adding one by one", "y", 0.7)],
         [S("Think of numbers from zero to nine hundred ninety nine as three digit strings, with leading zeros allowed.", [EQ(["000, 001, ..., 999", "1000 numbers, 3 digits each"], ["c", "w"], size=56)]),
          S("In each of the three positions, every digit from zero to nine appears exactly a hundred times.", [EQ(["each digit 0-9 appears 100 times", "per position"], ["w", "y"], size=54)]),
          S("The digits zero to nine add to forty five. So one position contributes forty five hundred.", [EQ(["45 × 100 = 4500"], ["g"], size=90)]),
          S("Three positions give thirteen thousand five hundred. Add the one from the number one thousand.", [EQ(["3 × 4500 = 13,500", "+ 1 = 13,501"], ["w", "g"], size=70)])],
         "13,501", "Thirteen thousand five hundred and one."),
]
