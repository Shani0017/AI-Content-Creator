"""Interview problems 151-175 (maths, combinatorics, number theory). Numbers verified below."""
import math
from fractions import Fraction as Fr
from iq_helpers import *

assert sum(k * k for k in range(1, 11)) == 385
assert sum(d for d in range(1, 28) if 28 % d == 0) == 28
assert (2 ** 10) % 11 == 1 and (3 * 5) % 7 == 1
assert pow(7, 100, 100) == 1
def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
assert is_prime(2 ** 31 - 1)
assert 2 ** 10 == 1024 and math.comb(10, 3) == 120 and math.comb(12, 2) == 66 and math.comb(10, 2) == 45
d4 = sum((-1) ** k * math.factorial(4) // math.factorial(k) for k in range(5))
assert d4 == 9
assert (12 - 2) * 180 == 1800
assert 1 + 3 + 3 + 1 == 8 and Fr(1, 2) + Fr(1, 4) + Fr(1, 8) + Fr(1, 16) == Fr(15, 16)
assert sum(Fr(1, k) for k in range(1, 5)) / 2 == Fr(25, 24)           # overhang of 4 books = H4/2 = 25/24
assert sum(Fr(1, k) for k in range(1, 5)) == Fr(25, 12)
assert max(a * b * c * d for a in range(1, 8) for b in range(1, 8) for c in range(1, 8) for d in range(1, 8) if a + b + c + d == 10) == 36
assert max(x * (10 - x) for x in range(0, 11)) == 25
assert all((n * (n + 1) * (n + 2)) % 6 == 0 for n in range(1, 200))
assert Fr(5, 36) == Fr(sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == 8), 36)
assert abs((1 + 1 / 1000000) ** 1000000 - math.e) < 1e-5
assert abs(math.log(2) / math.log(1.08) - 9.006) < 0.01
assert Fr(sum(a * b for a in range(1, 7) for b in range(1, 7)), 36) == Fr(49, 4)
assert sum(1 for a in range(0, 5) if True) == 5

PROBLEMS = [
    prob(151, "Harvard", "MATH", "Sum Of The First 10 Squares", "1 squared plus 2 squared and so on",
         "There's a formula that adds up squares instantly. Do you remember it?", "SUM OF\nSQUARES",
         "What is one squared plus two squared plus three squared, all the way up to ten squared, and what's the formula?",
         [H("1² + 2² + 3² + ... + 10²"), ROW([1, 4, 9, 16, 25, 36, 49, 64, 81, 100], w=84, h=96, size=44, y=640), F("total?", "y", 0.7)],
         [S("You can add them one at a time, but there's a closed form for any n.", [EQ(["Σ k² = n(n+1)(2n+1) / 6"], ["y"], size=50)]),
          S("For n equal to ten: ten times eleven times twenty one.", [EQ(["10 × 11 × 21 = 2310"], ["c"], size=70)]),
          S("Divide by six: three hundred eighty five.", [EQ(["2310 / 6 = 385"], ["g"], size=100)]),
          S("Check with a quick sum: one, five, fourteen, thirty, fifty five, and on up to three eighty five.", [ROW([1, 5, 14, 30, 55, 91, 140, 204, 285, 385], w=96, h=96, size=42, y=640, hl=[9])])],
         "385", "Three hundred eighty five."),

    prob(152, "Harvard", "NUMBER THEORY", "Is 28 A Perfect Number", "Divisors add up to itself",
         "Some numbers equal the sum of their own divisors. Is twenty eight one of them?", "PERFECT\nNUMBER?",
         "A perfect number equals the sum of its proper divisors, the divisors less than itself. Is twenty eight perfect?",
         [H("28"), ROW([1, 2, 4, 7, 14], w=140, h=110, size=60, y=640), F("do the divisors add to 28?", "y", 0.7)],
         [S("List the divisors of twenty eight smaller than itself: one, two, four, seven, fourteen.", [ROW([1, 2, 4, 7, 14], w=140, h=110, size=60, y=640, cols={0: "c", 1: "c", 2: "c", 3: "c", 4: "c"})]),
          S("Add them. One plus two is three, plus four is seven, plus seven is fourteen, plus fourteen is twenty eight.", [EQ(["1 + 2 + 4 + 7 + 14 = 28"], ["g"], size=70)]),
          S("So yes, it's perfect. The first perfect numbers are six, twenty eight, four ninety six, eight one twenty eight.", [ROW([6, 28, 496, 8128], w=200, h=120, size=64, y=640, hl=[1])])],
         "PERFECT", "Yes, twenty eight is perfect."),

    prob(153, "Harvard", "LOGIC", "Five Integers Two Differ By 4", "A pigeonhole argument",
         "Pick any five whole numbers. Two of them always differ by a multiple of four. Why?", "ANY 5\nINTEGERS",
         "Prove that among any five integers, two have a difference divisible by four.",
         [H("any 5 integers"), ROW(["a", "b", "c", "d", "e"], w=150, h=110, size=64, y=640), F("two differ by a multiple of 4?", "y", 0.7)],
         [S("Look at the remainders when you divide by four. There are only four possible remainders: zero, one, two, three.", [ROW(["rem 0", "rem 1", "rem 2", "rem 3"], w=210, h=120, size=44, y=640)]),
          S("Five numbers, four possible remainders. Two numbers must share a remainder.", [EQ(["5 pigeons, 4 holes"], ["c"], size=70)]),
          S("Two numbers with the same remainder differ by a multiple of four.", [EQ(["a = 4p + r,  b = 4q + r", "a − b = 4(p − q)"], ["w", "g"], size=60)])],
         "PIGEONHOLE", "Five numbers, four remainders: two must match."),

    prob(154, "Top Tech", "LOGIC", "Seven Bridges Of Konigsberg", "Can you cross each bridge once?",
         "A famous city puzzle that started graph theory. Seven bridges, can you cross each exactly once?", "SEVEN\nBRIDGES",
         "A city has four land areas connected by seven bridges. Can you take a walk that crosses every bridge exactly once?",
         [H("4 lands, 7 bridges"), NODES(["A", "B", "C", "D"], edges=[(0, 1), (0, 1), (0, 2), (0, 2), (0, 3), (1, 3), (2, 3)], xy=[(0.5, 0.15), (0.15, 0.55), (0.85, 0.55), (0.5, 0.9)], r=44), F("each bridge exactly once?", "y", 0.7)],
         [S("Turn it into a graph. Each land mass is a node, and each bridge is an edge.", [EQ(["lands = nodes", "bridges = edges"], ["c", "y"], size=64)]),
          S("In such a walk, every node you pass through uses two edges, one in and one out. Only the start and end can have an odd number.", [EQ(["odd-degree nodes allowed: 0 or 2"], ["y"], size=54)]),
          S("Count the bridges at each land: five, three, three, three. All four are odd.", [ROW([5, 3, 3, 3], w=150, h=110, size=64, y=640, cols={0: "r", 1: "r", 2: "r", 3: "r"})]),
          S("Four odd nodes is too many. So it's impossible.", [EQ(["4 odd nodes > 2", "→ impossible"], ["r", "r"], size=70)])],
         "IMPOSSIBLE", "Impossible. Euler proved it in 1736."),

    prob(155, "Top Tech", "GEOMETRY", "Angles Of A 12 Sided Polygon", "Interior angle sum",
         "What do the interior angles of a twelve sided polygon add up to?", "12-SIDED\nPOLYGON",
         "What is the sum of the interior angles of a twelve sided polygon?",
         [H("a dodecagon"), ROW(["n = 12"], cols={0: "y"}, w=300, h=130, size=72, y=640), F("sum of interior angles?", "y", 0.7)],
         [S("A triangle has one hundred eighty degrees. A quadrilateral splits into two triangles, so three sixty.", [ROW(["3 sides: 180°", "4 sides: 360°", "5 sides: 540°"], w=290, h=110, size=38, y=640)]),
          S("From one corner, draw diagonals. An n sided polygon splits into n minus two triangles.", [EQ(["triangles = n − 2"], ["c"], size=70)]),
          S("For twelve sides, ten triangles, each one hundred eighty degrees.", [EQ(["10 × 180° = 1800°"], ["g"], size=90)])],
         "1800°", "One thousand eight hundred degrees."),

    prob(156, "Quant", "PROBABILITY", "Sum Of Two Dice Equals 8", "How likely is an 8?",
         "Two dice. What are the chances they add to eight?", "TWO DICE\nSUM OF 8",
         "You roll two fair dice. What's the probability that the sum is eight?",
         [H("two dice, sum = 8"), ROW([2, 6, 3, 5, 4, 4], per=6, w=110, h=110, size=54, y=640), F("probability?", "y", 0.7)],
         [S("There are thirty six equally likely outcomes, six times six.", [EQ(["6 × 6 = 36 outcomes"], ["c"], size=70)]),
          S("List the ways to make eight: two and six, three and five, four and four, five and three, six and two.", [ROW(["2+6", "3+5", "4+4", "5+3", "6+2"], w=170, h=110, size=50, y=640, cols={0: "g", 1: "g", 2: "g", 3: "g", 4: "g"})]),
          S("Five outcomes out of thirty six.", [EQ(["5 / 36 ≈ 13.9%"], ["g"], size=88)])],
         "5/36", "Five thirty sixths, about fourteen percent."),

    prob(157, "Quant", "MATH", "Rule Of 72 Doubling Time", "How long to double at 8 percent?",
         "A mental shortcut that bankers use. How long to double your money at eight percent?", "RULE OF 72",
         "At eight percent annual interest, roughly how many years does it take for money to double, and how can you estimate it in your head?",
         [H("8% per year"), ROW(["$1,000", "→ $2,000"], cols={0: "c", 1: "g"}, w=300, h=120, size=54, y=640), F("how many years?", "y", 0.7)],
         [S("The exact answer comes from logarithms: log of two over log of one point oh eight.", [EQ(["t = ln 2 / ln 1.08"], ["y"], size=64)]),
          S("That's about nine years, nine point oh oh six. You'd not do that in your head.", [EQ(["t ≈ 9.006 years"], ["g"], size=70)]),
          S("The shortcut: divide seventy two by the interest rate. Seventy two over eight.", [EQ(["72 / 8 = 9 years"], ["g"], size=80)]),
          S("It works because ln two is point six nine three, and seventy two has lots of divisors.", [EQ(["100 × ln 2 ≈ 69.3 ≈ 72"], ["c"], size=54)])],
         "9 YEARS", "About nine years."),

    prob(158, "Harvard", "MATH", "Half Plus A Quarter Plus An Eighth", "Zeno's paradox adds up",
         "Walk half the distance, then half the remainder, forever. Do you ever arrive?", "ZENO'S\nPARADOX",
         "You walk half the distance to a wall, then half of what remains, then half again, forever. Do you ever reach the wall, and what do the distances add up to?",
         [H("1/2 + 1/4 + 1/8 + ..."), ROW(["1/2", "1/4", "1/8", "1/16", "..."], w=170, h=110, size=50, y=640), F("what's the total?", "y", 0.7)],
         [S("Each step covers half of what's left. After n steps, what remains is one over two to the n.", [EQ(["left after n steps: 1 / 2^n"], ["c"], size=58)]),
          S("After four steps, you've covered fifteen sixteenths. The gap is one sixteenth.", [BARS([50, 75, 87, 94], labels=["1", "2", "3", "4"], base=880, maxh=300, fmt="{}%")]),
          S("The gap shrinks toward zero. So the total distance gets closer and closer to one, the whole distance.", [EQ(["1/2 + 1/4 + 1/8 + ... = 1"], ["g"], size=64)]),
          S("Infinitely many steps, but a finite total. You do arrive.", [EQ(["Σ 1/2^k = 1"], ["g"], size=80)])],
         "1", "The distances add to exactly one."),

    prob(159, "Harvard", "MATH", "Stacking Books For Overhang", "How far can they stick out?",
         "Stack books on a table edge. How far can the top stick out past the edge?", "BOOK OVERHANG",
         "You stack identical books on a table, each book one unit long. With four books, how far past the table edge can the top book reach?",
         [H("4 books, each 1 long"), ROW(["book 1", "book 2", "book 3", "book 4"], w=210, h=110, size=40, y=640), F("maximum overhang?", "y", 0.7)],
         [S("Balance from the top down. The top book can overhang its support by one half.", [EQ(["top book: 1/2"], ["c"], size=70)]),
          S("The next book down can shift the pair by one quarter, then one sixth, then one eighth.", [EQ(["1/2 + 1/4 + 1/6 + 1/8"], ["y"], size=60)]),
          S("In general the overhang is half the harmonic series. For four books that's twenty five over twenty four.", [EQ(["(1/2)(1 + 1/2 + 1/3 + 1/4)", "= 25/24 ≈ 1.04"], ["w", "g"], size=58)]),
          S("More than a whole book length, with only four books. And with enough books you can reach any distance.", [EQ(["harmonic series diverges"], ["g"], size=60)])],
         "25/24", "Twenty five over twenty four, more than one book length."),

    prob(160, "Harvard", "NUMBER THEORY", "Fermat's Little Theorem Check", "2 to the 10 mod 11",
         "What's the remainder when two to the tenth is divided by eleven? There's a theorem for this.", "2^10\nMOD 11",
         "What is the remainder of two to the power ten when divided by eleven?",
         [H("2^10 mod 11"), ROW(["2^10 = 1024"], cols={0: "y"}, w=500, h=120, size=60, y=640), F("remainder?", "y", 0.7)],
         [S("You could compute one thousand twenty four and divide, which works here, but not for huge exponents.", [EQ(["1024 = 93 × 11 + 1"], ["w"], size=64)]),
          S("Fermat's little theorem: for a prime p and a not divisible by p, a to the p minus one is one mod p.", [EQ(["a^(p−1) ≡ 1 (mod p)"], ["y"], size=60)]),
          S("Here p is eleven and a is two, so two to the ten is one mod eleven. No arithmetic needed.", [EQ(["2^10 ≡ 1 (mod 11)"], ["g"], size=70)])],
         "1", "The remainder is one."),

    prob(161, "Harvard", "NUMBER THEORY", "Modular Inverse Of 3 Mod 7", "What times 3 leaves 1?",
         "In arithmetic mod seven, what number undoes multiplying by three?", "INVERSE OF 3\nMOD 7",
         "Find a number x such that three times x leaves remainder one when divided by seven.",
         [H("3 × x ≡ 1 (mod 7)"), ROW([1, 2, 3, 4, 5, 6], w=120, h=110, size=60, y=640), F("which x?", "y", 0.7)],
         [S("Try the possible values. Three times one is three, three times two is six, three times three is nine, which is two mod seven.", [EQ(["3×1=3", "3×2=6", "3×3=9 → 2"], ["w", "w", "w"], size=60)]),
          S("Keep going. Three times four is twelve, which is five mod seven. Three times five is fifteen, which is one.", [EQ(["3×4=12 → 5", "3×5=15 → 1 ✓"], ["w", "g"], size=64)]),
          S("So x is five. Inverses like this are the heart of modular division and cryptography.", [EQ(["5 is the inverse of 3 mod 7"], ["g"], size=58)])],
         "5", "The inverse is five."),

    prob(162, "Harvard", "NUMBER THEORY", "Last Two Digits Of 7 To The 100", "Cycle of 4 modulo 100",
         "What are the last two digits of seven to the power one hundred?", "LAST TWO\nDIGITS",
         "What are the last two digits of seven to the power one hundred?",
         [H("7^100"), ROW(["7^1", "7^2", "7^3", "7^4"], w=200, h=110, size=50, y=640), F("last two digits?", "y", 0.7)],
         [S("Work modulo one hundred. Seven to the first is seven, seven squared is forty nine.", [EQ(["7^1 = 07", "7^2 = 49"], ["w", "w"], size=64)]),
          S("Seven cubed is three forty three, so forty three. Seven to the fourth is two thousand four hundred one, so oh one.", [EQ(["7^3 = 343 → 43", "7^4 = 2401 → 01"], ["w", "g"], size=60)]),
          S("Seven to the fourth is one mod one hundred. One hundred is a multiple of four, so seven to the hundredth is one.", [EQ(["7^100 = (7^4)^25 ≡ 1"], ["g"], size=58)])],
         "01", "The last two digits are zero one."),

    prob(163, "Harvard", "NUMBER THEORY", "Is 2 To The 31 Minus 1 Prime", "A Mersenne prime",
         "A number with ten digits that you can't check by hand. Is it prime?", "IS 2147483647\nPRIME?",
         "Is two to the thirty first minus one, which is two billion one hundred forty seven million four hundred eighty three thousand six hundred forty seven, a prime number?",
         [H("2^31 − 1"), ROW(["2,147,483,647"], cols={0: "y"}, w=700, h=130, size=60, y=640), F("prime?", "y", 0.7)],
         [S("Trial division needs primes up to its square root, about forty six thousand. That's a few thousand checks, fine for a computer.", [EQ(["√2,147,483,647 ≈ 46,341"], ["c"], size=58)]),
          S("Numbers of the form two to the p minus one are called Mersenne numbers. When p is prime, they're often prime.", [EQ(["M_p = 2^p − 1"], ["y"], size=62)]),
          S("Thirty one is prime, and Euler proved in 1772 that this one is prime too. It's also the largest signed thirty two bit integer.", [EQ(["2^31 − 1 is prime"], ["g"], size=70)])],
         "PRIME", "Yes, it's a Mersenne prime."),

    prob(164, "Top Tech", "COUNTING", "Subsets Of A 10 Element Set", "How many different subsets?",
         "A set with ten elements. How many subsets does it have, counting the empty one?", "SUBSETS OF\n10 ELEMENTS",
         "How many subsets, including the empty set, does a set with ten elements have?",
         [H("a set of 10 elements"), ROW(list("ABCDEFGHIJ"), per=10, w=84, h=90, size=44, y=640), F("how many subsets?", "y", 0.7)],
         [S("For each element you make a choice: it's in the subset, or it's out.", [EQ(["in  /  out"], ["c"], size=90)]),
          S("Ten elements, two choices each, and the choices are independent.", [EQ(["2 × 2 × 2 × ... × 2  (10 times)"], ["y"], size=54)]),
          S("That's two to the tenth.", [EQ(["2^10 = 1024"], ["g"], size=100)])],
         "1024", "One thousand twenty four."),

    prob(165, "Top Tech", "COUNTING", "Committee Of 3 From 10", "Order doesn't matter",
         "Choose a committee of three from ten people. How many different committees?", "COMMITTEE\nOF 3",
         "In how many ways can you choose a committee of three people from ten, if order doesn't matter?",
         [H("choose 3 of 10"), ROW(list("ABCDEFGHIJ"), per=10, w=84, h=90, size=44, y=640, hl=[0, 4, 7]), F("how many committees?", "y", 0.7)],
         [S("If order mattered, there would be ten times nine times eight, seven hundred twenty.", [EQ(["10 × 9 × 8 = 720"], ["w"], size=80)]),
          S("But a committee of A, B, C is the same as B, C, A. Each committee is counted six times, the number of orderings of three.", [EQ(["3! = 6 orderings"], ["r"], size=70)]),
          S("Divide: seven hundred twenty over six.", [EQ(["720 / 6 = 120"], ["g"], size=100)])],
         "120", "One hundred twenty."),

    prob(166, "Top Tech", "COUNTING", "Derangements Of Four Letters", "Nobody in their own envelope",
         "Four letters, four envelopes, every letter in the wrong one. How many ways?", "ALL WRONG\nENVELOPES",
         "Four letters are put into four addressed envelopes, one each. In how many ways is every letter in the wrong envelope?",
         [H("4 letters, 4 envelopes"), ROW(["A", "B", "C", "D"], w=150, h=120, size=70, y=640), F("none in its own envelope?", "y", 0.7)],
         [S("There are four factorial, twenty four, ways to place the letters at all.", [EQ(["4! = 24"], ["c"], size=90)]),
          S("Use inclusion exclusion. Subtract those with at least one correct, add back those with at least two, and so on.", [EQ(["24 − 24 + 12 − 4 + 1"], ["y"], size=60)]),
          S("Twenty four minus twenty four plus twelve minus four plus one.", [EQ(["= 9"], ["g"], size=110)])],
         "9", "Nine ways."),

    prob(167, "Top Tech", "COUNTING", "Sharing 10 Candies Among 3 Kids", "Stars and bars",
         "Ten identical candies, three kids. How many ways to share them?", "10 CANDIES\n3 KIDS",
         "In how many ways can you give ten identical candies to three children, if a child can get none?",
         [H("10 identical candies"), ROW(["kid 1", "kid 2", "kid 3"], w=240, h=120, size=48, y=640), F("how many ways?", "y", 0.7)],
         [S("Line the ten candies up and place two dividers among them to separate the three kids.", [ROW(["★", "★", "★", "|", "★", "★", "|", "★", "★", "★", "★", "★"], per=12, w=70, h=90, size=46, y=640, hl=[3, 6])]),
          S("Twelve positions in total, ten candies and two dividers. You choose where the two dividers go.", [EQ(["C(12, 2)"], ["y"], size=90)]),
          S("Twelve times eleven over two is sixty six.", [EQ(["12 × 11 / 2 = 66"], ["g"], size=88)])],
         "66", "Sixty six ways."),

    prob(168, "Harvard", "MATH", "Coefficient In The Binomial Expansion", "x squared in (1+x)^10",
         "Expand one plus x to the tenth. What multiplies x squared?", "(1+x)^10",
         "In the expansion of one plus x, to the power ten, what's the coefficient of x squared?",
         [H("(1 + x)^10"), ROW(["1", "+", "10x", "+", "?·x²", "+ ..."], w=150, h=110, size=48, y=640, hl=[4]), F("coefficient of x²?", "y", 0.7)],
         [S("Expanding by hand means multiplying ten brackets. Instead, count how x squared appears.", [EQ(["pick x from 2 of the 10 brackets"], ["c"], size=52)]),
          S("You choose which two of the ten brackets contribute an x. The rest contribute one.", [EQ(["C(10, 2)"], ["y"], size=90)]),
          S("Ten times nine over two is forty five.", [EQ(["10 × 9 / 2 = 45"], ["g"], size=88)])],
         "45", "Forty five."),

    prob(169, "Top Tech", "GEOMETRY", "Cake Cut With 3 Planes", "Maximum pieces of a cake",
         "Cut a cake with three straight cuts. What's the most pieces you can get?", "CAKE\n3 CUTS",
         "What is the maximum number of pieces you can get from a cake, a solid, using three straight planar cuts?",
         [H("3 plane cuts"), ROW(["1 cut: 2", "2 cuts: 4", "3 cuts: ?"], w=290, h=110, size=38, y=640), F("most pieces?", "y", 0.7)],
         [S("Each new cut can cross all earlier cuts, and each crossing line splits regions of the new cut.", [EQ(["cut k adds the regions of a plane cut by k−1 lines"], ["c"], size=44)]),
          S("One cut gives two pieces, two cuts give four. The third plane is cut by two lines into four regions.", [EQ(["2, 4, 8"], ["y"], size=90)]),
          S("Four new pieces: four plus four is eight.", [EQ(["4 + 4 = 8"], ["g"], size=100)]),
          S("The pattern for 3D is one, two, four, eight, fifteen, twenty six.", [ROW([1, 2, 4, 8, 15, 26], w=130, h=110, size=54, y=640, hl=[3])])],
         "8 PIECES", "Eight pieces."),

    prob(170, "Quant", "GEOMETRY", "Estimate Pi By Throwing Darts", "Monte Carlo",
         "Throw darts at a square board with a circle inside. You can estimate pi from the counts.", "PI FROM\nDARTS",
         "How can you estimate pi by throwing random darts at a square board with a quarter circle inscribed in it?",
         [H("unit square, quarter circle"), PIE([0.785], cols=["c"], r=170, y=680), F("how do the counts give pi?", "y", 0.7)],
         [S("Throw darts uniformly at the unit square. Each lands inside the quarter circle if x squared plus y squared is at most one.", [EQ(["x² + y² ≤ 1  → inside"], ["c"], size=58)]),
          S("The quarter circle has area pi over four. The square has area one. So the fraction inside is pi over four.", [EQ(["P(inside) = π / 4"], ["y"], size=64)]),
          S("Multiply the fraction of darts inside by four. With a million darts you get pi to about three digits.", [EQ(["π ≈ 4 × inside / total"], ["g"], size=60)])],
         "π ≈ 4 × FRACTION", "Four times the fraction of darts inside."),

    prob(171, "Quant", "PROBABILITY", "Expected Product Of Two Dice", "Independence at work",
         "Roll two dice and multiply them. What's the average product?", "PRODUCT OF\nTWO DICE",
         "You roll two fair dice and multiply the results. What's the expected value of the product?",
         [H("a × b"), ROW([3, "×", 5, "= 15"], w=150, h=120, size=64, y=640), F("expected product?", "y", 0.7)],
         [S("Listing all thirty six products and averaging works but is long.", [EQ(["36 products to add"], ["r"], size=64)]),
          S("The two dice are independent, so the expected value of the product is the product of the expected values.", [EQ(["E[ab] = E[a] · E[b]"], ["y"], size=60)]),
          S("Each die averages three and a half.", [EQ(["3.5 × 3.5 = 12.25"], ["g"], size=88)])],
         "12.25", "Twelve and a quarter."),

    prob(172, "Quant", "PROBABILITY", "Compound Interest And e", "Compounding continuously",
         "You invest one dollar at one hundred percent interest. How does the number e appear?", "THE NUMBER e\nIN YOUR BANK",
         "You invest one dollar at one hundred percent annual interest, compounded n times a year. As n grows without limit, what does your balance approach after one year?",
         [H("$1 at 100% per year"), ROW(["n = 1", "n = 12", "n = 365"], w=250, h=120, size=48, y=640), F("what's the limit?", "y", 0.7)],
         [S("Compounding once gives two dollars. Compounding monthly gives a bit more.", [ROW(["n=1: $2.00", "n=12: $2.613", "n=365: $2.715"], w=290, h=110, size=36, y=640)]),
          S("Each time you compound, you earn interest on interest, but with smaller steps. The growth slows down.", [EQ(["(1 + 1/n)^n"], ["y"], size=88)]),
          S("As n goes to infinity, the amount settles at e, about two point seven one eight.", [EQ(["lim (1 + 1/n)^n = e ≈ 2.718"], ["g"], size=58)])],
         "e ≈ 2.718", "Two dollars and seventy two cents."),

    prob(173, "Top Tech", "MATH", "Largest Product With Sum 10", "Split 10 to maximise the product",
         "Split the number ten into positive whole numbers. Which split has the biggest product?", "SPLIT 10\nMAX PRODUCT",
         "You split ten into positive whole numbers that add up to ten. What's the largest possible product of the parts?",
         [H("a + b + c + ... = 10"), ROW([5, 5, "→ 25"], w=170, h=120, size=64, y=640), F("max product?", "y", 0.7)],
         [S("Two parts: five and five gives twenty five. But more parts can do better.", [EQ(["5 × 5 = 25"], ["w"], size=80)]),
          S("Three parts: three, three, four gives thirty six. Four parts: two, two, three, three gives thirty six.", [EQ(["3 × 3 × 4 = 36", "2 × 2 × 3 × 3 = 36"], ["g", "g"], size=60)]),
          S("The best parts are threes, with twos where needed, because a four is no better than two twos.", [EQ(["use as many 3s as possible"], ["c"], size=58)]),
          S("Ten is three, three, two, two. The product is thirty six.", [EQ(["3 · 3 · 2 · 2 = 36"], ["g"], size=88)])],
         "36", "Thirty six."),

    prob(174, "Top Tech", "MATH", "Rectangle With Perimeter 20", "Maximum area",
         "A rectangle with a fixed perimeter of twenty. Which shape has the biggest area?", "MAX AREA\nPERIMETER 20",
         "Among all rectangles with perimeter twenty, which has the largest area, and what is it?",
         [H("perimeter = 20"), BARS([9, 16, 21, 24, 25], labels=["1×9", "2×8", "3×7", "4×6", "5×5"], base=880, maxh=300, hl=[4], fmt="{}"), F("largest area?", "y", 0.7)],
         [S("The two side lengths add up to ten. Call them x and ten minus x.", [EQ(["area = x(10 − x)"], ["y"], size=70)]),
          S("Try values. One by nine is nine, two by eight is sixteen, three by seven is twenty one, four by six is twenty four.", [BARS([9, 16, 21, 24, 25], labels=["1×9", "2×8", "3×7", "4×6", "5×5"], base=880, maxh=300, hl=[4], fmt="{}")]),
          S("The area peaks when both sides are equal: a five by five square, twenty five.", [EQ(["x = 5 → 25"], ["g"], size=100)])],
         "25", "A five by five square, area twenty five."),

    prob(175, "Harvard", "NUMBER THEORY", "Three Consecutive Integers And 6", "Always divisible by six",
         "Multiply any three whole numbers in a row. The result is always a multiple of six. Why?", "3 IN A ROW",
         "Prove that the product of any three consecutive integers is divisible by six.",
         [H("n · (n+1) · (n+2)"), ROW([4, 5, 6, "= 120"], w=150, h=120, size=64, y=640), F("divisible by 6, always?", "y", 0.7)],
         [S("Six is two times three, and they share no factor. So you need the product divisible by two and by three.", [EQ(["6 = 2 × 3"], ["c"], size=90)]),
          S("Among any two consecutive integers, one is even. So the product is divisible by two.", [EQ(["n or n+1 is even"], ["y"], size=64)]),
          S("Among any three consecutive integers, exactly one is a multiple of three.", [EQ(["one of n, n+1, n+2 is ÷ 3"], ["y"], size=58)]),
          S("Both conditions hold, so six divides the product. Four, five, six gives a hundred twenty.", [EQ(["120 = 6 × 20"], ["g"], size=80)])],
         "ALWAYS", "Always, because one is even and one is a multiple of three."),
]
