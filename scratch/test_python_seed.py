import math

def _mixkey(seed_str: str) -> bytes:
    key = [0] * 256
    smear = 0
    for j, ch in enumerate(seed_str):
        idx = j & 255
        old_smear = smear
        smear = (smear ^ (key[idx] * 19)) & 0xFF_FF_FF_FF
        key[idx] = (smear + ord(ch)) & 255
        if j < 15:
            print(f"j={j} old_smear={old_smear} new_smear={smear} key_val={key[idx]}")
    # Slice to seed length (up to 256) to match JS dynamic array length
    return bytes(key[:min(len(seed_str), 256)])

class ARC4:
    _WIDTH = 256
    _MASK = 255

    def __init__(self, key_bytes: bytes) -> None:
        s = list(range(self._WIDTH))
        j = 0
        key = list(key_bytes) if key_bytes else [0]
        kl = len(key)
        j_list = []
        for i in range(self._WIDTH):
            if i == 52:
                print(f"i=52 j_before={j} s[52]={s[52]} key[52]={key[i % kl]}")
            j = (j + s[i] + key[i % kl]) & self._MASK
            s[i] = s[j]
            s[j] = i
            j_list.append(j)
        self._s = s
        self._i = 0
        self._j = j
        # self.g(self._WIDTH)  # RC4-drop[256]

    def g(self, count: int) -> int:
        r = 0
        s, mask = self._s, self._MASK
        i, j = self._i, self._j
        for _ in range(count):
            i = (i + 1) & mask
            t = s[i]
            j = (j + t) & mask
            
            # Swap
            s[i] = s[j]
            s[j] = t
            
            # Non-standard lookup
            idx = (t + j) & mask
            r = r * self._WIDTH + s[idx]
        self._i = i
        self._j = j
        return r

class Seedrandom:
    _CHUNKS = 6
    _WIDTH = 256
    _SIGNIFICANCE = 2 ** 52
    _OVERFLOW = _SIGNIFICANCE * 2
    _STARTDENOM = _WIDTH ** _CHUNKS

    def __init__(self, seed: str) -> None:
        key_bytes = _mixkey(seed)
        self._arc4 = ARC4(key_bytes)

    def random(self) -> float:
        n = self._arc4.g(self._CHUNKS)
        d = self._STARTDENOM
        x = 0
        while n < self._SIGNIFICANCE:
            n = (n + x) * self._WIDTH
            d *= self._WIDTH
            x = self._arc4.g(1)
        while n >= self._OVERFLOW:
            n //= 2
            d //= 2
            x >>= 1
        return (n + x) / d

# Test
email = "23f1000805@ds.study.iitm.ac.in"
seed1 = f"q-fastapi-metrics-cors-server#{email}#"
rng = Seedrandom(seed1)

key_bytes = _mixkey(seed1)
print("Key 45-61:", ", ".join(map(str, list(key_bytes[45:62]))))
