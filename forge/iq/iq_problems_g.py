"""Interview problems 126-150 (algorithms, data structures, systems, SQL). Answers verified by running the algorithms below."""
import math
from iq_helpers import *

# ---- verification by running the algorithms ----
def trap(h):
    l, r, lm, rm, t = 0, len(h) - 1, 0, 0, 0
    while l < r:
        if h[l] < h[r]:
            lm = max(lm, h[l]); t += lm - h[l]; l += 1
        else:
            rm = max(rm, h[r]); t += rm - h[r]; r -= 1
    return t
assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

def water(h):
    l, r, b = 0, len(h) - 1, 0
    while l < r:
        b = max(b, min(h[l], h[r]) * (r - l))
        if h[l] < h[r]: l += 1
        else: r -= 1
    return b
assert water([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49

def coins(c, a):
    dp = [0] + [10 ** 9] * a
    for x in range(1, a + 1):
        for k in c:
            if k <= x: dp[x] = min(dp[x], dp[x - k] + 1)
    return dp[a], dp
assert coins([1, 2, 5], 11)[0] == 3

def lis(a):
    d = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]: d[i] = max(d[i], d[j] + 1)
    return max(d)
assert lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4

def edit(a, b):
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1): d[i][0] = i
    for j in range(len(b) + 1): d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    return d[-1][-1]
assert edit("kitten", "sitting") == 3

def islands(g):
    seen, n = set(), 0
    for r in range(len(g)):
        for c in range(len(g[0])):
            if g[r][c] == 1 and (r, c) not in seen:
                n += 1
                st = [(r, c)]
                while st:
                    y, x = st.pop()
                    if (y, x) in seen or not (0 <= y < len(g) and 0 <= x < len(g[0])) or g[y][x] != 1: continue
                    seen.add((y, x)); st += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    return n
ISLAND_GRID = [[1, 1, 0, 0, 0], [1, 1, 0, 0, 1], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1]]
assert islands(ISLAND_GRID) == 4

def fib_calls(n):
    return 1 if n < 2 else 1 + fib_calls(n - 1) + fib_calls(n - 2)
assert fib_calls(20) == 2 * 10946 - 1                      # 2*F(21)-1 pattern
FIB = [0, 1]
for _ in range(60): FIB.append(FIB[-1] + FIB[-2])
assert 2 * FIB[41] - 1 == 331160281                          # calls for fib(40)

def mults(n):
    s = bin(n)[2:]
    return (len(s) - 1) + (s.count("1") - 1)
assert mults(100) == 8 and 3 ** 100 > 0
assert (12 & -12) == 4
def prof2(p):
    return sum(max(0, p[i + 1] - p[i]) for i in range(len(p) - 1))
assert prof2([7, 1, 5, 3, 6, 4]) == 7

def jump(a):
    far = 0
    for i, x in enumerate(a):
        if i > far: return False
        far = max(far, i + x)
    return True
assert jump([2, 3, 1, 1, 4]) and not jump([3, 2, 1, 0, 4])

def subsum(a, k):
    cnt, pre, seen = 0, 0, {0: 1}
    for x in a:
        pre += x
        cnt += seen.get(pre - k, 0)
        seen[pre] = seen.get(pre, 0) + 1
    return cnt
assert subsum([1, 1, 1], 2) == 2
assert 1000 ** 3 == 10 ** 9
s = "amanaplanacanalpanama"
assert s == s[::-1]

PROBLEMS = [
    prob(126, "Google", "ALGORITHMS", "Trapping Rain Water", "How much water sits between the bars?",
         "After the rain, how much water is trapped between these bars? One pass, no extra array.", "TRAPPED\nRAIN WATER",
         "Given bar heights, how much rain water is trapped between them? The heights are zero, one, zero, two, one, zero, one, three, two, one, two, one.",
         [H("bar heights"), BARS([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], base=880, maxh=240, hl=[7], fmt="{}"), F("water trapped?", "y", 0.7)],
         [S("At each position, the water level is the smaller of the tallest bar to its left and the tallest bar to its right, minus the bar itself.", [EQ(["water[i] = min(maxLeft, maxRight) − h[i]"], ["y"], size=46)]),
          S("Computing those two maxima for every position takes extra memory. Instead use two pointers from both ends.", [ROW(["left →", "← right"], cols={0: "c", 1: "c"}, w=300, h=120, size=48, y=640)]),
          S("Move the pointer at the shorter side, because that side's water level is already known. Add the gap between its running max and the bar.", [EQ(["h[left] < h[right]: use maxLeft", "else: use maxRight"], ["c", "y"], size=50)]),
          S("Summing across the array gives six units of water.", [EQ(["total = 6"], ["g"], size=110)])],
         "6", "Six units. One pass, constant memory."),

    prob(127, "Amazon", "ALGORITHMS", "Container With Most Water", "Two lines, widest area",
         "Pick two lines to form a container. Which pair holds the most water?", "MOST WATER\nIN A CONTAINER",
         "Given the heights one, eight, six, two, five, four, eight, three, seven, pick two lines that together with the x axis hold the most water. What's the maximum?",
         [H("heights 1 8 6 2 5 4 8 3 7"), BARS([1, 8, 6, 2, 5, 4, 8, 3, 7], base=880, maxh=260, hl=[1, 8], fmt="{}"), F("maximum area?", "y", 0.7)],
         [S("The area of a pair is the shorter height times the distance between them. Checking every pair is quadratic.", [EQ(["area = min(h1, h2) × distance", "all pairs: O(n²)"], ["y", "r"], size=52)]),
          S("Start with the two outer lines, the widest container. Then move the pointer at the shorter line inward.", [EQ(["move the shorter side"], ["c"], size=64)]),
          S("Moving the taller side could never help, because width shrinks and the height is still capped by the shorter line.", [EQ(["taller side: width ↓, height same"], ["r"], size=52)]),
          S("The best pair is eight at index one and seven at index eight: seven times seven, forty nine.", [EQ(["min(8, 7) × 7 = 49"], ["g"], size=80)])],
         "49", "Forty nine."),

    prob(128, "Amazon", "ALGORITHMS", "Coin Change Minimum Coins", "Make 11 with 1, 2 and 5",
         "Make eleven cents with the fewest coins. Greedy doesn't always work, but here is the method that does.", "FEWEST COINS",
         "With coins of one, two and five, what is the fewest number of coins that make eleven?",
         [H("coins 1, 2, 5   target 11"), ROW([1, 2, 5, "= 11 ?"], w=170, h=120, size=64, y=640), F("fewest coins?", "y", 0.7)],
         [S("Greedy takes the biggest coin first. Here that gives five, five, one. That works, but it fails for other coin sets.", [EQ(["5 + 5 + 1 = 11", "3 coins"], ["w", "c"], size=60)]),
          S("Dynamic programming is always right. Let best of x be the fewest coins for amount x. Try each coin.", [EQ(["best[x] = 1 + min(best[x − c])"], ["y"], size=54)]),
          S("Build from zero. Best of zero is zero, one is one, two is one, three is two, four is two, five is one.", [ROW([0, 1, 1, 2, 2, 1], w=130, h=110, size=60, y=640), F("best[0..5]", "c", 0.7)]),
          S("Keep going to eleven: best of eleven is best of six plus one, which is three.", [EQ(["best[11] = 3"], ["g"], size=100)])],
         "3 COINS", "Three coins."),

    prob(129, "Google", "ALGORITHMS", "Longest Increasing Subsequence", "Not necessarily contiguous",
         "Find the longest run of numbers that keep increasing, skipping some along the way.", "LONGEST\nINCREASING RUN",
         "Given ten, nine, two, five, three, seven, one hundred one, eighteen, what's the length of the longest strictly increasing subsequence?",
         [H("10 9 2 5 3 7 101 18"), ROW([10, 9, 2, 5, 3, 7, 101, 18], w=100, h=100, size=50, y=640), F("longest increasing subsequence?", "y", 0.7)],
         [S("A subsequence may skip elements but must keep the order. So two, five, seven, one hundred one works.", [ROW([2, 5, 7, 101], w=150, h=110, size=60, y=640, cols={0: "g", 1: "g", 2: "g", 3: "g"})]),
          S("Dynamic programming: for each element, the best length ending there is one plus the best among earlier smaller elements.", [EQ(["L[i] = 1 + max L[j]  for a[j] < a[i]"], ["y"], size=48)]),
          S("The lengths come out one, one, one, two, two, three, four, four.", [ROW([1, 1, 1, 2, 2, 3, 4, 4], w=100, h=100, size=54, y=640, hl=[6, 7])]),
          S("The largest is four.", [EQ(["max L = 4"], ["g"], size=100)])],
         "4", "Length four."),

    prob(130, "Google", "ALGORITHMS", "Edit Distance Kitten To Sitting", "Fewest edits between two words",
         "How many single letter edits turn kitten into sitting?", "KITTEN\n→ SITTING",
         "What's the minimum number of single character insertions, deletions or substitutions needed to turn kitten into sitting?",
         [H("kitten  →  sitting"), ROW(["kitten", "sitting"], cols={0: "c", 1: "y"}, w=330, h=120, size=54, y=640), F("fewest edits?", "y", 0.7)],
         [S("Try it by hand: replace k with s, replace e with i, then add a g at the end.", [ROW(["kitten", "sitten", "sittin", "sitting"], w=210, h=110, size=40, y=640, cols={3: "g"})]),
          S("To prove three is the minimum, build a table. Each cell is the cheapest way to turn a prefix of one word into a prefix of the other.", [EQ(["d[i][j] = min(delete, insert, substitute)"], ["y"], size=46)]),
          S("Each cell looks at its three neighbours. The bottom right cell holds the answer.", [EQ(["d[6][7] = 3"], ["g"], size=100)])],
         "3 EDITS", "Three edits."),

    prob(131, "Amazon", "ALGORITHMS", "Number Of Islands", "Count connected groups of land",
         "Count the islands on a map made of ones and zeros.", "COUNT THE\nISLANDS",
         "Given a grid of land and water, count the number of islands, where an island is a group of land cells connected up, down, left or right.",
         [H("land = 1, water = 0"), GRID(4, 5, cell=100, fill={"0,0": "c", "0,1": "c", "1,0": "c", "1,1": "c", "1,4": "y", "2,2": "p", "3,3": "g", "3,4": "g"}, reveal=False, y=690), F("how many islands?", "y", 0.7)],
         [S("Scan the grid cell by cell. When you meet unvisited land, you've found a new island.", [EQ(["new land cell → count + 1"], ["c"], size=58)]),
          S("From there, flood fill: visit every connected land cell and mark it, so you never count it again.", [EQ(["DFS / BFS flood fill"], ["y"], size=64)]),
          S("In this grid, the groups are the top left block, the single cell on the right, the middle cell, and the bottom right pair.", [EQ(["4 groups"], ["g"], size=100)])],
         "4 ISLANDS", "Four islands, in linear time."),

    prob(132, "Google", "ALGORITHMS", "Course Schedule Cycle Detection", "Can you finish all courses?",
         "Some courses need others first. Is there a way to finish them all?", "CAN YOU FINISH\nALL COURSES?",
         "Courses have prerequisites. Course A needs B, B needs C, and C needs A. How do you check whether all courses can be completed?",
         [H("A needs B, B needs C, C needs A"), NODES(["A", "B", "C"], edges=[(0, 1), (1, 2), (2, 0)], xy=[(0.5, 0.15), (0.2, 0.75), (0.8, 0.75)], r=50, hl=[0, 1, 2]), F("is there a valid order?", "y", 0.7)],
         [S("Model it as a directed graph, with an arrow from each course to its prerequisite.", [EQ(["course → prerequisite"], ["c"], size=64)]),
          S("A valid order exists exactly when the graph has no cycle. Use topological sort: repeatedly take courses with no remaining prerequisites.", [EQ(["take courses with 0 prerequisites", "remove them, repeat"], ["c", "y"], size=52)]),
          S("Here every course always has one prerequisite left, so nothing can start. The sort gets stuck.", [EQ(["stuck → cycle"], ["r"], size=90)])],
         "IMPOSSIBLE", "Impossible, because there's a cycle."),

    prob(133, "Microsoft", "COMPLEXITY", "Quicksort Worst Case", "Why sorted input can hurt",
         "Quicksort is fast on average, but one input makes it quadratic. Which one?", "QUICKSORT'S\nWORST CASE",
         "What input makes quicksort slow, quadratic time, when the pivot is always the first element?",
         [H("pivot = first element"), ROW([1, 2, 3, 4, 5, 6], w=120, h=110, size=60, y=640), F("what's the worst case?", "y", 0.7)],
         [S("Quicksort splits around a pivot. A good pivot splits the array roughly in half, giving n log n.", [EQ(["balanced split → O(n log n)"], ["g"], size=56)]),
          S("On sorted input, the first element is the smallest. Everything lands on one side, and the split is zero versus n minus one.", [EQ(["pivot 1 → [] and [2..n]", "pivot 2 → [] and [3..n]"], ["r", "r"], size=52)]),
          S("That gives n levels, each doing about n work. Total n squared.", [EQ(["n + (n−1) + ... + 1 = O(n²)"], ["r"], size=56)]),
          S("The fix is a random pivot or median of three.", [EQ(["random pivot → expected O(n log n)"], ["g"], size=52)])],
         "O(n²)", "Already sorted input with a first element pivot."),

    prob(134, "Google", "COMPLEXITY", "Dynamic Array Amortized Cost", "Doubling makes append O(1)",
         "Appending to an array sometimes copies everything. So why is append called constant time?", "APPEND IS\nO(1)?",
         "A dynamic array doubles its capacity when full. Why is appending still constant time on average?",
         [H("capacity doubles when full"), ROW([1, 2, 4, 8, 16], w=140, h=110, size=60, y=640), F("why O(1) amortized?", "y", 0.7)],
         [S("When the array is full, an append copies every element. That single append costs n.", [EQ(["full → copy n items"], ["r"], size=62)]),
          S("But copies only happen at sizes one, two, four, eight, sixteen. The copy costs form a geometric series.", [EQ(["1 + 2 + 4 + 8 + ... + n/2 + n ≈ 2n"], ["y"], size=50)]),
          S("Spread two n over n appends: about two units per append.", [EQ(["2n / n = 2 per append"], ["g"], size=62)]),
          S("So the amortized cost is constant, even though one append is expensive.", [EQ(["amortized O(1)"], ["g"], size=88)])],
         "AMORTIZED O(1)", "Constant, thanks to doubling."),

    prob(135, "Amazon", "SYSTEMS", "B-Tree Index Billion Rows", "How deep for 1,000,000,000 rows?",
         "A database finds one row among a billion in just a few disk reads. How?", "1 BILLION ROWS\n3 READS",
         "A B-tree index has about one thousand keys per node. How many levels does it need to index one billion rows?",
         [H("fan-out about 1,000"), ROW(["1,000", "× 1,000", "× 1,000"], w=250, h=120, size=54, y=640), F("how many levels?", "y", 0.7)],
         [S("A binary tree needs thirty levels for a billion rows, and each level could be a disk read. That's slow.", [EQ(["binary tree: log₂ 10⁹ ≈ 30"], ["r"], size=52)]),
          S("A B-tree node holds many keys, so each level multiplies by about one thousand.", [EQ(["level 1: 1,000", "level 2: 1,000,000", "level 3: 1,000,000,000"], ["w", "w", "g"], size=52)]),
          S("Three levels already cover a billion rows. And the top levels sit in memory.", [EQ(["3 levels", "≈ 1–2 disk reads"], ["g", "c"], size=70)])],
         "3 LEVELS", "About three levels, so one or two disk reads."),

    prob(136, "Microsoft", "SYSTEMS", "TCP Three Way Handshake", "How a connection starts",
         "Before any data moves, two computers agree to talk. In exactly three messages.", "TCP\nHANDSHAKE",
         "How does TCP establish a connection, and why does it need three messages?",
         [H("client and server"), ROW(["client", "server"], cols={0: "c", 1: "y"}, w=300, h=120, size=54, y=640), F("how do they connect?", "y", 0.7)],
         [S("First, the client sends SYN: I want to connect, and here's my starting number.", [EQ(["client → server:  SYN"], ["c"], size=60)]),
          S("Second, the server replies SYN ACK: I got yours, and here's my starting number.", [EQ(["server → client:  SYN-ACK"], ["y"], size=60)]),
          S("Third, the client sends ACK: I got yours too. Now both sides know the other can send and receive.", [EQ(["client → server:  ACK", "connection open"], ["c", "g"], size=60)]),
          S("Three messages are the minimum for both sides to confirm each other's number.", [EQ(["2 messages: server can't be sure"], ["r"], size=52)])],
         "SYN, SYN-ACK, ACK", "Three messages: SYN, SYN-ACK, ACK."),

    prob(137, "Meta", "SQL", "Second Highest Salary In SQL", "A classic database question",
         "Write a query that returns the second highest salary. Simple, until duplicates show up.", "2ND HIGHEST\nSALARY",
         "Given an employees table with a salary column, how do you return the second highest distinct salary?",
         [H("employees(salary)"), ROW([100, 300, 300, 200], w=170, h=110, size=60, y=640), F("2nd highest distinct salary?", "y", 0.7)],
         [S("A common mistake: order descending and take row two. With duplicates, that returns the top salary again.", [EQ(["300, 300, 200", "row 2 = 300  (wrong)"], ["w", "r"], size=58)], stamp="WRONG"),
          S("Use distinct, order descending, skip one, take one.", [EQ(["SELECT DISTINCT salary", "FROM employees", "ORDER BY salary DESC", "LIMIT 1 OFFSET 1;"], ["c", "w", "w", "g"], size=48)]),
          S("Or use a subquery: the maximum salary below the overall maximum. It returns null if there's no second salary.", [EQ(["SELECT MAX(salary) FROM employees", "WHERE salary < (SELECT MAX(salary)", "FROM employees);"], ["y", "w", "w"], size=42)])],
         "DISTINCT + OFFSET 1", "Distinct, descending, offset one."),

    prob(138, "Meta", "SQL", "Find Duplicate Emails In SQL", "GROUP BY and HAVING",
         "Find all duplicates in a column with one short query.", "FIND THE\nDUPLICATES",
         "Given a users table with an email column, how do you list all emails that appear more than once?",
         [H("users(email)"), ROW(["a@x.com", "b@x.com", "a@x.com"], cols={0: "r", 2: "r"}, w=270, h=110, size=36, y=640), F("which emails repeat?", "y", 0.7)],
         [S("Group the rows by email, so identical emails land in the same group.", [EQ(["GROUP BY email"], ["c"], size=70)]),
          S("Then keep only groups that have more than one row. You can't use WHERE for that, because WHERE runs before grouping.", [EQ(["HAVING COUNT(*) > 1"], ["y"], size=64)]),
          S("Together: select email, group by email, having count greater than one.", [EQ(["SELECT email FROM users", "GROUP BY email", "HAVING COUNT(*) > 1;"], ["w", "c", "g"], size=52)])],
         "GROUP BY + HAVING", "Group by email, having count greater than one."),

    prob(139, "Google", "COMPLEXITY", "Fibonacci 40 Naive Recursion", "331 million calls",
         "A tiny recursive function that takes hundreds of millions of calls to compute fib of forty.", "FIB(40)\nTAKES 331 MILLION CALLS",
         "The naive recursive Fibonacci function calls itself twice. How many calls does it make to compute fib of forty, and how do you fix it?",
         [H("fib(n) = fib(n−1) + fib(n−2)"), NODES(["f(4)", "f(3)", "f(2)", "f(2)", "f(1)", "f(1)"], edges=[(0, 1), (0, 2), (1, 3), (1, 4)], xy=[(0.5, 0.1), (0.3, 0.45), (0.7, 0.45), (0.15, 0.8), (0.45, 0.8), (0.85, 0.8)], r=38), F("how many calls for fib(40)?", "y", 0.7)],
         [S("Each call spawns two more, and they recompute the same values again and again. fib of two alone is computed many times.", [EQ(["f(5) calls f(3) 2×, f(2) 3×"], ["r"], size=52)]),
          S("The number of calls grows like the Fibonacci numbers themselves. For fib of forty it's about three hundred thirty one million.", [EQ(["calls = 2·F(41) − 1", "= 331,160,281"], ["w", "r"], size=58)]),
          S("The fix: remember each result, called memoization, or build up from the bottom.", [EQ(["memo: each fib(k) once"], ["g"], size=60)]),
          S("Then it takes just forty steps. Exponential becomes linear.", [EQ(["O(2^n) → O(n)"], ["g"], size=90)])],
         "331,160,281 CALLS", "Three hundred thirty one million calls, versus forty with memoization."),

    prob(140, "Apple", "COMPLEXITY", "Fast Exponentiation 3 To The 100", "Square and multiply",
         "How many multiplications does it take to compute three to the power one hundred? Far fewer than ninety nine.", "3^100\nIN 8 STEPS",
         "How many multiplications are needed to compute three to the one hundredth power, using the fewest with binary exponentiation?",
         [H("3^100"), ROW(["99 multiplications?"], cols={0: "r"}, w=620, h=120, size=48, y=640), F("fewest multiplications?", "y", 0.7)],
         [S("Multiplying three by itself ninety nine times works but is slow, especially for huge exponents.", [EQ(["naive: n − 1 multiplications"], ["r"], size=56)], stamp="WRONG"),
          S("Write one hundred in binary: one one zero zero one zero zero. Squaring repeatedly doubles the exponent each time.", [ROW([1, 1, 0, 0, 1, 0, 0], w=110, h=100, size=54, y=640, hl=[0, 1, 4]), F("100 = 1100100₂", "c", 0.65)]),
          S("Six squarings reach three to the sixty four. Multiply in the ones bits: thirty two and four.", [EQ(["3^2, 3^4, 3^8, 3^16, 3^32, 3^64", "6 squarings"], ["w", "c"], size=50)]),
          S("Two more multiplications to combine: eight in total.", [EQ(["6 + 2 = 8 multiplications"], ["g"], size=70)])],
         "8 STEPS", "Eight multiplications, logarithmic in the exponent."),

    prob(141, "Apple", "BIT TRICKS", "Isolate The Lowest Set Bit", "n and minus n",
         "Pull out the lowest one bit of a number in one operation.", "LOWEST SET BIT",
         "How do you isolate the lowest set bit of an integer in one expression?",
         [H("12 = 1100"), ROW([1, 1, 0, 0], w=150, h=120, size=64, y=640, hl=[1]), F("which bit is the lowest 1?", "y", 0.7)],
         [S("Loop over the bits until you hit a one. That works, but takes up to thirty two steps.", [EQ(["loop: O(bits)"], ["r"], size=64)]),
          S("In two's complement, negative n is the bitwise flip of n, plus one. The flip changes all bits, and adding one carries up to the lowest set bit.", [EQ(["n = 0000 1100", "−n = 1111 0100"], ["w", "c"], size=58)]),
          S("Everything below the lowest set bit is zero in both, and that bit is one in both. Everything above is opposite. An AND keeps just that bit.", [EQ(["1100 & 0100 = 0100", "→ 4"], ["w", "g"], size=60)]),
          S("So n and minus n isolates the lowest set bit.", [EQ(["n & −n"], ["g"], size=110)])],
         "n & −n", "n and minus n."),

    prob(142, "Microsoft", "SYSTEMS", "Detect Integer Overflow When Adding", "Check before you add",
         "Adding two integers can silently wrap around. How do you detect it without a bigger type?", "ADD WITHOUT\nOVERFLOW",
         "How do you check whether adding two signed thirty two bit integers will overflow, without using a larger type?",
         [H("a + b > 2,147,483,647 ?"), ROW(["a", "+", "b"], w=190, h=120, size=70, y=640), F("detect overflow before adding", "y", 0.7)],
         [S("Adding first and checking afterward is too late. On overflow the result wraps to a negative number, and in some languages it's undefined behaviour.", [EQ(["2,147,483,647 + 1 → −2,147,483,648"], ["r"], size=44)]),
          S("Check with subtraction instead. The sum overflows exactly when a is greater than the maximum minus b.", [EQ(["a > INT_MAX − b"], ["y"], size=70)]),
          S("For negative numbers, the same idea with the minimum. This never overflows itself.", [EQ(["a < INT_MIN − b"], ["c"], size=70)])],
         "a > MAX − b", "Compare against the maximum minus b."),

    prob(143, "Amazon", "ALGORITHMS", "Stock Profit With Many Trades", "Buy and sell as often as you like",
         "Same stock prices, but now you can trade as many times as you want. What's the profit?", "UNLIMITED\nTRADES",
         "Given daily prices seven, one, five, three, six, four, you may buy and sell as many times as you like, holding one share at a time. What's the maximum profit?",
         [H("7, 1, 5, 3, 6, 4"), BARS([7, 1, 5, 3, 6, 4], labels=["d1", "d2", "d3", "d4", "d5", "d6"], base=880, maxh=280, hl=[1, 2, 3, 4], fmt="{}"), F("maximum profit?", "y", 0.7)],
         [S("With unlimited trades, you don't need to find peaks and valleys by hand. Every rise is profit you can capture.", [EQ(["capture every upward step"], ["c"], size=58)]),
          S("Add up every positive day to day difference. One to five is four, three to six is three. The falls are skipped.", [EQ(["1 → 5: +4", "3 → 6: +3"], ["g", "g"], size=70)]),
          S("Total four plus three is seven. One pass, constant memory.", [EQ(["4 + 3 = 7"], ["g"], size=100)])],
         "7", "Seven."),

    prob(144, "Google", "ALGORITHMS", "Jump Game Greedy", "Can you reach the last index?",
         "Each number says how far you can jump. Can you reach the end?", "CAN YOU\nREACH THE END?",
         "Each element tells you the maximum jump length from that position. Starting at the first index of two, three, one, one, four, can you reach the last?",
         [H("2 3 1 1 4"), ROW([2, 3, 1, 1, 4], w=150, h=120, size=64, y=640), F("reach the last index?", "y", 0.7)],
         [S("Trying every jump length explores a huge tree. A greedy rule is enough.", [EQ(["track the farthest reachable index"], ["c"], size=52)]),
          S("From index zero, you can reach index two. From index one you can reach one plus three, four. The farthest reach is index four.", [EQ(["i=0: far = 2", "i=1: far = 4"], ["w", "g"], size=64)]),
          S("If you're ever standing beyond the farthest reach, you're stuck. Here you never are, and the last index is reachable.", [EQ(["far ≥ last index → yes"], ["g"], size=58)])],
         "YES", "Yes. One pass, linear time."),

    prob(145, "Meta", "ALGORITHMS", "Palindrome With Two Pointers", "Ignoring spaces and punctuation",
         "Is a man, a plan, a canal, Panama a palindrome? Check without building a new string.", "IS IT A\nPALINDROME?",
         "How do you check whether a phrase like a man, a plan, a canal, Panama is a palindrome, ignoring spaces and punctuation, in linear time and constant space?",
         [H("A man, a plan, a canal: Panama"), ROW(["a", "m", "a", "n", "...", "a", "m", "a"], w=100, h=100, size=54, y=640), F("palindrome?", "y", 0.7)],
         [S("Reversing a cleaned copy works, but allocates extra memory.", [EQ(["clean + reverse: O(n) memory"], ["r"], size=56)]),
          S("Use two pointers, one at each end. Skip anything that isn't a letter or digit.", [EQ(["left → ... ← right", "skip punctuation"], ["c", "y"], size=60)]),
          S("Compare the two letters, ignoring case. If they differ, it's not a palindrome. Otherwise move both inward.", [EQ(["a = a, m = m, a = a ..."], ["g"], size=60)]),
          S("They all match, so yes, it is a palindrome.", [EQ(["O(n) time", "O(1) memory"], ["g", "g"], size=70)])],
         "YES", "Yes, with two pointers."),

    prob(146, "Microsoft", "ALGORITHMS", "Rotate A Matrix 90 Degrees", "In place",
         "Rotate a square image ninety degrees in place, with two simple steps.", "ROTATE\nAN IMAGE",
         "How do you rotate an n by n matrix ninety degrees clockwise in place?",
         [H("rotate 90° clockwise"), GRID(3, 3, cell=110, text={"0,0": 1, "0,1": 2, "0,2": 3, "1,0": 4, "1,1": 5, "1,2": 6, "2,0": 7, "2,1": 8, "2,2": 9}, reveal=False, y=690), F("in place", "y", 0.7)],
         [S("A new matrix is easy, but uses n squared extra memory. There's a two step in place method.", [EQ(["new matrix: O(n²) memory"], ["r"], size=56)]),
          S("Step one: transpose. Swap each element across the main diagonal.", [GRID(3, 3, cell=110, text={"0,0": 1, "0,1": 4, "0,2": 7, "1,0": 2, "1,1": 5, "1,2": 8, "2,0": 3, "2,1": 6, "2,2": 9}, reveal=False, y=690)]),
          S("Step two: reverse every row. The matrix is rotated.", [GRID(3, 3, cell=110, text={"0,0": 7, "0,1": 4, "0,2": 1, "1,0": 8, "1,1": 5, "1,2": 2, "2,0": 9, "2,1": 6, "2,2": 3}, reveal=False, y=690, fill={"0,0": "g", "0,2": "g", "2,0": "g", "2,2": "g"}), F("transpose + reverse rows", "g", 0.7)])],
         "TRANSPOSE + REVERSE", "Transpose, then reverse each row."),

    prob(147, "Google", "ALGORITHMS", "Find A Peak Element", "Binary search without sorting",
         "An unsorted array, and you only need any peak. Find it in log n.", "FIND A PEAK",
         "Find any element that is greater than its neighbours in an array where adjacent elements differ, in logarithmic time.",
         [H("1 2 3 1"), ROW([1, 2, 3, 1], w=150, h=120, size=64, y=640, hl=[2]), F("find any peak in O(log n)", "y", 0.7)],
         [S("A linear scan works, but the array isn't sorted, so it seems binary search can't help. It can.", [EQ(["scan: O(n)"], ["r"], size=70)]),
          S("Look at the middle element and its right neighbour. If the right is bigger, a peak must exist on the right side.", [EQ(["a[mid] < a[mid+1] → go right"], ["c"], size=52)]),
          S("Otherwise a peak must exist on the left, including mid. Climbing uphill always ends at a peak.", [EQ(["a[mid] > a[mid+1] → go left"], ["y"], size=52)]),
          S("Halve the range each time. Logarithmic time.", [EQ(["O(log n)"], ["g"], size=110)])],
         "O(log n)", "Climb uphill with binary search."),

    prob(148, "Amazon", "ALGORITHMS", "Validate A Binary Search Tree", "Bounds, not just children",
         "A tree where every node looks fine locally, but isn't a valid search tree.", "IS THIS A\nVALID BST?",
         "How do you check that a binary tree is a valid binary search tree? Is it enough to compare each node with its children?",
         [H("5 → left 1, right 4 → 4's children 3, 6"), NODES(["5", "1", "4", "3", "6"], edges=[(0, 1), (0, 2), (2, 3), (2, 4)], xy=[(0.5, 0.1), (0.2, 0.5), (0.8, 0.5), (0.65, 0.85), (0.95, 0.85)], r=40, cols={4: "r"}), F("valid?", "y", 0.7)],
         [S("Comparing each node only with its direct children isn't enough. Four is less than five, which is fine locally.", [EQ(["5 → right child 4  (4 < 5!)"], ["r"], size=52)], stamp="WRONG"),
          S("The rule is that every node in the right subtree must be greater than the root. Six passes, but four doesn't.", [EQ(["right subtree of 5 must be > 5"], ["y"], size=52)]),
          S("Pass bounds down the tree. Each node must lie between a minimum and a maximum inherited from its ancestors.", [EQ(["check(node, low, high)", "left: high = node.val", "right: low = node.val"], ["c", "w", "w"], size=48)]),
          S("Here four violates the lower bound of five. Not a valid search tree.", [EQ(["4 ≤ 5 → invalid"], ["r"], size=80)])],
         "INVALID", "Pass down min and max bounds."),

    prob(149, "Google", "ALGORITHMS", "Find The Celebrity", "Everyone knows them, they know nobody",
         "At a party, one person is known by everyone and knows nobody. Find them with only n questions.", "FIND THE\nCELEBRITY",
         "At a party of n people, a celebrity is someone everyone knows and who knows no one. You can ask does A know B. How do you find the celebrity with about n questions?",
         [H("everyone knows the celebrity"), NODES(["A", "B", "C", "D"], edges=[(0, 2), (1, 2), (3, 2)], xy=[(0.15, 0.3), (0.15, 0.75), (0.55, 0.5), (0.9, 0.5)], r=44, cols={2: "y"}), F("find them with ~n questions", "y", 0.7)],
         [S("Asking every pair takes n squared questions. One question can eliminate someone though.", [EQ(["all pairs: n²"], ["r"], size=70)]),
          S("Ask whether A knows B. If yes, A is not the celebrity. If no, B is not the celebrity. Either way, one person is eliminated.", [EQ(["A knows B → A out", "A doesn't know B → B out"], ["c", "y"], size=54)]),
          S("Repeat with the remaining person. After n minus one questions, only one candidate is left.", [EQ(["n − 1 questions → 1 candidate"], ["g"], size=56)]),
          S("Verify the candidate with up to two n more questions. Linear total.", [EQ(["O(n) questions"], ["g"], size=90)])],
         "O(n)", "Linear number of questions."),

    prob(150, "Meta", "ALGORITHMS", "Subarray Sum Equals K", "Prefix sums and a hash map",
         "How many contiguous stretches add up to k? Do better than checking all of them.", "SUBARRAYS\nSUMMING TO K",
         "Given an array one, one, one and a target k equal to two, how many contiguous subarrays sum to k? How do you count them in linear time?",
         [H("array [1, 1, 1],  k = 2"), ROW([1, 1, 1], w=170, h=120, size=70, y=640), F("how many subarrays sum to 2?", "y", 0.7)],
         [S("Checking every start and end takes quadratic time.", [EQ(["all subarrays: O(n²)"], ["r"], size=64)]),
          S("Keep a running prefix sum. A subarray ending here sums to k if some earlier prefix equals the current prefix minus k.", [EQ(["prefix − k seen before?"], ["y"], size=58)]),
          S("Store how many times each prefix value has occurred in a hash map, starting with zero seen once.", [EQ(["prefixes: 0, 1, 2, 3", "need prefix − 2"], ["c", "w"], size=60)]),
          S("At prefix two, zero was seen. At prefix three, one was seen. That's two matches.", [EQ(["answer = 2"], ["g"], size=110)])],
         "2", "Two subarrays, in a single pass."),
]
