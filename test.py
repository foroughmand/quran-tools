from quran import Quran 
from main import *

q = Quran()

# print(' '.join([q.root(113, 5, i) for i in range(1)]))
print(q.aye(113, 5))

print(q.sure(112))
print(q.sure(112, print_besmellah = True))

for s in q.items():
    for a in s.items():
        for t in a.items():
            if t.root_roman() == 'HSd':
                print(t.sindex, t.aindex, t.tindex, t.token())

for t in q.search_root_roman('HSd'):
    print(t.sindex, t.aindex, t.tindex, t.token())

for t in q.search_root(q.deroman('HSd')):
    print(t.sindex, t.aindex, t.tindex, t.token())

print(q.sure(0))
print(common_roots(q, [Range(0, 0, 1), Range(0, 1, 3)], 0))
print(read_item('[[0,0,1],[0,1,3]]', 0, 0, False))
print(json.dumps(read_item('[[0,0,1],[0,1,3]]', 0, 1, True), ensure_ascii=False))