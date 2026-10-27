"""Interview problems 176-200 (data structures, algorithms, systems, SQL). Answers verified by running the algorithms below."""
import heapq, itertools, math
from iq_helpers import *

# ---- verification ----
def _roman(s):
    v = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    t = 0
    for i, ch in enumerate(s):
        t += -v[ch] if i + 1 < len(s) and v[ch] < v[s[i + 1]] else v[ch]
    return t
assert _roman("MCMXCIV") == 1994

def _spiral(m):
    out = []
    while m:
        out += m.pop(0)
        m = [list(r) for r in zip(*m)][::-1]
    return out
assert _spiral([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]

def _topk(a, k):
    from collections import Counter
    c = Counter(a)
    return [x for x, _ in c.most_common(k)]
assert _topk([1, 1, 1, 2, 2, 3], 2) == [1, 2]
assert 2 ** 3 == 8 and len(list(itertools.chain.from_iterable(itertools.combinations(range(3), r) for r in range(4)))) == 8

def _rot(a, t):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == t: return mid
        if a[lo] <= a[mid]:
            if a[lo] <= t < a[mid]: hi = mid - 1
            else: lo = mid + 1
        else:
            if a[mid] < t <= a[hi]: lo = mid + 1
            else: hi = mid - 1
    return -1
assert _rot([4, 5, 6, 7, 0, 1, 2], 0) == 4

def _medians(stream):
    lo, hi, out = [], [], []
    for x in stream:
        heapq.heappush(lo, -x)
        heapq.heappush(hi, -heapq.heappop(lo))
        if len(hi) > len(lo): heapq.heappush(lo, -heapq.heappop(hi))
        out.append(-lo[0] if len(lo) > len(hi) else (-lo[0] + hi[0]) / 2)
    return out
assert _medians([5, 15, 1, 3]) == [5, 10, 5, 4.0]
assert 62 ** 6 == 56800235584 and 2 ** 12 == 4096

def _three(a):
    a = sorted(a); res = set()
    for i in range(len(a)):
        l, r = i + 1, len(a) - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s == 0: res.add((a[i], a[l], a[r])); l += 1; r -= 1
            elif s < 0: l += 1
            else: r -= 1
    return sorted(res)
assert _three([-1, 0, 1, 2, -1, -4]) == [(-1, -1, 2), (-1, 0, 1)]
assert "erbottlewat" in "waterbottle" * 2
assert [3, 2, 1] == sorted([1, 2, 3], reverse=True)

PROBLEMS = [
    prob(176, "Amazon", "ALGORITHMS", "Middle Of A Linked List", "One pass, no length needed",
         "Find the middle of a linked list in a single pass, without knowing its length.", "MIDDLE OF A\nLINKED LIST",
         "How do you find the middle node of a singly linked list in one pass, without knowing its length?",
         [H("1 → 2 → 3 → 4 → 5"), NODES(["1", "2", "3", "4", "5"], edges=[(0, 1), (1, 2), (2, 3), (3, 4)], r=40, y=640), F("find the middle in one pass", "y", 0.7)],
         [S("Counting the length first and then walking half takes two passes. One pass is possible.", [EQ(["count + walk: 2 passes"], ["r"], size=60)]),
          S("Use two pointers. The slow one moves one step, the fast one moves two.", [ROW(["slow +1", "fast +2"], cols={0: "c", 1: "y"}, w=300, h=120, size=50, y=640)]),
          S("When the fast pointer reaches the end, the slow pointer has covered half the distance. It's at the middle.", [NODES(["1", "2", "3", "4", "5"], edges=[(0, 1), (1, 2), (2, 3), (3, 4)], r=40, y=640, hl=[2]), F("slow stops at 3", "g", 0.7)])],
         "SLOW & FAST", "Two pointers, one pass."),

    prob(177, "Amazon", "ALGORITHMS", "Merge Two Sorted Lists", "Zip them together",
         "Merge two sorted lists into one sorted list, in linear time.", "MERGE TWO\nSORTED LISTS",
         "How do you merge two sorted linked lists into one sorted list, in linear time?",
         [H("1 → 3 → 5   and   2 → 4 → 6"), ROW([1, 3, 5], w=110, h=100, size=54, y=600, cols={0: "c", 1: "c", 2: "c"}), ROW([2, 4, 6], w=110, h=100, size=54, y=740, cols={0: "y", 1: "y", 2: "y"})],
         [S("Concatenating and re-sorting costs n log n, and throws away the fact that both lists are already sorted.", [EQ(["concat + sort: O(n log n)"], ["r"], size=56)]),
          S("Keep a pointer into each list. Compare the two fronts and take the smaller one.", [EQ(["1 vs 2 → take 1", "3 vs 2 → take 2"], ["c", "y"], size=60)]),
          S("Repeat until one list runs out, then attach the rest of the other.", [ROW([1, 2, 3, 4, 5, 6], w=120, h=110, size=60, y=640, hl=[0, 1, 2, 3, 4, 5])]),
          S("Each element is touched once. Linear time.", [EQ(["O(n + m)"], ["g"], size=100)])],
         "O(n + m)", "Linear time, constant extra memory with a dummy head."),

    prob(178, "Meta", "ALGORITHMS", "Remove Nth Node From End", "Two pointers n apart",
         "Remove the second to last node of a linked list in one pass.", "REMOVE NTH\nFROM THE END",
         "How do you remove the nth node from the end of a singly linked list in one pass?",
         [H("remove the 2nd from the end"), NODES(["1", "2", "3", "4", "5"], edges=[(0, 1), (1, 2), (2, 3), (3, 4)], r=40, y=640, hl=[3]), F("one pass", "y", 0.7)],
         [S("The simple way counts the length, then walks to the right spot. That's two passes.", [EQ(["pass 1: length", "pass 2: remove"], ["r", "r"], size=60)]),
          S("Use two pointers. Move the first pointer n steps ahead. Then move both together.", [EQ(["fast: n steps ahead", "then both move"], ["c", "y"], size=58)]),
          S("When the fast pointer reaches the end, the slow one is just before the node to remove.", [EQ(["slow.next = slow.next.next"], ["g"], size=58)])],
         "GAP OF n", "Keep two pointers n apart."),

    prob(179, "Meta", "ALGORITHMS", "Binary Tree Level Order", "Breadth first search",
         "Print a binary tree level by level.", "TREE LEVEL\nBY LEVEL",
         "How do you print the values of a binary tree level by level, from the root down?",
         [H("3 → 9, 20 → 15, 7"), NODES(["3", "9", "20", "15", "7"], edges=[(0, 1), (0, 2), (2, 3), (2, 4)], xy=[(0.5, 0.1), (0.25, 0.5), (0.75, 0.5), (0.6, 0.9), (0.9, 0.9)], r=40), F("level by level?", "y", 0.7)],
         [S("Recursive depth first visits one branch at a time, which mixes levels.", [EQ(["DFS: 3, 9, 20, 15, 7"], ["w"], size=56), F("not by level", "r", 0.6)]),
          S("Use a queue. Start with the root. Pop a node, record it, and push its children.", [EQ(["queue: [3]", "pop 3 → push 9, 20"], ["c", "y"], size=60)]),
          S("Process the queue one level at a time, using its size at the start of the level.", [ROW(["[3]", "[9, 20]", "[15, 7]"], w=290, h=110, size=44, y=640, cols={0: "c", 1: "y", 2: "g"})]),
          S("That's breadth first search, linear time.", [EQ(["O(n)"], ["g"], size=100)])],
         "QUEUE (BFS)", "Breadth first search with a queue."),

    prob(180, "Google", "ALGORITHMS", "Maximum Depth Of A Tree", "Recursion in one line",
         "How deep is a binary tree? Recursion answers it in one line.", "HOW DEEP\nIS THE TREE?",
         "How do you compute the maximum depth of a binary tree?",
         [H("depth = longest root-to-leaf path"), NODES(["3", "9", "20", "15", "7"], edges=[(0, 1), (0, 2), (2, 3), (2, 4)], xy=[(0.5, 0.1), (0.25, 0.5), (0.75, 0.5), (0.6, 0.9), (0.9, 0.9)], r=40), F("max depth?", "y", 0.7)],
         [S("The depth of a tree is one plus the larger of its two subtrees' depths.", [EQ(["depth(t) = 1 + max(depth(L), depth(R))"], ["y"], size=50)]),
          S("An empty tree has depth zero. That's the base case.", [EQ(["depth(None) = 0"], ["c"], size=70)]),
          S("Here the right branch goes three, twenty, fifteen. The left is just nine.", [EQ(["left: 1", "right: 2", "depth = 1 + 2 = 3"], ["w", "w", "g"], size=60)])],
         "3", "Depth three."),

    prob(181, "Amazon", "ALGORITHMS", "Symmetric Tree Check", "Is it a mirror image?",
         "Is a binary tree a mirror image of itself?", "MIRROR\nTREE?",
         "How do you check whether a binary tree is symmetric around its centre?",
         [H("is the left side a mirror of the right?"), NODES(["1", "2", "2", "3", "4", "4", "3"], edges=[(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)], xy=[(0.5, 0.1), (0.25, 0.5), (0.75, 0.5), (0.1, 0.9), (0.4, 0.9), (0.6, 0.9), (0.9, 0.9)], r=36), F("symmetric?", "y", 0.7)],
         [S("Comparing the two subtrees node by node isn't enough, since they must mirror, not match.", [EQ(["left must mirror right"], ["c"], size=58)]),
          S("Write a helper that takes two nodes. They mirror if their values match, and the left's left mirrors the right's right.", [EQ(["a.val == b.val", "mirror(a.L, b.R)", "mirror(a.R, b.L)"], ["w", "c", "y"], size=52)]),
          S("Start with the root's two children. Both empty is a match, one empty is a mismatch.", [EQ(["None, None → true", "None, node → false"], ["g", "r"], size=58)])],
         "MIRROR(A, B)", "A recursive mirror check, linear time."),

    prob(182, "Microsoft", "ALGORITHMS", "Reverse The Words In A String", "In place",
         "Reverse the order of the words in a sentence, in place.", "REVERSE\nTHE WORDS",
         "How do you reverse the order of words in a string, in place?",
         [H("the sky is blue"), ROW(["the", "sky", "is", "blue"], w=200, h=110, size=54, y=640), F("blue is sky the", "g", 0.7)],
         [S("Splitting the string and joining it reversed is easy, but uses extra memory.", [EQ(["split + reverse + join: O(n) extra"], ["r"], size=52)]),
          S("An in place trick: reverse the entire string first.", [EQ(["eulb si yks eht"], ["c"], size=70)]),
          S("Then reverse each word on its own.", [EQ(["blue is sky the"], ["g"], size=80)]),
          S("Two reversals fix both the order and the letters.", [EQ(["reverse all + reverse each word"], ["g"], size=50)])],
         "REVERSE TWICE", "Reverse everything, then each word."),

    prob(183, "Amazon", "ALGORITHMS", "Roman Numeral MCMXCIV", "Subtract when a smaller comes first",
         "Convert a Roman numeral to a number. The trick is in the order.", "MCMXCIV = ?",
         "How do you convert the Roman numeral MCMXCIV to an integer?",
         [H("M C M X C I V"), ROW(["M", "CM", "XC", "IV"], w=200, h=110, size=60, y=640), F("what number?", "y", 0.7)],
         [S("Each letter has a value: M is one thousand, C a hundred, X ten, I one, V five.", [ROW(["M 1000", "C 100", "X 10", "V 5", "I 1"], w=170, h=110, size=36, y=640)]),
          S("Scan left to right. If a letter is smaller than the one after it, subtract it. Otherwise add.", [EQ(["IV: 1 < 5 → −1 + 5 = 4"], ["y"], size=58)]),
          S("M is one thousand. CM is nine hundred, XC is ninety, IV is four.", [EQ(["1000 + 900 + 90 + 4"], ["w"], size=64)]),
          S("That's nineteen ninety four.", [EQ(["= 1994"], ["g"], size=110)])],
         "1994", "Nineteen ninety four."),

    prob(184, "Google", "ALGORITHMS", "Spiral Matrix Order", "Peel the layers",
         "Walk a grid in a spiral from the outside in.", "SPIRAL\nORDER",
         "How do you return the elements of a matrix in spiral order, starting at the top left and moving clockwise?",
         [H("3 × 3 grid"), GRID(3, 3, cell=110, text={"0,0": 1, "0,1": 2, "0,2": 3, "1,0": 4, "1,1": 5, "1,2": 6, "2,0": 7, "2,1": 8, "2,2": 9}, reveal=False, y=690), F("spiral order?", "y", 0.7)],
         [S("Keep four boundaries: top, bottom, left, right. Walk the top row, then the right column.", [EQ(["top row →", "right column ↓"], ["c", "c"], size=60)]),
          S("Then the bottom row backwards, and the left column upwards. Shrink the boundaries after each side.", [EQ(["bottom row ←", "left column ↑"], ["y", "y"], size=60)]),
          S("Repeat until the boundaries cross. The order is one, two, three, six, nine, eight, seven, four, five.", [ROW([1, 2, 3, 6, 9, 8, 7, 4, 5], w=100, h=100, size=54, y=640)])],
         "1 2 3 6 9 8 7 4 5", "Linear in the number of cells."),

    prob(185, "Amazon", "ALGORITHMS", "Group The Anagrams", "Same letters, same key",
         "Group words that are anagrams of each other.", "GROUP THE\nANAGRAMS",
         "Given eat, tea, tan, ate, nat, bat, how do you group the words that are anagrams of each other efficiently?",
         [H("eat tea tan ate nat bat"), ROW(["eat", "tea", "tan", "ate", "nat", "bat"], w=130, h=100, size=44, y=640), F("group the anagrams", "y", 0.7)],
         [S("Comparing every pair of words works, but it's quadratic in the number of words.", [EQ(["all pairs: O(n²)"], ["r"], size=64)]),
          S("Give each word a canonical key: its letters sorted. Anagrams share the same key.", [EQ(["eat → aet", "tea → aet", "tan → ant"], ["w", "w", "y"], size=58)]),
          S("Put words in a hash map keyed by that sorted string.", [EQ(["aet: eat, tea, ate", "ant: tan, nat", "abt: bat"], ["g", "c", "y"], size=54)])],
         "SORTED KEY", "A hash map keyed by the sorted letters."),

    prob(186, "Google", "ALGORITHMS", "Top K Frequent Elements", "Bucket sort by count",
         "Find the k most frequent numbers in better than n log n.", "TOP K\nFREQUENT",
         "Given one, one, one, two, two, three and k equal two, how do you find the k most frequent elements in linear time?",
         [H("[1, 1, 1, 2, 2, 3]  k = 2"), ROW([1, 1, 1, 2, 2, 3], w=130, h=110, size=60, y=640), F("two most frequent?", "y", 0.7)],
         [S("Count each value with a hash map. One appears three times, two twice, three once.", [EQ(["1 → 3", "2 → 2", "3 → 1"], ["g", "g", "w"], size=60)]),
          S("Sorting those counts costs n log n. But counts can't exceed the array length, so use buckets.", [ROW(["count 1: [3]", "count 2: [2]", "count 3: [1]"], w=290, h=110, size=40, y=640)]),
          S("Walk the buckets from the highest count down, collecting k elements.", [EQ(["[1, 2]"], ["g"], size=110)]),
          S("Counting plus buckets: linear time.", [EQ(["O(n)"], ["g"], size=100)])],
         "[1, 2]", "One and two, in linear time."),

    prob(187, "Meta", "COUNTING", "All Subsets With A Bitmask", "2 to the n bit patterns",
         "List every subset of a set using nothing but a counter.", "ALL SUBSETS\nWITH BITS",
         "How do you generate all subsets of a set of three elements using a simple loop?",
         [H("{a, b, c}"), ROW(["a", "b", "c"], w=170, h=120, size=70, y=640), F("all subsets?", "y", 0.7)],
         [S("Each subset is a choice for every element: in or out. That's a binary number with one bit per element.", [EQ(["bit 1 = in, bit 0 = out"], ["c"], size=58)]),
          S("Count from zero to two to the n minus one. Each number's bits pick a subset.", [ROW(["000", "001", "010", "011", "100", "101", "110", "111"], w=100, h=100, size=40, y=640)]),
          S("Zero is the empty set, seven is all three. Eight subsets in total.", [EQ(["2^3 = 8 subsets"], ["g"], size=88)])],
         "8 SUBSETS", "Eight subsets from a counter."),

    prob(188, "Google", "ALGORITHMS", "Search In A Rotated Sorted Array", "Binary search with a twist",
         "A sorted array that was rotated. Find a value in logarithmic time.", "ROTATED\nSORTED ARRAY",
         "A sorted array was rotated, like four, five, six, seven, zero, one, two. How do you find the value zero in logarithmic time?",
         [H("4 5 6 7 0 1 2"), ROW([4, 5, 6, 7, 0, 1, 2], w=110, h=100, size=54, y=640), F("find 0 in O(log n)", "y", 0.7)],
         [S("A linear scan works but is slow. The array isn't sorted overall, but one half always is.", [EQ(["one half is always sorted"], ["c"], size=58)]),
          S("Look at the middle. If the left half is sorted, check whether the target lies in it. Otherwise it lies in the right half.", [EQ(["a[lo] ≤ a[mid] → left sorted"], ["y"], size=54)]),
          S("Halve the range each time. Zero is found at index four.", [EQ(["index 4", "O(log n)"], ["g", "g"], size=80)])],
         "INDEX 4", "Binary search, one half is always sorted."),

    prob(189, "Google", "ALGORITHMS", "Median Of A Data Stream", "Two heaps",
         "Numbers arrive one at a time. What's the median right now, instantly?", "RUNNING\nMEDIAN",
         "Numbers arrive in a stream. How do you report the median after each one, efficiently?",
         [H("5, 15, 1, 3"), ROW([5, 15, 1, 3], w=150, h=110, size=60, y=640), F("median after each number?", "y", 0.7)],
         [S("Sorting after every insert costs n log n each time. A better structure splits the data in the middle.", [EQ(["sort each time: slow"], ["r"], size=56)]),
          S("Keep a max heap for the lower half and a min heap for the upper half. Keep their sizes within one of each other.", [ROW(["max heap (low)", "min heap (high)"], cols={0: "c", 1: "y"}, w=330, h=120, size=40, y=640)]),
          S("The median is the top of the bigger heap, or the average of both tops.", [EQ(["5 → 5", "5, 15 → 10", "1, 5, 15 → 5", "1, 3, 5, 15 → 4"], ["w", "w", "w", "g"], size=48)]),
          S("Each insert costs log n, and the median is constant time.", [EQ(["insert: O(log n)", "median: O(1)"], ["y", "g"], size=64)])],
         "TWO HEAPS", "Two heaps, balanced."),

    prob(190, "Amazon", "ALGORITHMS", "Merge K Sorted Lists", "A heap of heads",
         "Merge k sorted lists into one. The heap makes it n log k.", "MERGE K\nSORTED LISTS",
         "How do you merge k sorted lists into one sorted list efficiently?",
         [H("k sorted lists"), ROW(["[1,4,7]", "[2,5,8]", "[3,6,9]"], w=270, h=110, size=40, y=640), F("one sorted list?", "y", 0.7)],
         [S("Merging them two at a time can cost k times n. A heap does better.", [EQ(["pairwise: O(n·k)"], ["r"], size=60)]),
          S("Put the first element of each list in a min heap. Pop the smallest, and push the next element from the same list.", [EQ(["heap holds k heads", "pop min → push its successor"], ["c", "y"], size=54)]),
          S("The heap never holds more than k items, so each push and pop costs log k.", [EQ(["n pops × log k"], ["g"], size=70)]),
          S("Total time: n log k.", [EQ(["O(n log k)"], ["g"], size=100)])],
         "O(n log k)", "A min heap of the k heads."),

    prob(191, "Google", "SYSTEMS", "URL Shortener Six Characters", "How many links fit in 6 characters?",
         "How many different short links can six characters hold?", "URL SHORTENER",
         "A URL shortener uses six characters from a to z, A to Z, and zero to nine. How many distinct short links can it create?",
         [H("a–z, A–Z, 0–9"), ROW(["62 symbols", "6 positions"], cols={0: "y", 1: "c"}, w=330, h=120, size=48, y=640), F("how many links?", "y", 0.7)],
         [S("Each position can be any of sixty two symbols: twenty six plus twenty six plus ten.", [EQ(["26 + 26 + 10 = 62"], ["y"], size=70)]),
          S("Six positions, choices multiply.", [EQ(["62 × 62 × 62 × 62 × 62 × 62"], ["c"], size=54)]),
          S("That's sixty two to the sixth, about fifty seven billion.", [EQ(["62^6 = 56,800,235,584"], ["g"], size=60)]),
          S("Enough for years of links, even at a thousand per second.", [EQ(["≈ 1.8 years per 10^10 links"], ["c"], size=48)])],
         "56.8 BILLION", "About fifty seven billion links."),

    prob(192, "Meta", "SYSTEMS", "Unique IDs Across Servers", "Snowflake style 64 bit IDs",
         "Generate unique, time ordered IDs on many servers without a central counter.", "UNIQUE IDs\nACROSS SERVERS",
         "How do you generate unique, roughly time ordered ids on many servers without coordinating, using sixty four bits?",
         [H("no central counter"), ROW(["time", "machine", "sequence"], cols={0: "c", 1: "y", 2: "g"}, w=290, h=120, size=44, y=640), F("fit it in 64 bits", "y", 0.7)],
         [S("A single database counter is a bottleneck and a single point of failure. Instead pack information into the id itself.", [EQ(["central counter: slow, fragile"], ["r"], size=52)]),
          S("Use forty one bits for the timestamp in milliseconds, ten bits for the machine id, and twelve bits for a sequence number.", [EQ(["41 + 10 + 12 = 63 bits", "(+ 1 sign bit)"], ["y", "w"], size=60)]),
          S("Ids sort by time, machines never collide, and each machine can issue four thousand ninety six ids per millisecond.", [EQ(["2^12 = 4,096 per ms per machine"], ["g"], size=52)])],
         "TIME | MACHINE | SEQ", "Timestamp, machine and sequence bits."),

    prob(193, "Google", "SYSTEMS", "CAP Theorem In One Minute", "Partition, consistency, availability",
         "During a network failure, a database must choose. What exactly does it choose between?", "CAP\nTHEOREM",
         "What does the CAP theorem say a distributed database must choose between when the network partitions?",
         [H("C · A · P"), ROW(["Consistency", "Availability", "Partition tolerance"], cols={0: "c", 1: "y", 2: "r"}, w=300, h=120, size=34, y=640), F("what must give?", "y", 0.7)],
         [S("Partitions happen on real networks, so you can't give up partition tolerance. The real choice is made during a partition.", [EQ(["partition happens → choose C or A"], ["c"], size=52)]),
          S("Choose consistency: refuse some requests, so every answer is correct, but the system is unavailable to some users.", [EQ(["CP: correct, sometimes unavailable"], ["c"], size=50)]),
          S("Choose availability: keep answering from each side, accepting that replicas may disagree for a while.", [EQ(["AP: always answers, may be stale"], ["y"], size=50)])],
         "C OR A", "During a partition you choose consistency or availability."),

    prob(194, "Meta", "SQL", "Employees Earning More Than Their Manager", "A self join",
         "Find employees who earn more than their own manager.", "PAID MORE\nTHAN THE BOSS",
         "Given an employees table with id, salary and manager id, how do you list employees who earn more than their manager?",
         [H("employees(id, salary, manager_id)"), ROW(["employee", "→ manager"], cols={0: "c", 1: "y"}, w=300, h=120, size=48, y=640), F("earns more than the boss?", "y", 0.7)],
         [S("A manager is just another row in the same table. So join the table to itself.", [EQ(["employees e  JOIN  employees m"], ["c"], size=54)]),
          S("Match each employee's manager id to the manager's id.", [EQ(["ON e.manager_id = m.id"], ["y"], size=60)]),
          S("Then keep rows where the employee's salary is higher.", [EQ(["SELECT e.id FROM employees e", "JOIN employees m ON e.manager_id = m.id", "WHERE e.salary > m.salary;"], ["w", "c", "g"], size=44)])],
         "SELF JOIN", "Join the table to itself."),

    prob(195, "Meta", "SQL", "Delete Duplicate Rows Keep One", "Keep the smallest id",
         "Remove duplicate rows from a table, but keep one copy of each.", "DELETE THE\nDUPLICATES",
         "Given a table with id and email, how do you delete duplicate emails but keep the row with the smallest id?",
         [H("people(id, email)"), ROW(["1  a@x.com", "2  a@x.com", "3  b@x.com"], cols={1: "r"}, w=300, h=110, size=34, y=640), F("keep the smallest id", "y", 0.7)],
         [S("Selecting duplicates is easy with group by. Deleting needs to keep one of each group.", [EQ(["GROUP BY email → groups"], ["c"], size=54)]),
          S("Self join the table. Match rows with the same email where the other row has a smaller id.", [EQ(["p1.email = p2.email", "p1.id > p2.id"], ["y", "y"], size=60)]),
          S("Delete the larger id copies.", [EQ(["DELETE p1 FROM people p1", "JOIN people p2", "ON p1.email = p2.email AND p1.id > p2.id;"], ["r", "w", "w"], size=42)])],
         "DELETE LARGER IDs", "Self join and delete the larger ids."),

    prob(196, "Google", "SYSTEMS", "Race Condition On A Counter", "Why counter++ loses updates",
         "Two threads each add one to a counter, and the counter only goes up by one.", "LOST UPDATE",
         "Two threads each run counter plus plus on a shared counter starting at five. Why might it end at six, not seven, and how do you fix it?",
         [H("counter = 5"), ROW(["thread A", "thread B"], cols={0: "c", 1: "y"}, w=300, h=120, size=48, y=640), F("why 6 instead of 7?", "y", 0.7)],
         [S("Counter plus plus is really three steps: read, add one, write back.", [EQ(["read → add → write"], ["c"], size=64)]),
          S("If both threads read five before either writes, both compute six, and both write six.", [EQ(["A reads 5", "B reads 5", "A writes 6", "B writes 6"], ["c", "y", "c", "y"], size=46)]),
          S("One update is lost. The fix is to make the three steps indivisible.", [EQ(["lock, or atomic increment"], ["g"], size=60)])],
         "ATOMIC INCREMENT", "Use a lock or an atomic increment."),

    prob(197, "Meta", "COMPLEXITY", "Hash Map Lookup Worst Case", "O(1) on average, O(n) at worst",
         "A hash map lookup is called constant time. When is it not?", "IS A HASH MAP\nREALLY O(1)?",
         "A hash map lookup is O(1) on average. Under what conditions does it become O(n)?",
         [H("hash(key) → bucket"), ROW(["good: 1 per bucket", "bad: all in one"], cols={0: "g", 1: "r"}, w=400, h=120, size=36, y=640), F("when is it slow?", "y", 0.7)],
         [S("Lookup hashes the key to a bucket, then searches inside that bucket.", [EQ(["hash → bucket → search"], ["c"], size=58)]),
          S("With a good hash function and a bounded load factor, buckets hold very few items. Lookup is constant.", [EQ(["load factor ≤ 0.75 → O(1)"], ["g"], size=54)]),
          S("If many keys collide into one bucket, that bucket becomes a long list, and lookup scans it.", [EQ(["all keys collide → O(n)"], ["r"], size=58)]),
          S("Attackers can craft colliding keys. Modern maps randomise the hash or turn long buckets into trees.", [EQ(["randomised hash / tree buckets"], ["y"], size=52)])],
         "O(n) WORST CASE", "Average constant, worst case linear."),

    prob(198, "Amazon", "SYSTEMS", "Idempotency Key For Payments", "Retries must not double charge",
         "A payment request times out and the client retries. How do you avoid charging twice?", "DON'T CHARGE\nTWICE",
         "A payment request times out, and the client retries. How do you make sure the customer isn't charged twice?",
         [H("charge $50 → timeout → retry"), ROW(["request 1", "retry"], cols={0: "c", 1: "y"}, w=300, h=120, size=48, y=640), F("charge exactly once", "y", 0.7)],
         [S("You can't know if the first request succeeded. Retrying blindly might charge twice, but not retrying might lose the payment.", [EQ(["unknown outcome → retry unsafe"], ["r"], size=52)]),
          S("Give each payment a unique idempotency key, generated by the client, and send it with every attempt.", [EQ(["key = 7f3a-..."], ["y"], size=70)]),
          S("The server stores the key with the result. A repeated key returns the stored result, with no second charge.", [EQ(["seen key → return stored result"], ["g"], size=54)])],
         "IDEMPOTENCY KEY", "A unique key per payment makes retries safe."),

    prob(199, "Google", "ALGORITHMS", "Three Sum To Zero", "Sort, then two pointers",
         "Find all triples in an array that add up to zero, without duplicates.", "THREE NUMBERS\nSUM TO ZERO",
         "Given minus one, zero, one, two, minus one, minus four, find all unique triples that sum to zero.",
         [H("[−1, 0, 1, 2, −1, −4]"), ROW([-1, 0, 1, 2, -1, -4], w=120, h=110, size=54, y=640), F("unique triples summing to 0?", "y", 0.7)],
         [S("Checking every triple is cubic. Sorting first lets two pointers do the work.", [EQ(["triples: O(n³)"], ["r"], size=64)]),
          S("Sort: minus four, minus one, minus one, zero, one, two. Fix the first number, and scan the rest with two pointers.", [ROW([-4, -1, -1, 0, 1, 2], w=120, h=110, size=54, y=640)]),
          S("If the sum is too small, move the left pointer up. Too big, move the right pointer down. Skip repeated values.", [EQ(["sum < 0 → left++", "sum > 0 → right−−"], ["c", "y"], size=58)]),
          S("The triples are minus one, minus one, two, and minus one, zero, one.", [EQ(["[−1, −1, 2]", "[−1, 0, 1]"], ["g", "g"], size=70)])],
         "2 TRIPLES", "Two triples, in quadratic time."),

    prob(200, "Amazon", "ALGORITHMS", "Is One String A Rotation Of Another", "A one line trick",
         "Is erbottlewat a rotation of waterbottle? There's a one line check.", "STRING\nROTATION?",
         "How do you check whether one string is a rotation of another, using only a substring check?",
         [H("waterbottle  vs  erbottlewat"), ROW(["waterbottle", "erbottlewat"], cols={0: "c", 1: "y"}, w=400, h=120, size=40, y=640), F("is it a rotation?", "y", 0.7)],
         [S("You could try every rotation, which is quadratic. There's a neat trick.", [EQ(["try every shift: O(n²)"], ["r"], size=60)]),
          S("Write the first string twice. Every rotation of it appears as a substring of the doubled string.", [EQ(["waterbottle waterbottle"], ["c"], size=60)]),
          S("Look for the second string inside. Erbottlewat appears starting at the third letter.", [EQ(["wat|erbottlewat|erbottle"], ["g"], size=52)]),
          S("Also check the lengths are equal. Then it's one substring search.", [EQ(["len(a) == len(b) and b in a + a"], ["g"], size=50)])],
         "b IN a + a", "Yes, b is in a plus a."),
]
