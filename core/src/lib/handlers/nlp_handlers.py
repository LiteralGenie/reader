from time import time

from konlpy.tag import Kkma
from konlpy.utils import pprint

start = time()
kkma = Kkma()
print(f"{1000*(time() - start):.0f}ms")

pprint(kkma.pos("네안녕하세요반갑습니다."))
print(f"{1000*(time() - start):.0f}ms")

pprint(kkma.pos("네 안녕하세요 반갑습니다"))
