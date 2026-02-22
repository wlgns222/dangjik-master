# --- [자료구조 정의] ---
class Circular_List:
    def __init__(self, c_list=None):
        if c_list is None :
            self.__c_list = []
        else :
            self.__c_list = c_list
    def clear(self) :
        self.__c_list = []
    def append(self, x):
        self.__c_list.append(x)
    def get_at(self, idx):
        if len(self.__c_list) == 0: return None
        return self.__c_list[idx % len(self.__c_list)]
    def get_slice_list(self, s, e):
        length = len(self.__c_list)
        safe_s = max(0, min(s, length))
        safe_e = max(0, min(e, length))
        return self.__c_list[safe_s:safe_e]

    def length(self):
        return len(self.__c_list)

class List_Pointer:
    def __init__(self, p_list, idx):
        self.__idx = idx
        self.__p_list = p_list
    def get_val(self):
        temp = self.__p_list.get_at(self.__idx)
        self.__idx += 1
        return temp

class ChainingHashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(self.size)]
    def clear(self) :
        self.table = [[] for _ in range(self.size)]
    def _hash_function(self, key):
        return hash(key) % self.size
    def set(self, key, value):
        index = self._hash_function(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))
    def get(self, key):
        index = self._hash_function(key)
        for k, v in self.table[index]:
            if k == key: return v
        return None