from time import time

from konlpy.tag import Kkma
from konlpy.utils import pprint

start = time()
kkma = Kkma()
print(f"{1000*(time() - start):.0f}ms")

pprint(kkma.pos("네안녕하세요반갑습니다."))
print(f"{1000*(time() - start):.0f}ms")

pprint(kkma.pos("참신하고 시사하는 바가 크다."))
print(f"{1000*(time() - start):.0f}ms")

pprint(
    kkma.pos(
        "오늘날에는 상대적으로 많이 사용되지 않는 라디오파 영역과 같이 비어있는 대역폭의 사용을 타진하는 것에서 시작할 수 있습니다."
    )
)
print(f"{1000*(time() - start):.0f}ms")
