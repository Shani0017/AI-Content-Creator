"""Brain Massage batch 3: 100 new reels in the new formats (ids 201-300).  Every answer is computed (code is executed, SQL is run in sqlite,
simulations are run), nothing is typed by hand where it can be computed.
30 guess-the-output | 15 spot-the-bug | 10 SQL | 10 Fermi estimates | 15 A-or-B quizzes | 10 behavioural | 10 live simulations"""
import contextlib
import io
import math
import random
import re
import sqlite3

PROBLEMS = []
_id = [200]


def nid():
    _id[0] += 1
    return _id[0]


def sp(s):
    """text -> something the voice reads naturally"""
    s = str(s).replace("\n", ", ")
    s = re.sub(r"[\[\](){}'\"<>]", " ", s)
    s = s.replace("_", " ").replace("#", "")
    return re.sub(r"\s+", " ", s).strip()


def esize(lines):
    m = max(len(x) for x in lines)
    return 54 if m <= 22 else (46 if m <= 28 else (40 if m <= 34 else 34))


def run_py(code):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<snippet>", "exec"), {})
    except Exception as e:
        return type(e).__name__
    return buf.getvalue().strip()


# ------------------------------------------------------------------ 1) guess the output (30)
def guess(topic, code, hint, why1, why2, trace):
    out = run_py(code)
    lines = code.strip("\n").split("\n")
    shown = out.replace("\n", "  /  ")
    PROBLEMS.append(dict(
        id=nid(), org="Python", tag="PYTHON", title=f"Guess The Output {topic}", sub="what does it print?",
        hook_say="Python interview question. What does this code print? You have five seconds.",
        hook_text="WHAT DOES\nTHIS PRINT?", hook_sub=hint,
        q=f"Python, {topic.lower()}. Look at the code on screen. What does it print? Take five seconds to think.",
        qparts=[dict(k="head", text="Python", col="c"),
                dict(k="eq", lines=lines, cols=["w"] * (len(lines) - 1) + ["y"], y=690, size=esize(lines)),
                dict(k="foot", text="what does it print?", col="y", at=0.7)],
        steps=[dict(say=why1, parts=[dict(k="head", text="think it through", col="c"),
                                     dict(k="eq", lines=trace, cols=["c"] * (len(trace) - 1) + ["y"], y=690, size=esize(trace))]),
               dict(say=why2, parts=[dict(k="head", text="so it prints", col="c"),
                                     dict(k="big", text=shown if len(shown) < 26 else shown[:26], col="g", size=92, y=690)])],
        ans=shown[:24], ans_say=f"It prints {sp(out)}."))


GUESS = [
    ("Float Equality", "print(0.1 + 0.2 == 0.3)", "looks obviously true",
     "Computers store decimals in binary, and zero point one cannot be stored exactly.",
     "So zero point one plus zero point two lands a hair above zero point three, and the comparison is false.",
     ["0.1 + 0.2 = 0.30000000000000004", "0.3 is stored as 0.29999999999999998", "not equal"]),
    ("Mutable Default", "def add(x, l=[]):\n    l.append(x)\n    return l\nadd(1)\nprint(add(2))", "the list remembers",
     "The default list is created once, when the function is defined, not on every call.",
     "So the second call reuses the same list, which already holds one.",
     ["l = [] is made once", "add(1) gives [1]", "add(2) gives [1, 2]"]),
    ("Unique Letters", 'print(len(set("mississippi")))', "count the letters",
     "A set keeps every different letter just once.",
     "Mississippi only uses the letters m, i, s and p.",
     ["m i s s i s s i p p i", "unique: m  i  s  p", "4 letters"]),
    ("Truthy String", 'print(bool("False"))', "read it carefully",
     "Any string that is not empty counts as true, whatever it says.",
     "Only the empty string is false. So this is true.",
     ['"False" is not empty', "non-empty string means True"]),
    ("Banker Rounding", "print(round(2.5), round(3.5))", "half up, right?",
     "Python rounds halves to the nearest even number. That is called bankers rounding.",
     "So two point five goes down to two, and three point five goes up to four.",
     ["2.5 -> nearest even = 2", "3.5 -> nearest even = 4"]),
    ("Floor Division", "print(10 // 3, -10 // 3)", "watch the minus sign",
     "Floor division rounds down toward minus infinity, not toward zero.",
     "Ten over three is three point three, which floors to three. Minus three point three floors to minus four.",
     ["10 / 3 = 3.33  floors to 3", "-10 / 3 = -3.33  floors to -4"]),
    ("Sum Of Lists", "print(sum([[1, 2], [3]], []))", "sum with a twist",
     "The second argument is the starting value, and here it is an empty list.",
     "Adding lists joins them, so sum flattens one level.",
     ["start: []", "[] + [1, 2] = [1, 2]", "[1, 2] + [3] = [1, 2, 3]"]),
    ("One And One Point Zero", 'd = {}\nd[1] = "a"\nd[1.0] = "b"\nprint(len(d))', "how many keys?",
     "One and one point zero are equal, and they hash the same.",
     "So the second assignment overwrites the first. There is just one key.",
     ["1 == 1.0  is True", "same hash, same key", "d = {1: 'b'}"]),
    ("Remove While Looping", "lst = [1, 2, 2, 3]\nfor x in lst:\n    if x == 2:\n        lst.remove(x)\nprint(lst)", "all the twos are gone?",
     "Removing items while looping shifts the list under the iterator.",
     "After the first two is removed, the loop skips the next item, which is the second two.",
     ["remove the first 2", "list shifts left", "the next 2 is skipped"]),
    ("Chained Comparison", "print(1 in [1, 2] == True)", "no brackets",
     "Python chains comparisons. This reads as one in the list, and the list equals true.",
     "The list is not equal to true, so the whole thing is false.",
     ["1 in [1, 2]  and  [1, 2] == True", "True and False"]),
    ("Finally Always Runs", 'def f():\n    try:\n        return "try"\n    finally:\n        print("finally")\nprint(f())', "which prints first?",
     "The finally block always runs, even after a return.",
     "So finally prints first, and then the returned value is printed.",
     ["return 'try' is queued", "finally runs: prints finally", "then print shows try"]),
    ("Empty All", "print(all([]))", "all of nothing",
     "All means no item is false.",
     "An empty list has no false items, so the answer is true.",
     ["any false item?  none", "so all() is True"]),
    ("Tuple With A List", "t = (1, [2, 3])\nt[1].append(4)\nprint(t)", "tuples are immutable",
     "A tuple cannot change which objects it holds.",
     "But the list inside is still a normal list, and it can grow.",
     ["t holds 1 and a list", "the list grows to [2, 3, 4]"]),
    ("Local Variable Trap", "x = 5\ndef f():\n    print(x)\n    x = 6\nf()", "x is five",
     "Assigning to x anywhere inside a function makes x local for the whole function.",
     "So the print runs before x has a value, and Python raises an error.",
     ["x = 6 makes x local", "print(x) comes first", "x has no value yet"]),
    ("Plus Signs", 'print("5" + "5", int("5") + int("5"))', "two kinds of plus",
     "Plus joins strings and adds numbers.",
     "So the two strings join into fifty five, and the two numbers add to ten.",
     ['"5" + "5" = "55"', "5 + 5 = 10"]),
    ("Divmod", "print(divmod(17, 5))", "two answers at once",
     "Divmod returns the quotient and the remainder together.",
     "Seventeen divided by five is three, with two left over.",
     ["17 // 5 = 3", "17 % 5 = 2"]),
    ("Bool Is An Int", "print(isinstance(True, int))", "is a bool a number?",
     "In Python, bool is a subclass of int.",
     "True is really the number one, so the answer is true.",
     ["True == 1", "bool inherits from int"]),
    ("Accented Letters", 'print(len("héllo"))', "characters or bytes?",
     "In Python three, strings are sequences of characters, not bytes.",
     "The accented e counts as one character, so the length is five.",
     ["h  é  l  l  o", "5 characters"]),
    ("Sorting Letters", 'print(sorted("bAc"))', "capital letters",
     "Strings sort by character code, and capital letters come before lowercase ones.",
     "So the capital A goes first, then b, then c.",
     ["A = 65, b = 98, c = 99", "sorted by code"]),
    ("Map And Filter", "print(list(map(lambda x: x * 2, filter(lambda x: x % 2, range(6)))))", "read it inside out",
     "Filter keeps the odd numbers from zero to five, which are one, three and five.",
     "Map then doubles each one.",
     ["range(6): 0 1 2 3 4 5", "odd only: 1 3 5", "doubled: 2 6 10"]),
    ("Reverse And Shout", 'print("Hello"[::-1].upper())', "slice then upper",
     "Slicing with minus one steps backwards, so Hello becomes olleH.",
     "Then upper makes every letter a capital.",
     ['"Hello"[::-1] = "olleH"', ".upper() = OLLEH"]),
    ("Plus Equals Versus Plus", "a = [1, 2]\nb = a\nb = b + [3]\nprint(a)", "b changed, a?",
     "The plus operator builds a brand new list, and b now points at it.",
     "The name a still points at the original list, which never changed.",
     ["b + [3] makes a new list", "b points to the new one", "a is untouched"]),
    ("Truncate Versus Floor", "print(int(-3.9), -3.9 // 1)", "toward zero or down?",
     "Int cuts off the decimals, which moves toward zero.",
     "Floor division always goes down, so it gives minus four.",
     ["int(-3.9) = -3", "-3.9 // 1 = -4.0"]),
    ("Shared Rows", "x = [[0] * 2] * 2\nx[0][0] = 1\nprint(x)", "change one cell",
     "Multiplying a list repeats the same inner list, not copies of it.",
     "Both rows are the very same list, so changing one changes both.",
     ["[[0, 0]] * 2: one list, two names", "x[0][0] = 1 changes it for both"]),
    ("Any And All", "print(any([]), all([]))", "empty lists again",
     "Any needs at least one true item, and an empty list has none.",
     "All needs no false items, and an empty list has none. So false, then true.",
     ["any([]): no true item  False", "all([]): no false item  True"]),
    ("Capital Letters Compare", 'print(max("apple", "Zebra"))', "alphabetical?",
     "Strings compare by character code, and lowercase letters have bigger codes than capitals.",
     "So the lowercase a beats the capital Z.",
     ["a = 97", "Z = 90", "apple wins"]),
    ("String Math", 's = "abc"\nprint(s * 2 + s[-1])', "multiply a string",
     "Multiplying a string repeats it, so abc times two is abcabc.",
     "The last character is c, and it gets added at the end.",
     ['"abc" * 2 = "abcabc"', 's[-1] = "c"']),
    ("Args And Kwargs", "def f(*a, **k):\n    print(len(a), len(k))\nf(1, 2, x=3)", "count them",
     "Star args collects the extra positional arguments, here one and two.",
     "Double star collects the keyword arguments, here just x.",
     ["*a = (1, 2)", "**k = {'x': 3}"]),
    ("None Is Not False", "print(type(None).__name__, None == False)", "falsy is not equal",
     "None has its own type, called NoneType.",
     "None is falsy, but it is not equal to false.",
     ["type(None) = NoneType", "None == False  is False"]),
    ("While Else", 'i = 0\nwhile i < 3:\n    i += 1\nelse:\n    print("done", i)', "else on a loop",
     "The else block of a loop runs when the loop ends without a break.",
     "There is no break here, so it prints done and the final value of i.",
     ["loop ends normally", "else runs", "i is 3"]),
]
for g in GUESS:
    guess(*g)


# ------------------------------------------------------------------ 2) spot the bug (15)
def spot(title, code, bug, fail, why1, fix, why2, hint="it looks fine"):
    lines = code
    cols_q = ["w"] * len(lines)
    cols_bug = ["w"] * len(lines)
    for b in bug:
        cols_bug[b] = "r"
    PROBLEMS.append(dict(
        id=nid(), org="Code", tag="DEBUGGING", title=f"Spot The Bug {title}", sub="find the bug in 10 seconds",
        hook_say="Spot the bug. This code looks perfect. It is not. Can you find the problem?",
        hook_text="SPOT\nTHE BUG", hook_sub=hint,
        q=f"Look at the code on screen. {title}. Where is the bug?",
        qparts=[dict(k="head", text="find the bug", col="c"),
                dict(k="eq", lines=lines, cols=cols_q, y=700, size=esize(lines)),
                dict(k="foot", text="which line is wrong?", col="y", at=0.7)],
        steps=[dict(say=why1, stamp="WRONG",
                    parts=[dict(k="head", text=fail, col="y"),
                           dict(k="eq", lines=lines, cols=cols_bug, y=700, size=esize(lines))]),
               dict(say=why2, parts=[dict(k="head", text="the fix", col="g"),
                                     dict(k="eq", lines=[fix], cols=["g"], y=640, size=esize([fix])),
                                     dict(k="foot", text="bug fixed", col="g", at=0.7)])],
        ans=fix[:24], ans_say="That is the bug, and that is the fix."))


SPOT = [
    ("Biggest Number", ["def biggest(nums):", "    top = 0", "    for n in nums:", "        if n > top:", "            top = n", "    return top"], [1],
     "nums = [-4, -7, -1]", "Try a list of only negative numbers. Nothing beats zero, so it returns zero, which is not even in the list.",
     "top = nums[0]", "Start from the first element of the data, never from zero."),
    ("Shared Box", ["def add_item(x, box=[]):", "    box.append(x)", "    return box"], [0],
     "every call shares one list", "The default list is created once, so every call that skips the argument shares and grows the same list.",
     "box=None", "Use none as the default, and create a new list inside the function."),
    ("Binary Search", ["lo, hi = 0, len(a) - 1", "while lo <= hi:", "    mid = (lo + hi) / 2", "    if a[mid] == t:", "        return mid"], [2],
     "TypeError: index must be int", "Slash is true division, so mid is a float, and a list cannot be indexed with a float.",
     "mid = (lo + hi) // 2", "Use double slash for integer division."),
    ("Forever Loop", ["i = 0", "while i < 5:", "    print(i)"], [1],
     "never stops", "Nothing changes i inside the loop, so the condition is true forever.",
     "i += 1", "Add the increment inside the loop."),
    ("Text Numbers", ["a = '10'", "b = '9'", "print(a > b)"], [0, 1],
     "prints False", "These are strings, and strings compare character by character. The character one comes before nine.",
     "int(a) > int(b)", "Convert to numbers before comparing."),
    ("Skipping Items", ["for x in nums:", "    if x < 0:", "        nums.remove(x)"], [2],
     "some negatives survive", "Removing from a list while looping over it makes the loop skip the next item.",
     "nums = [x for x in nums if x >= 0]", "Build a new list instead of editing the one you loop over."),
    ("Same Row Three Times", ["grid = [[0] * 3] * 3", "grid[0][0] = 1"], [0],
     "all three rows change", "The multiplication repeats one inner list, so all three rows are the same list.",
     "[[0] * 3 for _ in range(3)]", "Use a comprehension so every row is its own list."),
    ("Point One Plus Point Two", ["total = 0.1 + 0.2", "if total == 0.3:", "    print('equal')"], [1],
     "never prints", "Binary floats are not exact, so the sum is a tiny bit above zero point three.",
     "abs(total - 0.3) < 1e-9", "Compare floats with a small tolerance."),
    ("Factorial", ["def fact(n):", "    return n * fact(n - 1)"], [1],
     "RecursionError", "There is no base case, so the function calls itself forever until the stack overflows.",
     "if n <= 1: return 1", "Add a base case that stops the recursion."),
    ("Lambda Loop", ["funcs = []", "for i in range(3):", "    funcs.append(lambda: i)", "print(funcs[0]())"], [2],
     "prints 2, not 0", "The lambda looks up i when it is called, by then the loop has finished and i is two.",
     "lambda i=i: i", "Bind the current value as a default argument."),
    ("Word Counter", ["counts = {}", "for w in words:", "    counts[w] += 1"], [2],
     "KeyError on the first word", "A new word is not in the dictionary yet, so adding to it fails.",
     "counts.get(w, 0) + 1", "Use get with a default of zero."),
    ("Shadowed Name", ["list = [1, 2, 3]", "print(list('abc'))"], [0],
     "TypeError: list is not callable", "Naming a variable list hides the built-in list function.",
     "rename the variable", "Never reuse the names of built-ins."),
    ("Changing A String", ["s = 'hello'", "s[0] = 'H'"], [1],
     "TypeError: no item assignment", "Strings are immutable, so you cannot change a character in place.",
     "s = 'H' + s[1:]", "Build a new string instead."),
    ("Missing First Item", ["total = 0", "for i in range(1, len(a)):", "    total += a[i]"], [1],
     "always short by a[0]", "Range starts at one, so the first element is never added.",
     "range(len(a))", "Start at zero, or loop over the items directly."),
    ("Average Of Nothing", ["def average(nums):", "    return sum(nums) / len(nums)", "print(average([]))"], [1],
     "ZeroDivisionError", "An empty list has length zero, and dividing by zero raises an error.",
     "if not nums: return 0", "Handle the empty list first."),
]
for s_ in SPOT:
    spot(*s_)


# ------------------------------------------------------------------ 3) SQL (10)
def table_cells(rows, per):
    return ["\n".join(str(c) for c in r) for r in rows]


def sql_item(title, hook, schema, inserts, query, cols_hdr, shown_rows, q_say, steps, ans_rows_expected, ans_text, ans_say, lines):
    con = sqlite3.connect(":memory:")
    con.executescript(schema + inserts)
    res = [tuple(r) for r in con.execute(query).fetchall()]
    assert res == ans_rows_expected, (title, res, ans_rows_expected)
    cells = table_cells(shown_rows, len(shown_rows[0]))
    rcells = ["\n".join(str(c) for c in r) for r in res] or ["none"]
    per = min(5, len(cells))
    PROBLEMS.append(dict(
        id=nid(), org="SQL", tag="SQL", title=title, sub="SQL in 30 seconds",
        hook_say="SQL interview question. Can you write the query?", hook_text=hook, hook_sub="watch what the rows do",
        q=q_say,
        qparts=[dict(k="head", text=cols_hdr, col="c"),
                dict(k="row", items=cells, per=per, y=650, w=170, h=104, size=34, dur=0.45),
                dict(k="foot", text="write the query", col="y", at=0.7)],
        steps=[dict(say=steps[0], parts=[dict(k="head", text="the query", col="c"),
                                         dict(k="eq", lines=lines, cols=["c"] * len(lines), y=690, size=esize(lines))]),
               dict(say=steps[1], parts=[dict(k="head", text="the result", col="g"),
                                         dict(k="row", items=rcells, per=min(5, len(rcells)), y=650, w=190, h=110, size=40, hl=list(range(len(rcells))),
                                              cols={i: "g" for i in range(len(rcells))}, dur=0.5)])],
        ans=ans_text, ans_say=ans_say))


sql_item("Second Highest Salary 3000 To 8000", "2nd HIGHEST\nSALARY",
         "CREATE TABLE emp(name TEXT, salary INT);", "INSERT INTO emp VALUES('Ann',3000),('Bob',8000),('Cy',5500),('Di',8000),('Ed',6500);",
         "SELECT DISTINCT salary FROM emp ORDER BY salary DESC LIMIT 1 OFFSET 1", "emp  (name, salary)",
         [("Ann", 3000), ("Bob", 8000), ("Cy", 5500), ("Di", 8000), ("Ed", 6500)],
         "The table has five salaries. Return the second highest. Eight thousand appears twice.",
         ["Select the distinct salaries, order them from high to low, skip one row and take the next.", "Eight thousand is skipped, so the answer is six thousand five hundred."],
         [(6500,)], "6500", "Six thousand five hundred.",
         ["SELECT DISTINCT salary", "FROM emp", "ORDER BY salary DESC", "LIMIT 1 OFFSET 1"])
sql_item("Customers With No Orders", "NO ORDERS?\nFIND THEM",
         "CREATE TABLE c(id INT, name TEXT); CREATE TABLE o(cust_id INT);", "INSERT INTO c VALUES(1,'Ann'),(2,'Bob'),(3,'Cy'); INSERT INTO o VALUES(1),(1),(3);",
         "SELECT c.name FROM c LEFT JOIN o ON o.cust_id = c.id WHERE o.cust_id IS NULL", "customers  +  orders",
         [("Ann", 1), ("Bob", 2), ("Cy", 3), ("order", 1), ("order", 1), ("order", 3)],
         "Customers Ann, Bob and Cy. Orders belong to customer one, one and three. Which customers never ordered?",
         ["Left join orders onto customers, then keep the rows where the order side is null.", "Only Bob has no order."],
         [("Bob",)], "Bob", "Bob.",
         ["SELECT c.name", "FROM c LEFT JOIN o", "ON o.cust_id = c.id", "WHERE o.cust_id IS NULL"])
sql_item("Earns More Than The Manager", "EARNS MORE\nTHAN BOSS",
         "CREATE TABLE e(name TEXT, salary INT, mgr TEXT);", "INSERT INTO e VALUES('Ann',9000,NULL),('Bob',7000,'Ann'),('Cy',9500,'Ann'),('Di',6000,'Bob');",
         "SELECT w.name FROM e w JOIN e m ON w.mgr = m.name WHERE w.salary > m.salary", "e  (name, salary, boss)",
         [("Ann", 9000, "-"), ("Bob", 7000, "Ann"), ("Cy", 9500, "Ann"), ("Di", 6000, "Bob")],
         "Find the employees who earn more than their own manager.",
         ["Join the table to itself, matching each worker to their manager, then compare the two salaries.", "Only Cy earns more than the boss."],
         [("Cy",)], "Cy", "Cy.",
         ["SELECT w.name", "FROM e w JOIN e m", "ON w.mgr = m.name", "WHERE w.salary > m.salary"])
sql_item("Find Duplicate Emails", "FIND THE\nDUPLICATES",
         "CREATE TABLE u(email TEXT);", "INSERT INTO u VALUES('a@x'),('b@x'),('a@x'),('c@x');",
         "SELECT email FROM u GROUP BY email HAVING COUNT(*) > 1", "u  (email)",
         [("a@x",), ("b@x",), ("a@x",), ("c@x",)],
         "A table of emails. Find the emails that appear more than once.",
         ["Group by email, then keep only the groups with a count above one.", "Only a at x appears twice."],
         [("a@x",)], "a@x", "A at x.",
         ["SELECT email", "FROM u", "GROUP BY email", "HAVING COUNT(*) > 1"])
sql_item("Top Earner Per Department", "TOP EARNER\nPER DEPT",
         "CREATE TABLE e(name TEXT, dept TEXT, pay INT);", "INSERT INTO e VALUES('Ann','eng',9),('Bob','eng',7),('Cy','ops',5),('Di','ops',6);",
         "SELECT name FROM (SELECT name, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY pay DESC) r FROM e) WHERE r = 1 ORDER BY name", "e  (name, dept, pay)",
         [("Ann", "eng", 9), ("Bob", "eng", 7), ("Cy", "ops", 5), ("Di", "ops", 6)],
         "Return the best paid person in each department.",
         ["Number the people inside each department from the highest pay, and keep number one.", "Ann leads engineering and Di leads operations."],
         [("Ann",), ("Di",)], "Ann + Di", "Ann and Di.",
         ["ROW_NUMBER() OVER (", "  PARTITION BY dept", "  ORDER BY pay DESC)", "keep row 1"])
sql_item("Running Total", "RUNNING\nTOTAL",
         "CREATE TABLE s(day INT, amt INT);", "INSERT INTO s VALUES(1,10),(2,20),(3,5),(4,15);",
         "SELECT SUM(amt) OVER (ORDER BY day) FROM s ORDER BY day", "s  (day, amount)",
         [(1, 10), (2, 20), (3, 5), (4, 15)],
         "Sales per day are ten, twenty, five and fifteen. Return the running total.",
         ["Use a window sum ordered by day, so each row adds everything up to itself.", "The totals are ten, thirty, thirty five and fifty."],
         [(10,), (30,), (35,), (50,)], "10 30 35 50", "Ten, thirty, thirty five, fifty.",
         ["SELECT SUM(amt)", "  OVER (ORDER BY day)", "FROM s"])
sql_item("Customers With Two Or More Orders", "2 OR MORE\nORDERS",
         "CREATE TABLE o(cust TEXT);", "INSERT INTO o VALUES('Ann'),('Ann'),('Bob'),('Cy'),('Ann'),('Cy');",
         "SELECT cust, COUNT(*) FROM o GROUP BY cust HAVING COUNT(*) >= 2 ORDER BY cust", "o  (customer)",
         [("Ann",), ("Ann",), ("Bob",), ("Cy",), ("Ann",), ("Cy",)],
         "Six orders from three customers. Who has placed two or more orders?",
         ["Group by customer and keep the groups with a count of at least two.", "Ann has three orders and Cy has two."],
         [("Ann", 3), ("Cy", 2)], "Ann 3, Cy 2", "Ann with three, and Cy with two.",
         ["SELECT cust, COUNT(*)", "FROM o", "GROUP BY cust", "HAVING COUNT(*) >= 2"])
sql_item("Pass And Fail Counts", "PASS VS\nFAIL",
         "CREATE TABLE r(score INT);", "INSERT INTO r VALUES(40),(75),(90),(30),(60);",
         "SELECT SUM(CASE WHEN score >= 50 THEN 1 ELSE 0 END), SUM(CASE WHEN score < 50 THEN 1 ELSE 0 END) FROM r", "r  (score)  pass mark 50",
         [(40,), (75,), (90,), (30,), (60,)],
         "Scores forty, seventy five, ninety, thirty and sixty. Pass mark is fifty. Count the passes and the fails in one query.",
         ["Use case when inside a sum, one for each outcome.", "Three passed and two failed."],
         [(3, 2)], "3 PASS  2 FAIL", "Three passed and two failed.",
         ["SUM(CASE WHEN score >= 50", "     THEN 1 ELSE 0 END)", "SUM(CASE WHEN score < 50", "     THEN 1 ELSE 0 END)"])
sql_item("Keep The Lowest Id", "DELETE THE\nDUPLICATES",
         "CREATE TABLE d(id INT, email TEXT);", "INSERT INTO d VALUES(1,'a'),(2,'a'),(3,'b'),(4,'a');",
         "SELECT id FROM d WHERE id IN (SELECT MIN(id) FROM d GROUP BY email) ORDER BY id", "d  (id, email)",
         [(1, "a"), (2, "a"), (3, "b"), (4, "a")],
         "Delete the duplicate emails but keep the row with the lowest id for each email. Which ids survive?",
         ["Group by email, take the minimum id of each group, and keep only those ids.", "Ids one and three survive."],
         [(1,), (3,)], "ids 1 and 3", "Ids one and three survive.",
         ["keep id IN (", "  SELECT MIN(id) FROM d", "  GROUP BY email)"])
sql_item("Above The Average Salary", "ABOVE THE\nAVERAGE",
         "CREATE TABLE e(salary INT);", "INSERT INTO e VALUES(3000),(4000),(5000),(8000);",
         "SELECT salary FROM e WHERE salary > (SELECT AVG(salary) FROM e)", "e  (salary)",
         [(3000,), (4000,), (5000,), (8000,)],
         "Salaries are three thousand, four thousand, five thousand and eight thousand. Return the salaries above the average.",
         ["Compute the average in a subquery, then keep the salaries above it. The average is five thousand.", "Five thousand is not above itself, so only eight thousand remains."],
         [(8000,)], "8000", "Eight thousand.",
         ["SELECT salary FROM e", "WHERE salary >", "  (SELECT AVG(salary)", "   FROM e)"])


# ------------------------------------------------------------------ 4) Fermi estimates (10)
def fmt(x):
    if x >= 1000 or x == int(x):
        return f"{x:,.0f}"
    return f"{x:g}"


def fermi(title, hook, q_say, base, base_unit, ops, ans_text, ans_say):
    """ops: (kind, factor, say_phrase, unit_after)"""
    steps = []
    cur = base
    cur_unit = base_unit
    for kind, f, phrase, unit in ops:
        new = cur * f if kind == "mul" else cur / f
        sym = "x" if kind == "mul" else "÷"
        ftxt = fmt(f) if f >= 1 else f"{f:g}"
        steps.append(dict(
            say=f"{phrase}. That gives {fmt(new)} {unit}.",
            parts=[dict(k="head", text=f"{cur_unit}  →  {unit}", col="c"),
                   dict(k="eq", lines=[f"{fmt(cur)} {cur_unit}", f"{sym} {ftxt}", f"= {fmt(new)} {unit}"], cols=["w", "w", "g"], y=690, size=48)]))
        cur, cur_unit = new, unit
    PROBLEMS.append(dict(
        id=nid(), org="Estimation", tag="FERMI", title=title, sub="estimate it in 30 seconds",
        hook_say="Famous interview question. No data, no google. Estimate the answer by breaking it into steps.",
        hook_text=hook, hook_sub="no google allowed",
        q=q_say,
        qparts=[dict(k="big", text="?", col="y", size=150, y=640, sub=title.replace(" Estimate", "")), dict(k="foot", text="break it into steps", col="c", at=0.7)],
        steps=steps, ans=ans_text, ans_say=ans_say))


fermi("Golf Balls In A School Bus", "GOLF BALLS\nIN A BUS", "How many golf balls fit inside a school bus? Break it into steps.",
      50, "cubic metres", [("mul", 1000, "One cubic metre is a thousand litres", "litres"), ("div", 0.04, "A golf ball takes about four hundredths of a litre", "balls"),
                           ("mul", 0.64, "Balls only fill about sixty four percent of the space", "balls that fit")],
      "≈ 800,000", "About eight hundred thousand golf balls.")
fermi("Heartbeats In A Lifetime", "HEARTBEATS\nIN A LIFE", "How many times does a heart beat in a lifetime? Break it into steps.",
      70, "beats a minute", [("mul", 60, "Sixty minutes in an hour", "beats an hour"), ("mul", 24, "Twenty four hours a day", "beats a day"),
                             ("mul", 365, "Three hundred and sixty five days a year", "beats a year"), ("mul", 80, "Eighty years of life", "beats in a lifetime")],
      "≈ 3 billion", "About three billion heartbeats.")
fermi("Pizzas Eaten In The US", "PIZZAS IN\nTHE US", "How many pizzas do Americans eat in a year? Break it into steps.",
      330_000_000, "people", [("mul", 12, "Say each person eats about one pizza a month, that is twelve a year", "pizzas a year")],
      "≈ 4 billion", "About four billion pizzas a year.")
fermi("Petrol Stations In Malaysia", "PETROL STATIONS\nIN MALAYSIA", "How many petrol stations are there in Malaysia? Break it into steps.",
      34_000_000, "people", [("div", 2, "About two people per vehicle", "vehicles"), ("mul", 52, "Each vehicle fills up about once a week, fifty two times a year", "fill ups a year"),
                             ("div", 365_000, "One station serves about a thousand fill ups a day, that is three hundred and sixty five thousand a year", "stations")],
      "≈ 2,400", "About two thousand four hundred petrol stations.")
fermi("Ping Pong Balls In A 747", "PING PONG BALLS\nIN A 747", "How many ping pong balls fit inside a Boeing seven forty seven? Break it into steps.",
      900, "cubic metres", [("mul", 1000, "A thousand litres in a cubic metre", "litres"), ("div", 0.0335, "A ping pong ball is about three hundredths of a litre", "balls"),
                            ("mul", 0.64, "Packing wastes about a third of the space", "balls that fit")],
      "≈ 17 million", "About seventeen million.")
fermi("Piano Tuners In Chicago", "PIANO TUNERS\nIN CHICAGO", "How many piano tuners work in Chicago? Break it into steps.",
      3_000_000, "people", [("div", 3, "About three people per household", "households"), ("div", 20, "One household in twenty owns a piano", "pianos"),
                            ("div", 1000, "One tuner can tune about a thousand pianos a year", "tuners")],
      "≈ 50", "About fifty piano tuners.")
fermi("Windows In Manhattan", "WINDOWS IN\nMANHATTAN", "How many windows are there in Manhattan? Break it into steps.",
      1_600_000, "residents", [("div", 2.5, "About two and a half people per apartment", "apartments"), ("mul", 5, "Five windows per apartment", "home windows"),
                               ("mul", 1.5, "Add half again for offices and shops", "windows")],
      "≈ 5 million", "About five million windows.")
fermi("Water Drunk In A Lifetime", "WATER IN\nA LIFETIME", "How much water does a person drink in a lifetime? Break it into steps.",
      2, "litres a day", [("mul", 365, "Three hundred and sixty five days", "litres a year"), ("mul", 80, "Eighty years", "litres in a lifetime")],
      "≈ 58,000 L", "About fifty eight thousand litres.")
fermi("Words In A Novel", "WORDS IN\nA NOVEL", "How many words are in a typical novel? Break it into steps.",
      300, "pages", [("mul", 300, "About three hundred words on a page", "words")],
      "≈ 90,000", "About ninety thousand words.")
fermi("Fans On A Football Pitch", "PEOPLE ON\nA PITCH", "How many people could stand on a football pitch? Break it into steps.",
      7000, "square metres", [("div", 0.25, "One standing person takes about a quarter of a square metre", "people")],
      "≈ 28,000", "About twenty eight thousand people.")


# ------------------------------------------------------------------ 5) A or B quizzes (15)
def quiz(title, hook, q_say, a, b, ans, why_a, why_b, say_a, say_b, ans_say, org="Top Tech"):
    PROBLEMS.append(dict(
        id=nid(), org=org, tag="QUIZ", title=title, sub="A or B? pick fast",
        hook_say="Quick quiz. A or B? Pick fast.", hook_text="A  OR  B?", hook_sub=hook,
        q=q_say,
        qparts=[dict(k="head", text=title, col="c"),
                dict(k="row", items=[f"A\n{a}", f"B\n{b}"], w=400, h=240, y=690, size=54, hl=[0, 1], cols={0: "c", 1: "p"}, dur=0.4),
                dict(k="foot", text="3 · 2 · 1 ...", col="y", at=0.7)],
        steps=[dict(say=say_a, parts=[dict(k="head", text=f"A  {a}", col="c"), dict(k="eq", lines=why_a, cols=["w"] * (len(why_a) - 1) + ["g" if ans == "A" else "r"], y=690)]),
               dict(say=say_b, parts=[dict(k="head", text=f"B  {b}", col="p"), dict(k="eq", lines=why_b, cols=["w"] * (len(why_b) - 1) + ["g" if ans == "B" else "r"], y=690)])],
        ans=f"{ans}  ·  {a if ans == 'A' else b}", ans_say=ans_say))


quiz("List Or Set Lookup", "python speed quiz", "You test whether a number is in a collection of one million numbers, again and again. Which is faster, a list or a set?",
     "LIST", "SET", "B", ["scans item by item", "O(n)", "1,000,000 checks"], ["hashes straight to it", "O(1)", "1 check"],
     "A list checks the items one by one, up to a million comparisons.", "A set uses a hash and jumps straight to the spot, in one step.", "B, the set. Constant time, whatever the size.")
quiz("Binary Or Linear Search", "sorted data", "The array is sorted and has a million items. Which finds a value faster, binary search or linear search?",
     "BINARY", "LINEAR", "A", ["halves the range each step", "O(log n)", "about 20 steps"], ["checks one by one", "O(n)", "up to 1,000,000 steps"],
     "Binary search halves the range every step, so a million items take about twenty steps.", "Linear search may check every single item.", "A, binary search. About twenty steps instead of a million.")
quiz("TCP Or UDP For Live Video", "streaming", "You are streaming live video and a little loss is fine, but delay is not. TCP or UDP?",
     "TCP", "UDP", "B", ["waits to resend lost data", "adds delay", "good for downloads"], ["no resending, no waiting", "low delay", "good for live video"],
     "TCP guarantees delivery, so lost packets are resent, and that adds delay.", "UDP just sends. A lost frame is skipped and the stream keeps moving.", "B, UDP. Live video values speed over perfection.")
quiz("Stack Or Queue For Undo", "which structure", "An editor needs an undo button that reverses the last action first. Stack or queue?",
     "STACK", "QUEUE", "A", ["last in, first out", "undo the newest first", "perfect for undo"], ["first in, first out", "undo the oldest first", "wrong order"],
     "A stack is last in, first out, so the newest action is undone first.", "A queue would undo the oldest action first, which is the wrong order.", "A, the stack.")
quiz("Array Or Linked List", "random access", "You need to jump straight to the five hundredth element, many times. Array or linked list?",
     "ARRAY", "LINKED LIST", "A", ["address = start + index", "O(1)", "instant jump"], ["follow 500 pointers", "O(n)", "slow jump"],
     "An array computes the address directly from the index, in one step.", "A linked list must follow five hundred pointers from the head.", "A, the array.")
quiz("Hash Map Or Tree Map", "sorted keys", "You need to read the keys in sorted order. Hash map or tree map?",
     "HASH MAP", "TREE MAP", "B", ["keys in no order", "fast lookup", "needs a sort step"], ["keys kept sorted", "O(log n) lookup", "iterate in order"],
     "A hash map gives fast lookups but no ordering.", "A tree map keeps its keys sorted all the time.", "B, the tree map.")
quiz("Process Or Thread", "shared memory", "Which one shares memory with its siblings, a process or a thread?",
     "PROCESS", "THREAD", "B", ["own memory space", "isolated", "safer, heavier"], ["shares the same memory", "lighter", "needs locks"],
     "Each process has its own memory, so it is isolated.", "Threads in one process share the same memory, which is why they need locks.", "B, the thread.")
quiz("GET Or POST For Login", "web basics", "A login form sends a password. GET or POST?",
     "GET", "POST", "B", ["data goes in the URL", "saved in history and logs", "never for passwords"], ["data goes in the body", "not in the URL", "use it for passwords"],
     "GET puts the data in the address, where it ends up in history and server logs.", "POST puts the data in the request body.", "B, POST, and use HTTPS as well.")
quiz("SQL Or NoSQL For Banking", "transactions", "A bank moves money between accounts and must never lose a cent. SQL or NoSQL?",
     "SQL", "NOSQL", "A", ["ACID transactions", "all or nothing", "built for money"], ["often relaxed consistency", "great for scale", "riskier for money"],
     "Relational databases give ACID transactions, so a transfer either fully happens or does not happen at all.", "Many NoSQL stores relax consistency to scale, which is risky for money.", "A, SQL.")
quiz("Mutex Or Semaphore", "one resource", "Exactly one thread may use a resource at a time. Mutex or semaphore?",
     "MUTEX", "SEMAPHORE", "A", ["one owner at a time", "lock and unlock", "exactly one"], ["counts permits", "allows N at once", "more general"],
     "A mutex lets one owner in at a time.", "A semaphore counts permits, so several can enter, if you set it that way.", "A, the mutex.")
quiz("BFS Or DFS Shortest Path", "graphs", "Find the shortest path in an unweighted graph. BFS or DFS?",
     "BFS", "DFS", "A", ["explores level by level", "first arrival is shortest", "uses a queue"], ["dives deep first", "first arrival may be long", "uses a stack"],
     "BFS explores level by level, so the first time it reaches a node is by the shortest route.", "DFS dives deep, so the first path it finds can be very long.", "A, BFS.")
quiz("Which Is Bigger Two To The Twenty", "powers", "Which is bigger, two to the power of twenty, or one million?",
     "2^20", "1,000,000", "A", ["2^10 = 1,024", "2^20 = 1,048,576", "bigger"], ["10^6 = 1,000,000", "a bit smaller", "close, but less"],
     "Two to the ten is one thousand and twenty four, so two to the twenty is one million, forty eight thousand, five hundred and seventy six.", "One million is slightly smaller.", "A, two to the twenty.")
quiz("Row Or Column Traversal", "cache", "In a big two dimensional array in C, which loop order is faster, rows first or columns first?",
     "ROW FIRST", "COLUMN FIRST", "A", ["walks memory in order", "cache friendly", "fast"], ["jumps across memory", "cache misses", "slow"],
     "C stores rows one after another, so walking along a row reads memory in order, and the cache loves it.", "Walking down a column jumps across memory and misses the cache.", "A, rows first.")
quiz("Stable Sort Merge Or Quick", "stability", "Which of these is a stable sort, merge sort or quick sort?",
     "MERGE", "QUICK", "A", ["equal items keep order", "stable", "O(n log n)"], ["may reorder equal items", "not stable", "usually in place"],
     "Merge sort keeps equal items in their original order.", "Standard quick sort can swap equal items past each other.", "A, merge sort.")
quiz("Memory Array Or Linked List", "memory use", "One million integers. Which uses more memory, an array or a linked list?",
     "ARRAY", "LINKED LIST", "B", ["just the numbers", "packed tightly", "less memory"], ["number plus a pointer", "extra bytes per item", "more memory"],
     "An array stores only the values, packed together.", "A linked list stores a pointer next to every value, so it needs more memory.", "B, the linked list.")


# ------------------------------------------------------------------ 6) behavioural (10)
def behav(title, hook, q_say, bad_say, bad, good_say, good, tag_line, closing_say):
    PROBLEMS.append(dict(
        id=nid(), org="Interview", tag="BEHAVIORAL", title=title, sub="bad answer vs good answer",
        hook_say=f"The interview question everyone dreads. {q_say} Most people ruin it.", hook_text=hook, hook_sub="bad answer vs good answer",
        q="Here is the answer most people give, and here is the one that gets the job.",
        qparts=[dict(k="head", text="30 seconds. Make them count.", col="y"), dict(k="big", text=hook.replace("\n", " "), col="c", size=64, y=690), dict(k="foot", text="two ways to answer", col="y", at=0.7)],
        steps=[dict(say=bad_say, stamp="WRONG", parts=[dict(k="head", text="the bad answer", col="r"), dict(k="eq", lines=bad, cols=["r"] * len(bad), y=690, size=46)]),
               dict(say=good_say, parts=[dict(k="head", text="the good answer", col="g"), dict(k="eq", lines=good, cols=["g"] * len(good), y=690, size=44)]),
               dict(say=closing_say, parts=[dict(k="big", text=tag_line, col="g", size=84, y=650), dict(k="foot", text="practise it out loud", col="y", at=0.7)])],
        ans=tag_line[:24], ans_say=closing_say))


behav("Why Should We Hire You", "WHY HIRE\nYOU?", "Why should we hire you?",
      "The bad answer. Because I need a job, I am a hard worker, and I am a fast learner. That is what everyone says.",
      ["because I need a job", "I am a hard worker", "I am a fast learner"],
      "The good answer matches your proof to their problem. Name their need, show a result you delivered, and say what you will do for them.",
      ["1  THEIR NEED: what they want solved", "2  MY PROOF: one result, with a number", "3  MY PLAN: what I will do first"],
      "NEED · PROOF · PLAN", "Their need, your proof, your plan.")
behav("Your Biggest Weakness", "YOUR BIGGEST\nWEAKNESS?", "What is your biggest weakness?",
      "The bad answer. I work too hard, or I am a perfectionist. Interviewers have heard it a thousand times.",
      ["I work too hard", "I am a perfectionist", "I have no weaknesses"],
      "The good answer is a real weakness that is not critical, with the fix you are already making.",
      ["1  A REAL weakness (not critical)", "2  HOW it showed up once", "3  WHAT I do about it now"],
      "REAL · EXAMPLE · FIX", "A real weakness, a real example, a real fix.")
behav("Where Do You See Yourself In Five Years", "5 YEARS\nFROM NOW?", "Where do you see yourself in five years?",
      "The bad answer. Your job, or running the company, or I have no idea.",
      ["in your chair", "running this company", "I have no idea"],
      "The good answer shows growth that fits the role and the company.",
      ["1  SKILLS I want to master", "2  IMPACT I want to have", "3  WHY this company fits that"],
      "SKILLS · IMPACT · FIT", "Skills, impact, fit.")
behav("Tell Me About A Conflict", "A CONFLICT\nAT WORK?", "Tell me about a conflict with a coworker.",
      "The bad answer. Blaming the other person, or saying you never had a conflict.",
      ["he was impossible", "it was all her fault", "I never have conflicts"],
      "The good answer uses the star method. Situation, task, action and result, with you staying calm and fair.",
      ["S  the situation, briefly", "T  my task", "A  what I did", "R  the result"],
      "STAR METHOD", "Use the star method.")
behav("Why Are You Leaving Your Job", "WHY LEAVE\nYOUR JOB?", "Why are you leaving your current job?",
      "The bad answer. Complaining about your boss, the pay or the company.",
      ["my boss is terrible", "the pay is awful", "the company is a mess"],
      "The good answer is positive and forward looking. What you are moving toward, not what you are running from.",
      ["1  WHAT I learned there", "2  WHAT I want next", "3  WHY this role is it"],
      "MOVE TOWARD", "Talk about what you are moving toward.")
behav("Tell Me About A Failure", "A FAILURE\nAT WORK?", "Tell me about a time you failed.",
      "The bad answer. I have never failed, or a failure that was secretly a success.",
      ["I have never failed", "my failure was a success", "it was my team's fault"],
      "The good answer owns the mistake, says what you learned, and shows what changed afterwards.",
      ["1  THE mistake, owned", "2  WHAT I learned", "3  WHAT I do differently now"],
      "OWN · LEARN · CHANGE", "Own it, learn it, change it.")
behav("Salary Expectations", "SALARY\nEXPECTATIONS?", "What are your salary expectations?",
      "The bad answer. Whatever you think is fair, or throwing out a number with no research.",
      ["whatever you think is fair", "I don't know", "the first number that came to mind"],
      "The good answer is a researched range, based on the market and your value, with some flexibility.",
      ["1  RESEARCH the market range", "2  SAY a range, not one number", "3  STAY open to the whole package"],
      "RESEARCH · RANGE", "Research it and give a range.")
behav("Do You Have Any Questions", "ANY\nQUESTIONS?", "Do you have any questions for us?",
      "The bad answer. No, I think you covered everything.",
      ["no, all good", "I think you covered it", "when do I get holidays?"],
      "The good answer asks two smart questions about the team, the goals and how success is measured.",
      ["1  WHAT does success look like?", "2  WHAT are the team's challenges?", "3  WHAT are the next steps?"],
      "ASK SMART QUESTIONS", "Always ask smart questions.")
behav("Why This Company", "WHY THIS\nCOMPANY?", "Why do you want to work here?",
      "The bad answer. I need a job, or you are a big name, or it is close to home.",
      ["I need a job", "you are famous", "it's close to home"],
      "The good answer shows you did your homework. A specific product or value, and why it matters to you.",
      ["1  ONE specific thing about them", "2  WHY it matters to me", "3  HOW my skills fit it"],
      "SPECIFIC · PERSONAL", "Be specific and personal.")
behav("Describe Your Leadership", "YOUR LEADERSHIP\nSTYLE?", "How would you describe your leadership style?",
      "The bad answer. I am a natural leader, or I just tell people what to do.",
      ["I am a natural leader", "I tell people what to do", "I have no style"],
      "The good answer is a style backed by a story. How you lead, and a time it worked.",
      ["1  MY style in one line", "2  A STORY where it worked", "3  THE team result"],
      "STYLE + STORY", "A style and a story.")


# ------------------------------------------------------------------ 7) live simulations (10)
def sim(title, hook, q_say, stages, run, labels, ans_text, ans_say, stage_say, vmax, org="Quant", hint="we play it for real", head=None):
    steps = []
    for n in stages:
        vals = run(n)
        mx = vmax(n, vals) if callable(vmax) else vmax
        steps.append(dict(say=stage_say(n, vals), parts=[dict(k="head", text=(head(n) if head else f"{fmt(n)} trials"), col="c"),
                                                          dict(k="bars", vals=list(vals), labels=list(labels), hl=[len(vals) - 1], max=mx, base=900, maxh=340,
                                                               fmt="{:g}")]))
    PROBLEMS.append(dict(
        id=nid(), org=org, tag="SIMULATION", title=title, sub="we simulate it live", hook_say="Don't trust your gut. Let's simulate it.",
        hook_text=hook, hook_sub=hint,
        q=q_say,
        qparts=[dict(k="head", text=title, col="y"), dict(k="big", text="simulate\nit", col="c", size=110, y=660), dict(k="foot", text="then trust the numbers", col="y", at=0.7)],
        steps=steps, ans=ans_text, ans_say=ans_say))


def r(seed):
    return random.Random(seed)


def monty(doors):
    def run(n):
        g = r(7 + doors)
        stay = sum(1 for _ in range(n) if g.randrange(doors) == g.randrange(doors))
        return (stay, n - stay)
    return run


sim("Simulate Monty Hall", "SWITCH\nOR STAY?", "Three doors, one car. You pick one, the host opens a goat door. Should you stay or switch? We play it ten, a hundred, and a thousand times.",
    [10, 100, 1000], monty(3), ("STAY", "SWITCH"), "SWITCH", "Always switch. Your first pick is right only one time in three.",
    lambda n, v: f"{fmt(n)} games. Staying won {v[0]} times. Switching won {v[1]}.", lambda n, v: n, head=lambda n: f"{fmt(n)} games")
sim("Monty Hall With Five Doors", "5 DOORS\nSWITCH?", "Five doors, one car. You pick one, and the host opens three goat doors. Do you stay, or switch to the last closed door?",
    [10, 100, 1000], monty(5), ("STAY", "SWITCH"), "SWITCH", "Switch. Staying wins one in five. Switching wins four in five.",
    lambda n, v: f"{fmt(n)} games. Staying won {v[0]}. Switching won {v[1]}.", lambda n, v: n, head=lambda n: f"{fmt(n)} games")


def birthday(size):
    g = r(size)
    hits = sum(1 for _ in range(4000) if len({g.randrange(365) for _ in range(size)}) < size)
    return (round(100 * hits / 4000),)


sim("The Birthday Paradox", "SAME\nBIRTHDAY?", "How many people do you need in a room before two of them probably share a birthday? We test rooms of ten, twenty three and forty.",
    [10, 23, 40], birthday, ("shared %",), "23 PEOPLE", "Twenty three people is enough for a fifty percent chance.",
    lambda n, v: f"A room of {n}. In {v[0]} percent of rooms, two people shared a birthday.", 100, hint="the answer surprises everyone", head=lambda n: f"room of {n} people")


def two_kids(n):
    g = r(5)
    both = mixed = 0
    while both + mixed < n:
        a, b = g.randrange(2), g.randrange(2)
        if a == 0 and b == 0:
            both += 1
        elif a == 0 or b == 0:
            mixed += 1
    return (both, mixed)


sim("Two Children One Is A Boy", "ONE IS\nA BOY", "A family has two children, and at least one is a boy. What is the chance that both are boys? We check families that match.",
    [10, 100, 1000], two_kids, ("BOTH BOYS", "BOY AND GIRL"), "ONLY 1 IN 3", "One in three, not one half.",
    lambda n, v: f"Out of {fmt(n)} families with a boy, {v[0]} had two boys and {v[1]} had a boy and a girl.", lambda n, v: n)


def coupon(n):
    g = r(11)
    tot = 0
    for _ in range(n):
        seen, k = set(), 0
        while len(seen) < 6:
            seen.add(g.randrange(6))
            k += 1
        tot += k
    return (round(tot / n, 1),)


sim("Collect All Six Dice Faces", "ALL SIX\nFACES", "How many times must you roll a die before you have seen every face at least once? We average ten, a hundred, and a thousand attempts.",
    [10, 100, 1000], coupon, ("avg rolls",), "ABOUT 14.7", "About fourteen point seven rolls.",
    lambda n, v: f"Average over {fmt(n)} attempts: {v[0]} rolls.", 20, hint="not six")


def first_six(n):
    g = r(21)
    tot = 0
    for _ in range(n):
        k = 1
        while g.randrange(6) != 5:
            k += 1
        tot += k
    return (round(tot / n, 1),)


sim("Rolls Until A Six", "ROLLS UNTIL\nA SIX", "How many times do you roll a die, on average, before you get your first six?",
    [10, 100, 1000], first_six, ("avg rolls",), "6 ROLLS", "Six rolls, on average.",
    lambda n, v: f"Over {fmt(n)} tries it took {v[0]} rolls on average.", 10, hint="easier than you think")


def stick(n):
    g = r(31)
    ok = 0
    for _ in range(n):
        a, b = sorted((g.random(), g.random()))
        x, y, z = a, b - a, 1 - b
        if max(x, y, z) < 0.5:
            ok += 1
    return (round(100 * ok / n),)


sim("Broken Stick Simulation", "STICK TO\nTRIANGLE?", "Break a stick in two random places. What is the chance the three pieces can form a triangle?",
    [10, 100, 1000], stick, ("triangle %",), "25 PERCENT", "One in four.",
    lambda n, v: f"After {fmt(n)} sticks, {v[0]} percent made a triangle.", 100, hint="harder than it sounds")


def dice(n):
    g = r(41)
    c = [0] * 11
    for _ in range(n):
        c[g.randrange(1, 7) + g.randrange(1, 7) - 2] += 1
    return tuple(c)


sim("Two Dice Sums", "TWO DICE\nWHICH SUM?", "You roll two dice and add them. Which total comes up most often? We roll thirty six, three hundred and sixty, and three thousand six hundred times.",
    [36, 360, 3600], dice, tuple(str(i) for i in range(2, 13)), "SEVEN WINS", "Seven. It has six ways to appear.",
    lambda n, v: f"{fmt(n)} rolls. Seven came up {v[5]} times.", lambda n, v: max(v) * 1.1, hint="not a flat curve")


def walk(n):
    g = r(51)
    tot = 0
    for _ in range(n):
        p = 0
        for _ in range(100):
            p += 1 if g.random() < 0.5 else -1
        tot += abs(p)
    return (round(tot / n, 1),)


sim("Random Walk Distance", "DRUNK MAN'S\nWALK", "A drunk man takes one hundred random steps, each one forward or back. How far from the start is he, on average?",
    [10, 100, 1000], walk, ("avg steps away",), "ABOUT 8", "Only about eight steps from the start.",
    lambda n, v: f"Across {fmt(n)} walks he ended {v[0]} steps from the start on average.", 20, hint="not fifty")


def hats(n):
    g = r(61)
    zero = 0
    for _ in range(n):
        p = list(range(10))
        g.shuffle(p)
        if all(p[i] != i for i in range(10)):
            zero += 1
    return (round(100 * zero / n),)


sim("Hat Check Disaster", "NOBODY GETS\nTHEIR HAT", "Ten people check their hats, and the hats come back completely shuffled. What is the chance nobody gets their own hat?",
    [100, 1000, 10000], hats, ("nobody %",), "ABOUT 37%", "About thirty seven percent. It is one over e.",
    lambda n, v: f"In {fmt(n)} shuffles, nobody got their own hat {v[0]} percent of the time.", 100, hint="it is not tiny")

assert len(PROBLEMS) == 100, len(PROBLEMS)
