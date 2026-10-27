"""Interview problems 52-76 (algorithms and systems). Small simulations below check the claims used in the narration."""
import math
from iq_helpers import *

# --- checks ---
assert math.isclose(math.sqrt(2 * 2 ** 32 * math.log(2)), 77163, rel_tol=1e-3)
assert 30 == math.ceil(math.log2(10 ** 9))
fib = [1, 1]
for _ in range(10):
    fib.append(fib[-1] + fib[-2])
assert fib[10] == 89                      # ways to climb 10 stairs
assert abs(0.1 + 0.2 - 0.3) > 1e-17
assert math.ceil(math.log2(math.factorial(10))) == 22
assert 2 ** 30 > 10 ** 9 > 2 ** 29


def _popcount_steps(n):
    c = 0
    while n:
        n &= n - 1
        c += 1
    return c


assert _popcount_steps(0b1011_0100) == 4

PROBLEMS = [
    prob(52, "Amazon", "ALGORITHMS", "Detect A Cycle In A Linked List", "Tortoise and hare",
         "Amazon loves this one. A linked list that might loop forever, and you get no extra memory.", "LINKED LIST\nLOOP?",
         "Given a linked list, how can you tell whether it contains a cycle, using only constant extra memory?",
         [H("does the list loop back?"), NODES(["1", "2", "3", "4", "5"], edges=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 2)], y=640, r=40, xy=[(0.05, 0.4), (0.25, 0.4), (0.45, 0.4), (0.65, 0.4), (0.85, 0.4)]),
          F("O(1) memory", "y", 0.7)],
         [S("The obvious way is to remember every node you've visited in a set. It works, but costs memory proportional to the list.", [EQ(["visited set → O(n) memory"], ["r"], size=56)], stamp="WRONG"),
          S("Use two pointers. A slow one moves one step at a time, a fast one moves two. Both start at the head.", [ROW(["slow: +1", "fast: +2"], cols={0: "c", 1: "y"}, w=300, h=120, size=48, y=640)]),
          S("If there's no cycle, the fast pointer simply reaches the end. If there is a cycle, the fast pointer laps the slow one inside the loop and they meet.", [EQ(["no cycle: fast hits the end", "cycle: fast catches slow"], ["c", "g"], size=54)]),
          S("Each step the gap shrinks by one, so they must meet. It runs in linear time and constant memory.", [EQ(["time O(n)", "memory O(1)"], ["g", "g"], size=70)])],
         "TWO POINTERS", "Floyd's tortoise and hare. Linear time, constant memory."),

    prob(53, "Amazon", "ALGORITHMS", "Find The Missing Number", "1 to n with one missing",
         "An array holds every number from one to n except one. Find it in a single pass.", "ONE NUMBER\nIS MISSING",
         "An array contains the numbers one to n, with exactly one missing. How do you find the missing number in linear time and constant space?",
         [H("n = 8, one missing"), ROW([1, 2, 3, 5, 6, 7, 8], w=100, h=100, size=50, y=640, cols={}), F("which is missing?", "y", 0.7)],
         [S("Sorting works, but it's n log n. A hash set works, but it uses extra memory. There's a one line trick.", [EQ(["sort: O(n log n)", "set: O(n) memory"], ["r", "r"], size=56)], stamp="WRONG"),
          S("The sum of one to n is n times n plus one over two. For eight that's thirty six.", [EQ(["1 + 2 + ... + 8 = 8 × 9 / 2 = 36"], ["y"], size=50)]),
          S("Add up the array. It totals thirty two. The difference is the missing number.", [EQ(["array sum = 32", "36 − 32 = 4"], ["w", "g"], size=70)]),
          S("An alternative is to XOR all indexes with all values. Pairs cancel and the missing number is left, with no overflow risk.", [EQ(["XOR(1..n) ⊕ XOR(array) = missing"], ["c"], size=48)])],
         "4", "The missing number is four, found in one pass."),

    prob(54, "Meta", "ALGORITHMS", "Reverse A Linked List", "Three pointers",
         "Reverse a linked list in place. Three pointers and a loop.", "REVERSE A\nLINKED LIST",
         "How do you reverse a singly linked list in place, in linear time?",
         [H("1 → 2 → 3 → 4"), NODES(["1", "2", "3", "4"], edges=[(0, 1), (1, 2), (2, 3)], y=640, r=44), F("reverse it in place", "y", 0.7)],
         [S("Walk down the list and keep three variables: previous, current, and next. Previous starts as nothing.", [ROW(["prev = null", "curr = head", "next = ?"], cols={0: "d", 1: "y", 2: "c"}, w=290, h=120, size=36, y=640)]),
          S("At each step save current's next, point current back at previous, then slide both forward.", [EQ(["next = curr.next", "curr.next = prev", "prev = curr", "curr = next"], ["c", "y", "w", "w"], size=48)]),
          S("After one pass previous points at the new head. Each node's arrow now points backward.", [NODES(["4", "3", "2", "1"], edges=[(0, 1), (1, 2), (2, 3)], y=640, r=44, hl=[0]), F("O(n) time, O(1) memory", "g", 0.7)])],
         "3 POINTERS", "Linear time, constant space."),

    prob(55, "Google", "ALGORITHMS", "Two Sum With A Hash Map", "Find two numbers that add to a target",
         "The most asked coding question of all. And the brute force is just the beginning.", "TWO SUM",
         "Given an array of numbers and a target, find two numbers that add up to the target. How do you do it in linear time?",
         [H("target = 9"), ROW([2, 7, 11, 15], w=150, h=110, size=54, y=640), F("which two add to 9?", "y", 0.7)],
         [S("Checking every pair works, but it takes quadratic time. For a million numbers, that's half a trillion checks.", [EQ(["all pairs: O(n²)"], ["r"], size=66)], stamp="WRONG"),
          S("Walk once through the array. For each number, ask: have I already seen nine minus this number?", [EQ(["x = 2 → need 7", "seen {} → no, store 2"], ["w", "c"], size=54)]),
          S("Keep a hash map of numbers seen so far. Looking up is constant time.", [EQ(["x = 7 → need 2", "2 is in the map → found!"], ["w", "g"], size=54)]),
          S("One pass, one hash map. Linear time.", [EQ(["O(n) time", "O(n) memory"], ["g", "y"], size=70)])],
         "2 + 7", "Two and seven, found in a single pass."),

    prob(56, "Google", "ALGORITHMS", "Majority Element", "More than half the array",
         "Find the element that appears more than half the time, with constant memory.", "THE MAJORITY\nELEMENT",
         "An array has an element that appears more than half the time. How do you find it in one pass with constant extra memory?",
         [H("one value fills over half"), ROW([2, 2, 1, 1, 1, 2, 2], w=110, h=100, size=54, y=640), F("O(1) memory?", "y", 0.7)],
         [S("Counting with a hash map works, but uses memory proportional to the number of distinct values.", [EQ(["hash map: O(n) memory"], ["r"], size=56)]),
          S("Boyer Moore voting: keep a candidate and a count. If the count is zero, take the current number as candidate.", [EQ(["count = 0 → candidate = x", "same as candidate → count + 1", "different → count − 1"], ["c", "g", "r"], size=46)]),
          S("Each differing pair cancels out one majority and one other. The majority has more than half, so it survives.", [ROW(["2", "2", "1", "1", "1", "2", "2"], cols={0: "g", 1: "g", 2: "r", 3: "r", 4: "r", 5: "g", 6: "g"}, w=110, h=100, size=54, y=640), F("candidate: 2", "g", 0.7)])],
         "VOTING", "Boyer Moore voting finds it in one pass."),

    prob(57, "Google", "BIT TRICKS", "Count The Set Bits", "Brian Kernighan's trick",
         "Count how many ones are in a binary number, without looping over all 32 bits.", "COUNT THE\n1 BITS",
         "How do you count the number of one bits in an integer, using time proportional to the number of ones?",
         [H("1011 0100"), ROW([1, 0, 1, 1, 0, 1, 0, 0], w=100, h=100, size=54, y=640, hl=[0, 2, 3, 5]), F("how many ones?", "y", 0.7)],
         [S("Checking each of the thirty two bits works, but always takes thirty two steps.", [EQ(["loop 32 times"], ["r"], size=70)]),
          S("Here's the trick. n and n minus one clears the lowest set bit. Subtracting one flips the trailing zeros and that bit.", [EQ(["1011 0100", "1011 0011  (n − 1)", "1011 0000  (n & n−1)"], ["w", "c", "g"], size=50)]),
          S("Repeat until n is zero and count the steps. One step per one bit.", [EQ(["1011 0100 → 4 ones", "4 steps"], ["w", "g"], size=64)])],
         "n & (n−1)", "Count loops equal the number of ones."),

    prob(58, "Apple", "BIT TRICKS", "Is It A Power Of Two", "One line, no loop",
         "Check if a number is a power of two in a single expression.", "POWER\nOF TWO?",
         "How do you check whether a positive integer is a power of two in one expression, with no loop?",
         [H("8 → yes     6 → no"), ROW(["1000", "0110"], cols={0: "g", 1: "r"}, w=300, h=120, size=60, y=640), F("one expression", "y", 0.7)],
         [S("A power of two in binary has exactly one bit set. Eight is one zero zero zero.", [ROW(["1", "0", "0", "0"], w=120, h=120, size=64, y=640, hl=[0])]),
          S("Subtracting one turns that bit off and every bit below it on. So n and n minus one share no bits.", [EQ(["1000  (8)", "0111  (7)", "1000 & 0111 = 0000"], ["w", "w", "g"], size=54)]),
          S("Any number with two or more bits set keeps its top bit after the and, so the result isn't zero.", [EQ(["0110 & 0101 = 0100 ≠ 0"], ["r"], size=56)])],
         "n & (n−1) == 0", "n and n minus one equals zero, for positive n."),

    prob(59, "Microsoft", "BIT TRICKS", "Swap Without A Temp Variable", "XOR swap",
         "Swap two numbers without a third variable. A classic that still shows up.", "SWAP\nWITHOUT TEMP",
         "How do you swap two integers without using a temporary variable?",
         [H("a = 5   b = 9"), ROW(["a = 5", "b = 9"], cols={0: "c", 1: "y"}, w=300, h=120, size=54, y=640), F("no temp variable", "y", 0.7)],
         [S("XOR has a neat property: x xor y xor y gives back x. So XOR is its own undo.", [EQ(["x ⊕ y ⊕ y = x"], ["c"], size=70)]),
          S("Three steps. a becomes a xor b. Then b becomes a xor b, which is the old a. Then a becomes a xor b again, the old b.", [EQ(["a = a ⊕ b", "b = a ⊕ b   (old a)", "a = a ⊕ b   (old b)"], ["w", "c", "y"], size=50)]),
          S("Try with five and nine. Five xor nine is twelve. Twelve xor nine is five. Twelve xor five is nine.", [EQ(["a = 5 ⊕ 9 = 12", "b = 12 ⊕ 9 = 5", "a = 12 ⊕ 5 = 9"], ["w", "w", "g"], size=52)])],
         "XOR", "Three xors swap the values."),

    prob(60, "Amazon", "BIT TRICKS", "The Number That Appears Once", "Every other number appears twice",
         "Every number appears twice except one. Find it with no extra memory.", "FIND THE\nLONELY NUMBER",
         "Every number in an array appears twice except one that appears once. How do you find it in linear time with constant memory?",
         [H("pairs everywhere, one single"), ROW([4, 1, 2, 1, 2], w=130, h=110, size=60, y=640, hl=[0]), F("find the single one", "y", 0.7)],
         [S("A hash map counts each number, but it needs memory for every distinct value.", [EQ(["hash map: O(n) memory"], ["r"], size=56)]),
          S("Use XOR. A number xor itself is zero, and a number xor zero is itself. Order doesn't matter.", [EQ(["x ⊕ x = 0", "x ⊕ 0 = x"], ["c", "c"], size=70)]),
          S("XOR everything together. Every pair cancels to zero, leaving only the single number.", [EQ(["4 ⊕ 1 ⊕ 2 ⊕ 1 ⊕ 2", "= 4 ⊕ 0 ⊕ 0 = 4"], ["w", "g"], size=56)])],
         "4", "Four, in one pass with no extra memory."),

    prob(61, "Google", "ALGORITHMS", "Binary Search A Billion", "How many steps for 1,000,000,000?",
         "How many steps does it take to find one name among a billion?", "1 IN A BILLION",
         "A sorted list has one billion items. In the worst case, how many comparisons does binary search need?",
         [H("sorted list, 1,000,000,000 items"), EQ(["worst case = ?"], ["y"], size=70), F("how many comparisons?", "y", 0.7)],
         [S("Linear search could take a billion steps. Binary search halves the remaining range each time.", [BARS([1000, 500, 250, 125], labels=["1B", "500M", "250M", "125M"], base=880, maxh=300, fmt="{}", hl=[3])]),
          S("After k steps there are a billion over two to the k items left. You stop when that is one.", [EQ(["10⁹ / 2^k = 1", "2^k = 10⁹"], ["w", "y"], size=64)]),
          S("Two to the thirty is one point oh seven billion. Two to the twenty nine falls short.", [EQ(["2^29 = 0.54 billion  <  1 billion", "2^30 = 1.07 billion  ≥  1 billion"], ["r", "g"], size=44)]),
          S("So thirty comparisons find any item among a billion.", [EQ(["k = 30"], ["g"], size=110)])],
         "30 STEPS", "Thirty comparisons."),

    prob(62, "Amazon", "ALGORITHMS", "Climbing Stairs 10 Steps", "Ways to climb with 1 or 2 steps",
         "You can climb one or two stairs at a time. How many ways to reach the tenth step?", "CLIMBING\nSTAIRS",
         "You climb a staircase of ten steps, taking either one or two steps at a time. How many different ways can you reach the top?",
         [H("1 or 2 steps at a time"), ROW([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], w=84, h=90, size=44, y=640), F("how many ways to step 10?", "y", 0.7)],
         [S("Think about the last move. To reach step n, you came from step n minus one or step n minus two.", [EQ(["ways(n) = ways(n−1) + ways(n−2)"], ["y"], size=52)]),
          S("One way to reach step one, two ways to reach step two. Then three, five, eight, thirteen.", [ROW([1, 2, 3, 5, 8, 13, 21, 34, 55, 89], w=96, h=100, size=44, y=640, hl=[9])]),
          S("It's the Fibonacci sequence. Step ten has eighty nine ways.", [EQ(["ways(10) = 89"], ["g"], size=100)])],
         "89 WAYS", "Eighty nine ways."),

    prob(63, "Meta", "ALGORITHMS", "Balanced Parentheses With A Stack", "Is the string valid?",
         "Check whether every bracket in a string is closed in the right order.", "BALANCED\nBRACKETS?",
         "How do you check whether a string of brackets, like open paren open bracket close bracket close paren, is balanced?",
         [H("( [ ] )   vs   ( [ ) ]"), ROW(["([])", "([)]"], cols={0: "g", 1: "r"}, w=300, h=120, size=64, y=640), F("is it balanced?", "y", 0.7)],
         [S("Counting opens and closes isn't enough. The string open paren open bracket close paren close bracket has equal counts but is wrong.", [EQ(["([)]  equal counts"], ["r"], size=60), F("order matters", "r", 0.6)], stamp="WRONG"),
          S("Use a stack. Push every opening bracket. When you see a closing bracket, pop and check that it matches.", [EQ(["open → push", "close → pop and match"], ["c", "y"], size=60)]),
          S("If a pop doesn't match, or the stack is empty, it's invalid. At the end, the stack must be empty.", [EQ(["mismatch → invalid", "stack empty at end → valid"], ["r", "g"], size=54)])],
         "STACK", "Push opens, pop on closes. Linear time."),

    prob(64, "Google", "ALGORITHMS", "Why Sorting Takes n Log n", "A lower bound proof",
         "Why can't any comparison sort beat n log n? A counting argument proves it.", "WHY SORTING\nIS SLOW",
         "Why can no comparison based sorting algorithm be faster than n log n in the worst case?",
         [H("comparison sort of n items"), ROW(["n!  orderings", "yes/no questions"], cols={0: "y", 1: "c"}, w=400, h=120, size=40, y=640), F("why not faster?", "y", 0.7)],
         [S("There are n factorial possible orderings of n items. The algorithm must figure out which one it is.", [EQ(["10 items → 10! = 3,628,800"], ["y"], size=58)]),
          S("Each comparison gives one yes or no answer, so it at most halves the possibilities.", [EQ(["1 comparison → 2 outcomes", "k comparisons → 2^k outcomes"], ["c", "c"], size=52)]),
          S("To tell n factorial orderings apart you need two to the k at least n factorial. So k is at least log of n factorial.", [EQ(["2^k ≥ n!", "k ≥ log₂(n!)"], ["w", "g"], size=64)]),
          S("Stirling's approximation says log of n factorial is about n log n. That's the lower bound.", [EQ(["log₂(n!) ≈ n log₂ n"], ["g"], size=64)])],
         "n log n", "No comparison sort beats n log n."),

    prob(65, "Google", "ALGORITHMS", "Fisher Yates Shuffle", "Is your shuffle truly uniform?",
         "A shuffle that looks fine but is subtly biased. How do you shuffle a deck fairly?", "SHUFFLE\nTHE DECK",
         "How do you shuffle an array so that every permutation is equally likely?",
         [H("every permutation equally likely"), ROW(["A", "B", "C", "D"], w=150, h=110, size=60, y=640), F("fair shuffle?", "y", 0.7)],
         [S("A common mistake is to swap each element with a random position anywhere in the array. It looks random, but it's biased.", [EQ(["n^n paths", "n! permutations"], ["r", "r"], size=62), F("n^n isn't divisible by n!", "r", 0.65)], stamp="WRONG"),
          S("Fisher Yates: go from the last position down. Pick a random index from zero up to the current position, and swap.", [EQ(["for i from n−1 down to 1:", "j = random(0..i)", "swap(a[i], a[j])"], ["c", "y", "w"], size=48)]),
          S("The last slot has n choices, the next n minus one, and so on. That gives exactly n factorial equally likely outcomes.", [EQ(["n × (n−1) × ... × 1 = n!"], ["g"], size=60)])],
         "FISHER–YATES", "Pick from the remaining positions only. Each permutation has probability one over n factorial."),

    prob(66, "Google", "ALGORITHMS", "Reservoir Sampling", "Pick one at random from a stream",
         "A stream of unknown length, and you must pick one item uniformly at random.", "PICK 1 FROM\nA STREAM",
         "Items arrive one at a time, and you don't know how many there will be. How do you pick one uniformly at random, using constant memory?",
         [H("length unknown, one pass"), ROW(["x1", "x2", "x3", "..."], w=150, h=110, size=54, y=640), F("uniform pick, O(1) memory", "y", 0.7)],
         [S("You can't wait until the end to count them, and you can't store them all. Decide as you go.", [EQ(["no counting first", "no storing"], ["r", "r"], size=62)]),
          S("Keep the first item. When the k-th item arrives, replace the kept one with probability one over k.", [EQ(["item 1: keep", "item k: replace with prob 1/k"], ["w", "y"], size=58)]),
          S("Check item one survives to the end with probability one times one half times two thirds, and so on, which telescopes to one over n.", [EQ(["1 × 1/2 × 2/3 × 3/4 × ... × (n−1)/n", "= 1/n"], ["w", "g"], size=48)])],
         "1/k RULE", "Replace with probability one over k. Everyone ends up equally likely."),

    prob(67, "Google", "SYSTEMS", "Hash Collisions Birthday Bound", "32 bit hashes",
         "A hash with four billion values. How many items before a collision is likely?", "HASH\nCOLLISIONS",
         "A hash function outputs 32 bit values, about four point three billion possibilities. Roughly how many items can you hash before a collision is more likely than not?",
         [H("2^32 possible hash values"), ROW(["4.29 billion values", "collision at ?"], cols={0: "y", 1: "r"}, w=400, h=120, size=36, y=640), F("how many items for a 50% collision?", "y", 0.7)],
         [S("Many people guess two billion, half the space. That's wrong. It's the birthday paradox in disguise.", [BIG("2 billion ?", "r", size=100)], stamp="WRONG"),
          S("A collision needs any pair to match. With n items there are about n squared over two pairs.", [EQ(["pairs ≈ n² / 2"], ["c"], size=70)]),
          S("Each pair collides with probability one over two to the thirty two. Set pairs over two to the thirty two to about point seven.", [EQ(["n² / 2^33 ≈ 0.69"], ["y"], size=62)]),
          S("Solve for n: about seventy seven thousand items. Far fewer than anyone expects.", [EQ(["n ≈ √(2 · 2^32 · ln 2)", "≈ 77,000"], ["w", "g"], size=58)])],
         "~77,000", "Only about seventy seven thousand items."),

    prob(68, "Amazon", "SYSTEMS", "Design An LRU Cache", "O(1) get and put",
         "A cache that evicts the least recently used item, with constant time operations.", "DESIGN AN\nLRU CACHE",
         "Design a cache of fixed size that evicts the least recently used item when full, with constant time get and put.",
         [H("get / put in O(1)"), ROW(["hash map", "linked list"], cols={0: "c", 1: "y"}, w=330, h=120, size=48, y=640), F("what two structures?", "y", 0.7)],
         [S("A plain hash map gives constant lookup, but doesn't know the order of use. A list knows the order but searching is slow.", [EQ(["map: O(1) lookup, no order", "list: order, O(n) lookup"], ["c", "y"], size=52)]),
          S("Combine them. A hash map from key to a node in a doubly linked list. The list is ordered from most to least recently used.", [NODES(["MRU", "...", "...", "LRU"], edges=[(0, 1), (1, 2), (2, 3)], y=620, r=44, hl=[0], cols={3: "r"})]),
          S("On get or put, move that node to the front. When full, drop the node at the tail. All steps are constant time.", [EQ(["use → move to front", "full → evict tail"], ["g", "r"], size=62)])],
         "MAP + LIST", "A hash map plus a doubly linked list."),

    prob(69, "Google", "ALGORITHMS", "Find The Duplicate Number", "n+1 numbers from 1 to n",
         "An array of n plus one numbers, each from one to n. One repeats. Find it without changing the array.", "FIND THE\nDUPLICATE",
         "An array has n plus one integers, each between one and n. At least one repeats. How do you find a duplicate in linear time, constant space, without modifying the array?",
         [H("n + 1 numbers in 1..n"), ROW([3, 1, 3, 4, 2], w=130, h=110, size=60, y=640, hl=[0, 2]), F("find the repeat", "y", 0.7)],
         [S("Sorting modifies the array, and a set uses extra memory. Treat the array as a linked list instead.", [EQ(["index → value → next index"], ["c"], size=58)]),
          S("Each value points to a position. Because there are n plus one values in n slots, two positions point to the same place, so there's a loop.", [NODES(["0", "1", "2", "3", "4"], edges=[(0, 3), (3, 4), (4, 2), (2, 3)], xy=[(0.1, 0.4), (0.3, 0.4), (0.5, 0.4), (0.7, 0.4), (0.9, 0.4)], y=640, r=40, hl=[3])]),
          S("The duplicate value is where the loop starts. Use the tortoise and hare, then move one pointer from the start to find the loop's entrance.", [EQ(["entrance of the cycle = duplicate"], ["g"], size=52)])],
         "FLOYD", "Cycle detection finds it in linear time and constant space."),

    prob(70, "Amazon", "ALGORITHMS", "Maximum Subarray Kadane", "Best consecutive sum",
         "Find the contiguous stretch with the largest sum, in one pass.", "BEST STRETCH\nOF NUMBERS",
         "Given an array of positive and negative numbers, find the contiguous subarray with the largest sum, in linear time.",
         [H("−2, 1, −3, 4, −1, 2, 1, −5, 4"), ROW([-2, 1, -3, 4, -1, 2, 1, -5, 4], w=100, h=100, size=46, y=640), F("best consecutive sum?", "y", 0.7)],
         [S("Trying every start and end takes cubic time naively, or quadratic with prefix sums.", [EQ(["all pairs: O(n²)"], ["r"], size=66)]),
          S("Kadane: keep the best sum ending here. At each number, either extend the running sum or start fresh.", [EQ(["here = max(x, here + x)", "best = max(best, here)"], ["c", "y"], size=54)]),
          S("Walking the array, the running sum peaks at six, covering four, minus one, two, one.", [ROW([4, -1, 2, 1], cols={0: "g", 1: "g", 2: "g", 3: "g"}, w=150, h=110, size=60, y=640), F("4 − 1 + 2 + 1 = 6", "g", 0.7)])],
         "6", "The best subarray sums to six."),

    prob(71, "Google", "SYSTEMS", "Rate Limiter Token Bucket", "Allow bursts, cap the average",
         "Design a rate limiter that allows bursts but caps the average rate.", "DESIGN A\nRATE LIMITER",
         "How would you design a rate limiter that allows short bursts but enforces an average limit?",
         [H("100 requests per minute, bursts OK"), ROW(["tokens", "refill"], cols={0: "y", 1: "c"}, w=300, h=120, size=48, y=640), F("burst + average cap", "y", 0.7)],
         [S("A fixed window counter is simple, but lets double the rate through at a window boundary.", [EQ(["end of window: 100", "start of next: 100", "= 200 in a moment"], ["w", "w", "r"], size=52)], stamp="WRONG"),
          S("Use a token bucket. The bucket holds up to a capacity of tokens and refills at a steady rate.", [BARS([10, 7, 4, 8], labels=["full", "after burst", "low", "refilled"], base=880, maxh=300, hl=[0], fmt="{}")]),
          S("Each request takes one token. No token, the request is rejected or queued. Bursts are limited by capacity, average by refill.", [EQ(["capacity → max burst", "refill rate → average"], ["y", "c"], size=60)])],
         "TOKEN BUCKET", "Capacity sets the burst, the refill rate sets the average."),

    prob(72, "Amazon", "SYSTEMS", "Consistent Hashing", "Add a server, move almost nothing",
         "Add a server to a cluster without reshuffling almost every key.", "CONSISTENT\nHASHING",
         "You spread keys over servers with hash modulo n. When you add a server, almost every key moves. How do you avoid that?",
         [H("key → server"), ROW(["hash(k) mod 4", "add server → mod 5"], cols={0: "c", 1: "r"}, w=400, h=120, size=36, y=640), F("most keys would move", "r", 0.7)],
         [S("With modulo, going from four to five servers remaps about eighty percent of the keys. Caches go cold.", [BARS([20, 80], labels=["keys that stay", "keys that move"], cols={0: "g", 1: "r"}, fmt="{}%", base=880, maxh=300)]),
          S("Put servers and keys on a circle by hashing them. Each key belongs to the next server clockwise.", [NODES(["S1", "k", "S2", "k", "S3", "k"], layout="circle", hl=[0, 2, 4], r=36)]),
          S("Add a server and it only takes keys from its clockwise neighbour. On average one over n of the keys move.", [EQ(["new server takes ~1/n of the keys"], ["g"], size=52)])],
         "THE RING", "Only about one over n of the keys move."),

    prob(73, "Google", "SYSTEMS", "Bloom Filter", "Probably in, definitely not in",
         "Check membership in a huge set with a tiny amount of memory. The catch: sometimes it lies, but only one way.", "BLOOM\nFILTER",
         "How can you test whether an item is in a huge set using very little memory, accepting occasional false positives but no false negatives?",
         [H("billions of items, tiny memory"), ROW(["0", "1", "0", "1", "1", "0", "0", "1"], w=100, h=100, size=50, y=640, hl=[1, 3, 4, 7]), F("a bit array", "y", 0.7)],
         [S("Storing every item exactly would take gigabytes. A hash set is accurate but heavy.", [EQ(["exact set: gigabytes"], ["r"], size=60)]),
          S("Use a bit array and several hash functions. To add an item, set the bits that each hash points to.", [EQ(["add(x): set bits h1(x), h2(x), h3(x)"], ["c"], size=48)]),
          S("To query, check those same bits. If any is zero, the item is definitely not present. If all are one, it's probably present.", [EQ(["any 0 → definitely NOT in", "all 1 → PROBABLY in"], ["g", "y"], size=58)])],
         "NO FALSE NEGATIVES", "No false negatives, a controllable chance of false positives."),

    prob(74, "Microsoft", "COMPLEXITY", "Nested Loop Complexity", "for i, for j < i",
         "What's the time complexity of a loop inside a loop where the inner one depends on the outer?", "BIG O\nOF TWO LOOPS",
         "What's the time complexity of a loop where i runs from zero to n and the inner loop runs j from zero to i?",
         [H("for i in 0..n: for j in 0..i"), EQ(["total steps = ?"], ["y"], size=66), F("O( ? )", "y", 0.7)],
         [S("Many say n squared and stop there. That's right, but the real count tells you how it behaves.", [EQ(["i = 0: 0 steps", "i = 1: 1 step", "i = 2: 2 steps"], ["w", "w", "w"], size=52)]),
          S("The inner loop runs i times on iteration i. Total is zero plus one plus two, up to n minus one.", [EQ(["0 + 1 + 2 + ... + (n−1)", "= n(n−1)/2"], ["y", "g"], size=58)]),
          S("That's about n squared over two. Constants don't matter in big O, so it's quadratic.", [EQ(["O(n²)"], ["g"], size=110)])],
         "O(n²)", "Quadratic. The constant is one half."),

    prob(75, "Google", "SYSTEMS", "Bits For A Billion IDs", "How many bits to number 1,000,000,000 items?",
         "How many bits do you need to give a unique ID to every one of a billion items?", "1 BILLION IDs",
         "How many bits are needed to give a unique number to each of one billion items?",
         [H("1,000,000,000 unique IDs"), ROW(["? bits"], cols={0: "y"}, w=300, h=130, size=72, y=640), F("fewest bits?", "y", 0.7)],
         [S("Each extra bit doubles how many IDs you can represent. Ten bits give one thousand twenty four.", [EQ(["1 bit: 2", "10 bits: 1,024", "20 bits: 1,048,576"], ["w", "w", "w"], size=52)]),
          S("Twenty bits give about a million. Thirty bits give about a billion.", [EQ(["30 bits: 1,073,741,824"], ["g"], size=60)]),
          S("Twenty nine bits give only five hundred thirty seven million, which falls short. So thirty it is.", [EQ(["29 bits: 536,870,912  <  1B", "30 bits is enough"], ["r", "g"], size=54)])],
         "30 BITS", "Thirty bits. It fits in a normal 32 bit integer."),

    prob(76, "Meta", "SYSTEMS", "Why 0.1 Plus 0.2 Isn't 0.3", "Floating point surprise",
         "In nearly every language, zero point one plus zero point two does not equal zero point three. Why?", "0.1 + 0.2\n≠ 0.3",
         "Why does zero point one plus zero point two not equal zero point three in most programming languages?",
         [H("0.1 + 0.2 == 0.3 ?"), ROW(["0.1", "+", "0.2", "=", "0.3?"], w=170, h=110, size=50, y=640), F("false in most languages", "r", 0.7)],
         [S("Computers store numbers in binary. Some decimals, like zero point one, have no exact binary form, just like one third has no exact decimal form.", [EQ(["1/3 = 0.3333...", "0.1 = 0.0001100110011...₂"], ["c", "y"], size=50)]),
          S("So the stored values are tiny approximations. Their sum lands a hair away from the stored value of zero point three.", [EQ(["0.1 + 0.2 = 0.30000000000000004"], ["r"], size=44)]),
          S("To compare floats, check that they're within a small tolerance, not exactly equal. Or use integers, like cents.", [EQ(["abs(a − b) < 1e−9", "or store cents as integers"], ["g", "c"], size=52)])],
         "BINARY ROUNDING", "Binary can't represent zero point one exactly."),
]
