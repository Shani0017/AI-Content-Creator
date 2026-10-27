"""Interview problems 101-125. Every number verified below."""
import math, itertools
from fractions import Fraction as Fr
from iq_helpers import *

# ---- verification ----
assert abs(6 * (1 / 6) * (5 / 6) ** 5 - 0.4019) < 1e-3
assert abs(13 * sum(1 / k for k in range(1, 14)) - 41.3) < 0.1
assert 4 * math.comb(13, 5) == 5148 and abs(5148 / math.comb(52, 5) - 0.00198) < 1e-5
assert Fr(4, 52) * Fr(3, 51) == Fr(1, 221)
def _p3(n, days=365):                      # P(some birthday shared by 3 people) by exact DP-free Monte Carlo-free formula via inclusion not needed: simulate exactly with small recursion
    from math import comb
    # probability that no day has >= 3 people: sum over k pairs: number of ways with k days holding 2 people each and n-2k days holding 1
    tot = 0
    for k in range(0, n // 2 + 1):
        ones = n - 2 * k
        if ones + k > days:
            continue
        ways = math.comb(days, k) * math.comb(days - k, ones) * math.factorial(n) // (2 ** k)
        tot += ways
    return 1 - tot / days ** n
assert _p3(87) < 0.5 < _p3(88)
assert 144 == sum(1 for m in range(1024) if "11" not in format(m, "010b")) and abs(144 / 1024 - 0.1406) < 1e-3
assert 10 * 11 // 2 + 1 == 56
assert sum(1 for n in range(1, 101) if n % 3 == 0 or n % 5 == 0) == 47
assert sum(1 for n in range(1, 1001) if n % 3 == 0 or n % 5 == 0 or n % 7 == 0) == 543
assert Fr(sum(max(a, b, c) for a in range(1, 7) for b in range(1, 7) for c in range(1, 7)), 216) == Fr(1071, 216)
assert 8 * 8 - 1 == 63 and 10 * 7 // 2 == 35
assert sum(1000 // 5 ** k for k in range(1, 5)) == 249
assert math.lcm(*range(1, 11)) == 2520
assert math.factorial(11) // (math.factorial(4) * math.factorial(4) * math.factorial(2)) == 34650
assert math.factorial(5) == 120 and sum(2 * k + 1 for k in range(50)) == 2500
assert sum(int(c) for c in "1234567890") == 45
assert [24, 12, 8, 6] == [math.prod([1, 2, 3, 4]) // x for x in [1, 2, 3, 4]]


def merge(iv):
    iv = sorted(iv)
    out = [list(iv[0])]
    for a, b in iv[1:]:
        if a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]


def longest(s):
    best = start = 0
    seen = {}
    for i, ch in enumerate(s):
        if ch in seen and seen[ch] >= start:
            start = seen[ch] + 1
        seen[ch] = i
        best = max(best, i - start + 1)
    return best


assert longest("abcabcbb") == 3

PROBLEMS = [
    prob(101, "Quant", "PROBABILITY", "Exactly One Six In Six Dice", "Roll six dice: how likely is exactly one 6?",
         "Roll six dice. Most people think you almost always get a six. Do you?", "SIX DICE\nONE SIX?",
         "You roll six fair dice. What's the probability that exactly one of them shows a six?",
         [H("6 dice, exactly one 6"), ROW([3, 6, 1, 4, 2, 5], w=130, h=110, size=60, y=640, hl=[1]), F("probability of exactly one six?", "y", 0.7)],
         [S("Many say it's certain, since six dice and a one in six chance each gives one six on average. That's the average, not the exact chance.", [BIG("100% ?", "r", size=120)], stamp="WRONG"),
          S("Pick which die is the six. There are six choices, and each has probability one sixth.", [EQ(["choose the die: 6 ways", "it shows 6: 1/6"], ["c", "y"], size=58)]),
          S("The other five must not be sixes. Each is five sixths, so five sixths to the fifth power.", [EQ(["(5/6)^5 = 0.402"], ["y"], size=70)]),
          S("Multiply: six times one sixth times point four oh two. That's about forty percent.", [EQ(["6 × 1/6 × (5/6)^5", "≈ 40.2%"], ["w", "g"], size=64)])],
         "40%", "About forty percent."),

    prob(102, "Quant", "PROBABILITY", "Collect All 13 Card Ranks", "Draw with replacement from a deck",
         "Draw a card, put it back, repeat. How long until you've seen every rank from ace to king?", "ALL 13 RANKS",
         "You draw a card from a deck, note its rank, and put it back, then repeat. On average, how many draws until you've seen all thirteen ranks?",
         [H("13 ranks, draw and replace"), ROW(["A", "2", "3", "...", "K"], w=130, h=100, size=54, y=640), F("expected number of draws?", "y", 0.7)],
         [S("This is the coupon collector problem with thirteen coupons. The first rank is free, and each new one takes longer.", [EQ(["13 coupons"], ["c"], size=80)]),
          S("With k ranks still missing, a draw is new with probability k over thirteen, so you wait thirteen over k draws.", [EQ(["13 missing: 13/13 = 1", "12 missing: 13/12 = 1.08", "1 missing: 13/1 = 13"], ["w", "w", "r"], size=48)]),
          S("Add up thirteen over k for k from one to thirteen. That's thirteen times the harmonic number H thirteen.", [EQ(["13 × (1 + 1/2 + ... + 1/13)", "= 13 × 3.18"], ["w", "g"], size=54)]),
          S("That's about forty one point three draws.", [EQ(["≈ 41.3 draws"], ["g"], size=88)])],
         "41.3 DRAWS", "About forty one draws."),

    prob(103, "Quant", "PROBABILITY", "Poker Flush Probability", "Five cards, all one suit",
         "Five cards from a deck. What are the odds they're all the same suit?", "ALL THE\nSAME SUIT",
         "You are dealt five cards from a standard fifty two card deck. What's the probability that all five are the same suit?",
         [H("5 cards, one suit"), ROW(["♠", "♠", "♠", "♠", "♠"], w=130, h=110, size=60, y=640), F("probability of a flush?", "y", 0.7)],
         [S("Count the favourable hands first. Pick the suit, four ways. Then pick five of its thirteen cards.", [EQ(["4 suits", "C(13, 5) = 1,287 per suit"], ["c", "y"], size=58)]),
          S("That's four times one thousand two hundred eighty seven, five thousand one hundred forty eight hands.", [EQ(["4 × 1,287 = 5,148"], ["g"], size=80)]),
          S("All possible five card hands: fifty two choose five, two million five hundred ninety eight thousand nine hundred sixty.", [EQ(["C(52, 5) = 2,598,960"], ["y"], size=70)]),
          S("Divide: five thousand one hundred forty eight over two point six million. About point two percent, one in five hundred.", [EQ(["5,148 / 2,598,960", "≈ 0.2%  (1 in 505)"], ["w", "g"], size=60)])],
         "0.2%", "About two tenths of a percent."),

    prob(104, "Quant", "PROBABILITY", "Two Aces In A Row", "Draw two cards, both aces",
         "Draw two cards. Both aces. Rarer than you think.", "TWO ACES\nIN A ROW",
         "You draw two cards from a shuffled fifty two card deck without replacement. What's the probability that both are aces?",
         [H("two cards, no replacement"), ROW(["A", "A"], cols={0: "y", 1: "y"}, w=200, h=130, size=72, y=640), F("probability both are aces?", "y", 0.7)],
         [S("Four aces in fifty two cards. The first card is an ace with probability four over fifty two.", [EQ(["P(first ace) = 4/52"], ["c"], size=70)]),
          S("Given that, three aces remain in fifty one cards.", [EQ(["P(second ace | first) = 3/51"], ["y"], size=64)]),
          S("Multiply the two. Twelve over two thousand six hundred fifty two simplifies to one over two hundred twenty one.", [EQ(["4/52 × 3/51 = 12 / 2652", "= 1 / 221"], ["w", "g"], size=64)])],
         "1/221", "About one in two hundred twenty one."),

    prob(105, "Quant", "PROBABILITY", "Monty Hall With 100 Doors", "The host opens 98 doors",
         "Monty Hall, but with a hundred doors. Now does switching matter?", "MONTY HALL\nWITH 100 DOORS",
         "There are one hundred doors and one car. You pick door one. The host, who knows where the car is, opens ninety eight other doors, all goats, leaving your door and one other. Do you switch?",
         [H("100 doors, 1 car"), ROW(["your door", "98 goats opened", "the last door"], cols={0: "c", 1: "d", 2: "y"}, w=290, h=120, size=34, y=640), F("stay or switch?", "y", 0.7)],
         [S("Your first pick was right with probability one in one hundred. That never changes.", [BARS([1, 99], labels=["your door", "everything else"], cols={0: "c", 1: "g"}, fmt="{}%", base=880, maxh=300)]),
          S("The host opens every other door but one, always avoiding the car. So the ninety nine percent slides onto the one remaining door.", [EQ(["stay: 1 in 100", "switch: 99 in 100"], ["r", "g"], size=70)]),
          S("With three doors it's two thirds. With a hundred it's ninety nine percent. Always switch.", [EQ(["n doors: switch wins (n−1)/n"], ["g"], size=58)])],
         "SWITCH: 99%", "Switch. You win ninety nine percent of the time."),

    prob(106, "Quant", "PROBABILITY", "Three People Share A Birthday", "How many people for a triple?",
         "The birthday paradox with a twist: not two people, but three on the same day.", "TRIPLE\nBIRTHDAY",
         "How many people do you need in a room before there's a better than fifty percent chance that at least three of them share the same birthday?",
         [H("3 people, same birthday"), ROW([23, 50, 88, 183], w=170, h=120, size=60, y=640), F("how many for 50%?", "y", 0.7)],
         [S("For two people sharing, twenty three is enough. For three, you need many more, since a triple is much rarer than a pair.", [EQ(["pair: 23 people", "triple: ?"], ["g", "y"], size=64)]),
          S("Count the ways nobody shares three: some days hold two people, the rest hold one. That sum is messy but exact.", [EQ(["no day has 3 or more"], ["c"], size=60)]),
          S("Computing it exactly, the chance of a triple is forty nine point four percent with eighty seven people, and fifty one point one percent with eighty eight.", [BARS([42, 49, 51, 58], labels=["84", "87", "88", "90"], hl=[2], fmt="{}%", base=890, maxh=300)])],
         "88 PEOPLE", "Eighty eight people."),

    prob(107, "Top Tech", "COUNTING", "Binary Strings Without Two 1s", "Length 10, no two adjacent ones",
         "How many ten digit binary strings never have two ones in a row?", "NO TWO 1s\nIN A ROW",
         "How many binary strings of length ten have no two consecutive ones?",
         [H("length 10, no \"11\""), ROW([1, 0, 1, 0, 0, 1, 0, 1, 0, 0], w=84, h=96, size=50, y=640, hl=[0, 2, 5, 7]), F("how many such strings?", "y", 0.7)],
         [S("Listing all one thousand twenty four strings is hopeless. Count with a recurrence instead.", [EQ(["2^10 = 1024 strings"], ["r"], size=64)]),
          S("Look at the last digit. If it's zero, the first n minus one digits can be any valid string. If it's one, the previous digit must be zero.", [EQ(["a(n) = a(n−1) + a(n−2)"], ["y"], size=60)]),
          S("a of one is two, a of two is three, and then five, eight, thirteen. The Fibonacci numbers again.", [ROW([2, 3, 5, 8, 13, 21, 34, 55, 89, 144], w=96, h=100, size=44, y=640, hl=[9])]),
          S("a of ten is one hundred forty four.", [EQ(["a(10) = 144"], ["g"], size=100)])],
         "144", "One hundred forty four strings."),

    prob(108, "Top Tech", "COUNTING", "Regions From 10 Lines", "Maximum pieces of a plane",
         "Ten straight lines cut a plane into regions. What's the maximum?", "10 LINES\nHOW MANY REGIONS?",
         "What is the maximum number of regions that ten straight lines can divide a plane into?",
         [H("10 lines, max regions"), ROW(["1 line: 2", "2 lines: 4", "3 lines: 7"], w=290, h=110, size=38, y=640), F("how many for 10 lines?", "y", 0.7)],
         [S("Each new line can cross every existing line once, at different points, if no two are parallel and no three meet.", [EQ(["new line crosses all old lines"], ["c"], size=54)]),
          S("A new line crossing k old lines is cut into k plus one pieces, and each piece splits a region in two. So it adds k plus one regions.", [EQ(["line number k adds k regions"], ["y"], size=54)]),
          S("Starting from one region: add one, two, three, up to ten.", [EQ(["1 + (1 + 2 + ... + 10)", "= 1 + 55"], ["w", "g"], size=62)]),
          S("That's fifty six regions.", [EQ(["n(n+1)/2 + 1 = 56"], ["g"], size=80)])],
         "56 REGIONS", "Fifty six regions."),

    prob(109, "Harvard", "COUNTING", "Divisible By 3 Or 5", "Inclusion exclusion up to 100",
         "How many numbers up to a hundred are divisible by three or five?", "3 OR 5",
         "How many whole numbers from one to one hundred are divisible by three or by five?",
         [H("1 to 100"), ROW(["÷3", "or", "÷5"], w=200, h=110, size=60, y=640), F("how many?", "y", 0.7)],
         [S("Counting multiples of three and multiples of five and adding them double counts the numbers divisible by both.", [EQ(["33 + 20 = 53 ?", "too many"], ["w", "r"], size=62)], stamp="WRONG"),
          S("Multiples of three: thirty three. Multiples of five: twenty.", [EQ(["⌊100/3⌋ = 33", "⌊100/5⌋ = 20"], ["c", "y"], size=64)]),
          S("Multiples of fifteen were counted twice. There are six of them.", [EQ(["⌊100/15⌋ = 6"], ["r"], size=80)]),
          S("Inclusion exclusion: thirty three plus twenty minus six equals forty seven.", [EQ(["33 + 20 − 6 = 47"], ["g"], size=88)])],
         "47", "Forty seven."),

    prob(110, "Harvard", "COUNTING", "Divisible By 3, 5 Or 7", "Inclusion exclusion up to 1000",
         "Three divisibility rules and one thousand numbers. Count carefully.", "3, 5 OR 7",
         "How many whole numbers from one to one thousand are divisible by three, five, or seven?",
         [H("1 to 1000"), ROW(["÷3", "÷5", "÷7"], cols={0: "c", 1: "y", 2: "p"}, w=220, h=120, size=64, y=640), F("how many?", "y", 0.7)],
         [S("Add the singles, then subtract the overlaps of pairs, then add back numbers divisible by all three.", [EQ(["|A| + |B| + |C|", "− pairs", "+ triple"], ["w", "r", "g"], size=58)]),
          S("Singles: three hundred thirty three, two hundred, and one hundred forty two. That's six hundred seventy five.", [EQ(["333 + 200 + 142 = 675"], ["y"], size=60)]),
          S("Pairs: fifteen gives sixty six, twenty one gives forty seven, thirty five gives twenty eight. Subtract one hundred forty one.", [EQ(["66 + 47 + 28 = 141", "675 − 141 = 534"], ["r", "w"], size=60)]),
          S("All three, one hundred five: nine numbers. Add them back for five hundred forty three.", [EQ(["534 + 9 = 543"], ["g"], size=90)])],
         "543", "Five hundred forty three."),

    prob(111, "Quant", "PROBABILITY", "Expected Max Of Three Dice", "Roll three dice, keep the highest",
         "Roll three dice and keep the highest. What's the average?", "HIGHEST OF\nTHREE DICE",
         "You roll three fair dice and keep the largest. What's the expected value?",
         [H("max of three dice"), ROW([2, 6, 4, "→ 6"], w=140, h=120, size=64, y=640, cols={3: "g"}), F("expected value?", "y", 0.7)],
         [S("Count outcomes by the maximum. The max is at most m in m cubed of the two hundred sixteen outcomes.", [EQ(["P(max ≤ m) = (m/6)^3"], ["y"], size=64)]),
          S("So the number of outcomes with max exactly m is m cubed minus m minus one cubed. One, seven, nineteen, thirty seven, sixty one, ninety one.", [ROW([1, 7, 19, 37, 61, 91], w=140, h=110, size=54, y=640, hl=[5]), F("ways for max = 1 ... 6", "c", 0.7)]),
          S("Weight each by its max and divide by two sixteen. That's one thousand seventy one over two sixteen.", [EQ(["(1+14+57+148+305+546) / 216", "= 1071 / 216"], ["w", "g"], size=52)]),
          S("About four point nine six.", [EQ(["≈ 4.96"], ["g"], size=110)])],
         "4.96", "About four point nine six."),

    prob(112, "Top Tech", "LOGIC", "Chocolate Bar Breaks", "An 8 by 8 bar, how many breaks?",
         "An eight by eight chocolate bar. How many breaks to get single squares?", "BREAK THE\nCHOCOLATE",
         "You have an eight by eight chocolate bar. Each break splits one piece along a line into two pieces. How many breaks do you need to get all sixty four single squares?",
         [H("8 × 8 = 64 squares"), GRID(8, 8, cell=62, checker=True, reveal=False, y=690), F("how many breaks?", "y", 0.7)],
         [S("You might plan row cuts and column cuts, and count carefully. That works but misses the shortcut.", [EQ(["7 + 8 × 7 = 63 ?"], ["c"], size=60)]),
          S("Every break turns one piece into two. So each break increases the number of pieces by exactly one.", [EQ(["1 piece → 64 pieces"], ["y"], size=64)]),
          S("You start with one piece and need sixty four. That's sixty three increases, so sixty three breaks, regardless of how you break.", [EQ(["64 − 1 = 63 breaks"], ["g"], size=80)])],
         "63 BREAKS", "Sixty three, whatever order you use."),

    prob(113, "Top Tech", "COUNTING", "Diagonals Of A Decagon", "How many diagonals in a 10 sided shape?",
         "A ten sided polygon. How many diagonals does it have?", "DIAGONALS OF\nA DECAGON",
         "How many diagonals does a regular ten sided polygon have?",
         [H("a decagon: 10 vertices"), NODES(list("ABCDEFGHIJ"), layout="circle", r=30, hl=[0, 5]), F("how many diagonals?", "y", 0.7)],
         [S("From each vertex you can draw a line to every other vertex, nine lines. But two of those are sides, not diagonals.", [EQ(["9 lines − 2 sides = 7 diagonals"], ["y"], size=58)]),
          S("Ten vertices, seven diagonals each: seventy. But every diagonal was counted from both ends.", [EQ(["10 × 7 = 70", "counted twice"], ["w", "r"], size=62)]),
          S("Divide by two. Thirty five diagonals. The general formula is n times n minus three over two.", [EQ(["10 × 7 / 2 = 35"], ["g"], size=88)])],
         "35", "Thirty five."),

    prob(114, "Harvard", "NUMBER THEORY", "Trailing Zeros Of 1000 Factorial", "Count the factors of five",
         "A bigger version of a famous question: how many zeros end a thousand factorial?", "1000!\nTRAILING ZEROS",
         "How many zeros are at the end of one thousand factorial?",
         [H("1000! = 1 × 2 × ... × 1000"), EQ(["trailing zeros = ?"], ["y"], size=66), F("how many zeros?", "y", 0.7)],
         [S("Each zero is a factor of ten, which is a two times a five. Twos are plentiful, so count the fives.", [EQ(["zeros = number of 5s"], ["c"], size=64)]),
          S("Multiples of five give two hundred. Multiples of twenty five give another forty. Multiples of one twenty five give eight, and six twenty five gives one.", [EQ(["1000/5 = 200", "1000/25 = 40", "1000/125 = 8", "1000/625 = 1"], ["w", "w", "w", "w"], size=48)]),
          S("Add them up: two hundred forty nine.", [EQ(["200 + 40 + 8 + 1 = 249"], ["g"], size=88)])],
         "249", "Two hundred forty nine zeros."),

    prob(115, "Harvard", "NUMBER THEORY", "Smallest Number Divisible By 1 To 10", "Least common multiple",
         "Find the smallest number that every whole number from one to ten divides evenly.", "DIVISIBLE BY\n1 TO 10",
         "What is the smallest positive number that is divisible by every integer from one to ten?",
         [H("divisible by 1, 2, 3, ... 10"), ROW([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], w=84, h=90, size=44, y=640), F("smallest such number?", "y", 0.7)],
         [S("Multiplying them all gives three point six million, which works but is far too big.", [EQ(["10! = 3,628,800 (too big)"], ["r"], size=56)]),
          S("You only need the highest power of each prime up to ten. Two cubed from eight, three squared from nine, five, seven.", [EQ(["2³ = 8", "3² = 9", "5", "7"], ["w", "w", "w", "w"], size=54)]),
          S("Multiply eight times nine times five times seven. That's twenty five hundred twenty.", [EQ(["8 × 9 × 5 × 7 = 2520"], ["g"], size=80)])],
         "2520", "Two thousand five hundred twenty."),

    prob(116, "Harvard", "COUNTING", "Arrangements Of MISSISSIPPI", "Letters with repeats",
         "How many different words can you make by shuffling the letters of MISSISSIPPI?", "MISSISSIPPI",
         "How many different arrangements are there of the letters in the word MISSISSIPPI?",
         [H("11 letters, many repeats"), ROW(["M", "I", "S", "S", "I", "S", "S", "I", "P", "P", "I"], per=11, w=76, h=90, size=44, y=640), F("how many arrangements?", "y", 0.7)],
         [S("Eleven letters would give eleven factorial, almost forty million orderings. But swapping two identical letters changes nothing.", [EQ(["11! = 39,916,800"], ["r"], size=64)]),
          S("The letters repeat: four I's, four S's, two P's, and one M.", [EQ(["I × 4, S × 4, P × 2, M × 1"], ["c"], size=54)]),
          S("Divide by the arrangements of the repeats: four factorial for I, four for S, two for P.", [EQ(["11! / (4! · 4! · 2!)", "= 39,916,800 / 1,152"], ["w", "y"], size=58)]),
          S("That's thirty four thousand six hundred fifty.", [EQ(["= 34,650"], ["g"], size=100)])],
         "34,650", "Thirty four thousand six hundred fifty."),

    prob(117, "Top Tech", "COUNTING", "Seating 6 People Around A Table", "Round table arrangements",
         "Six people around a round table. How many different seatings?", "ROUND TABLE\n6 PEOPLE",
         "In how many different ways can six people sit around a round table, if rotations of the same arrangement count as the same?",
         [H("rotations don't count"), NODES(list("ABCDEF"), layout="circle", r=40, hl=[0]), F("how many seatings?", "y", 0.7)],
         [S("In a row, six people have six factorial, seven hundred twenty arrangements.", [EQ(["6! = 720"], ["w"], size=80)]),
          S("But at a round table, rotating everyone one seat gives the same arrangement. Each seating appears six times.", [EQ(["6 rotations = 1 seating"], ["r"], size=60)]),
          S("Divide by six: that's five factorial. Equivalently, seat one person, then arrange the other five.", [EQ(["720 / 6 = 120", "= 5!"], ["w", "g"], size=70)])],
         "120", "One hundred twenty."),

    prob(118, "Harvard", "MATH", "Sum Of The First 50 Odd Numbers", "A square in disguise",
         "Add the first fifty odd numbers. There's no need to add them one by one.", "50 ODD\nNUMBERS",
         "What's the sum of the first fifty odd numbers, one plus three plus five, and so on?",
         [H("1 + 3 + 5 + ... + 99"), ROW([1, 3, 5, 7, "...", 97, 99], w=110, h=100, size=46, y=640), F("sum?", "y", 0.7)],
         [S("Look at small cases. One is one. One plus three is four. One plus three plus five is nine.", [ROW([1, 4, 9, 16, 25], w=140, h=110, size=60, y=640, hl=[4]), F("always a perfect square", "c", 0.65)]),
          S("Each new odd number adds an L shaped layer to a square. The first n odd numbers always make n squared.", [GRID(4, 4, cell=96, fill={"0,0": "y", "1,0": "c", "1,1": "c", "0,1": "c", "2,0": "p", "2,1": "p", "2,2": "p", "0,2": "p", "1,2": "p"}, reveal=False, y=690)]),
          S("Fifty odd numbers: fifty squared.", [EQ(["50² = 2500"], ["g"], size=100)])],
         "2500", "Two thousand five hundred."),

    prob(119, "Top Tech", "LOGIC", "15 Friends With 3 Friends Each", "A handshake argument",
         "Fifteen people, each friends with exactly three others. Can it happen?", "15 PEOPLE\n3 FRIENDS EACH",
         "In a group of fifteen people, can each person be friends with exactly three others in the group?",
         [H("15 people · 3 friends each"), NODES(list(range(1, 11)), per=5, y=620, r=34, hl=[0]), F("is it possible?", "y", 0.7)],
         [S("It sounds possible, by arranging friendships in some pattern. Count the friendship ends instead.", [EQ(["15 × 3 = 45 friendship ends"], ["y"], size=58)]),
          S("Every friendship has exactly two ends, one at each person. So the total number of ends must be even.", [EQ(["ends = 2 × friendships", "→ even"], ["c", "g"], size=64)]),
          S("Forty five is odd. So it's impossible.", [EQ(["45 is odd", "→ impossible"], ["r", "r"], size=80)])],
         "IMPOSSIBLE", "Impossible. The total of friendship ends would be odd."),

    prob(120, "Harvard", "NUMBER THEORY", "Divisible By 9 Digit Test", "Is 1234567890 divisible by 9?",
         "Is one billion two hundred thirty four million and so on divisible by nine? Check without dividing.", "DIVISIBLE\nBY 9?",
         "How can you tell whether a number like one two three four five six seven eight nine zero is divisible by nine, without dividing?",
         [H("1,234,567,890 ÷ 9 ?"), ROW([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], w=84, h=96, size=50, y=640), F("divisible by 9?", "y", 0.7)],
         [S("Long division works, but there's a one line test. A number is divisible by nine exactly when its digit sum is.", [EQ(["N ≡ digit sum  (mod 9)"], ["y"], size=58)]),
          S("Why? Each power of ten leaves remainder one when divided by nine. So every digit counts as itself.", [EQ(["10 = 9 + 1", "100 = 99 + 1", "1000 = 999 + 1"], ["w", "w", "w"], size=52)]),
          S("Add the digits: one plus two plus up to nine, plus zero. Forty five.", [EQ(["1+2+...+9+0 = 45"], ["c"], size=62)]),
          S("Forty five is nine times five. So yes, the number is divisible by nine.", [EQ(["45 = 9 × 5", "→ divisible"], ["w", "g"], size=70)])],
         "YES", "Yes. Its digit sum is forty five."),

    prob(121, "Google", "ALGORITHMS", "Merge Overlapping Intervals", "Sort, then sweep",
         "A classic calendar problem: merge all overlapping meetings into the fewest blocks.", "MERGE\nINTERVALS",
         "Given a list of intervals like one to three, two to six, eight to ten, fifteen to eighteen, merge all overlapping intervals.",
         [H("[1,3] [2,6] [8,10] [15,18]"), TL([("1–3", 1, 3, "c"), ("2–6", 2, 6, "y"), ("8–10", 8, 10, "c"), ("15–18", 15, 18, "y")], total=18, step=3), F("merge the overlaps", "y", 0.7)],
         [S("Comparing every pair works but takes quadratic time. Sorting first makes overlaps neighbours.", [EQ(["sort by start: O(n log n)"], ["c"], size=60)]),
          S("Walk through the sorted list, keeping the current merged interval. If the next one starts before the current ends, extend it.", [EQ(["[1,3] + [2,6] → [1,6]", "next start 8 > 6 → new interval"], ["g", "y"], size=50)]),
          S("The result is one to six, eight to ten, and fifteen to eighteen.", [TL([("1–6", 1, 6, "g"), ("8–10", 8, 10, "c"), ("15–18", 15, 18, "y")], total=18, step=3), F("3 intervals", "g", 0.7)])],
         "[1,6] [8,10] [15,18]", "Three merged intervals, in n log n time."),

    prob(122, "Amazon", "ALGORITHMS", "Valid Anagram Check", "Same letters, different order?",
         "Are two words made of the same letters? Do it in one pass.", "ANAGRAM\nCHECK",
         "How do you check whether two strings are anagrams of each other in linear time?",
         [H("listen  vs  silent"), ROW(["listen", "silent"], cols={0: "c", 1: "y"}, w=320, h=120, size=54, y=640), F("same letters?", "y", 0.7)],
         [S("Sorting both strings and comparing works, but costs n log n.", [EQ(["sort both: O(n log n)"], ["r"], size=60)]),
          S("Count the letters instead. Make a table of twenty six counters. Add one for each letter of the first word.", [EQ(["l:1  i:1  s:1  t:1  e:1  n:1"], ["c"], size=48)]),
          S("Subtract one for each letter of the second word. If every counter ends at zero, they're anagrams.", [EQ(["all counters = 0", "→ anagrams"], ["w", "g"], size=64)]),
          S("One pass over each word, constant extra memory.", [EQ(["O(n) time", "O(1) memory"], ["g", "g"], size=64)])],
         "COUNT LETTERS", "A letter count table, linear time."),

    prob(123, "Amazon", "ALGORITHMS", "First Unique Character", "Find the first letter that appears once",
         "In the word swiss, which letter appears first with no repeats?", "FIRST\nUNIQUE LETTER",
         "Given a string, how do you find the first character that appears only once, in linear time?",
         [H("s w i s s"), ROW(["s", "w", "i", "s", "s"], w=120, h=110, size=64, y=640), F("first letter that appears once?", "y", 0.7)],
         [S("For each character, scanning the rest of the string for repeats takes quadratic time.", [EQ(["O(n²)"], ["r"], size=80)]),
          S("First pass: count every character in a hash map. For swiss: s three, w one, i one.", [EQ(["s → 3", "w → 1", "i → 1"], ["r", "g", "g"], size=60)]),
          S("Second pass: walk the string in order and return the first character whose count is one.", [ROW(["s", "w", "i", "s", "s"], cols={0: "r", 1: "g"}, w=120, h=110, size=64, y=640), F("answer: w", "g", 0.65)])],
         "w", "The letter w. Two passes, linear time."),

    prob(124, "Google", "ALGORITHMS", "Longest Substring Without Repeats", "Sliding window",
         "In a string, find the longest stretch with no repeated letter.", "LONGEST\nNO-REPEAT STRETCH",
         "Given a string, find the length of the longest substring without repeating characters. For example, a b c a b c b b.",
         [H("a b c a b c b b"), ROW(["a", "b", "c", "a", "b", "c", "b", "b"], w=100, h=100, size=54, y=640, cols={0: "g", 1: "g", 2: "g"}), F("longest stretch without a repeat?", "y", 0.7)],
         [S("Checking every substring takes cubic time. A window that slides is far better.", [EQ(["all substrings: O(n³)"], ["r"], size=60)]),
          S("Keep a left and right edge. Move the right edge forward. If the new letter already sits inside the window, jump the left edge past its earlier position.", [EQ(["window: a b c", "add a → left jumps past old a"], ["g", "y"], size=50)]),
          S("Track the biggest window you ever had. The window a b c has length three, and nothing longer ever appears.", [EQ(["max window = 3"], ["g"], size=88)])],
         "3", "Three. The window is abc."),

    prob(125, "Amazon", "ALGORITHMS", "Product Of Array Except Self", "No division allowed",
         "For every position, the product of all the other numbers, without division.", "PRODUCT OF\nALL THE OTHERS",
         "Given an array of numbers, return an array where each element is the product of all the other elements, without using division, in linear time.",
         [H("[1, 2, 3, 4]"), ROW([1, 2, 3, 4], w=150, h=110, size=64, y=640), F("answer array?", "y", 0.7)],
         [S("Dividing the total product by each element works, unless there's a zero, and division isn't allowed anyway.", [EQ(["total ÷ x   (not allowed)"], ["r"], size=56)]),
          S("Pass left to right, storing the product of everything to the left of each position.", [ROW([1, 1, 2, 6], w=150, h=110, size=64, y=640, cols={0: "c", 1: "c", 2: "c", 3: "c"}), F("left products", "c", 0.65)]),
          S("Pass right to left, multiplying each by the product of everything to its right.", [ROW([24, 12, 8, 6], w=150, h=110, size=64, y=640, cols={0: "g", 1: "g", 2: "g", 3: "g"}), F("× right products", "g", 0.65)]),
          S("Two passes, linear time, no division.", [EQ(["[24, 12, 8, 6]"], ["g"], size=80)])],
         "[24, 12, 8, 6]", "Twenty four, twelve, eight, six."),
]
