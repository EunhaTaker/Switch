'''
字典树，作用于命令行补全
插入时区分大小写
查询时不区分大小写
'''

def trans_case(char):
    '''转换大小写'''
    if char.isupper():
        char = char.lower()
    else:
        char = char.upper()
    return char

class Node:

    def __init__(self, char=None):
        self.char = char
        self.isString = False
        self.next = {}

    def getNext(self, char=None, ignore=True):
        if char != None:
            if not ignore:
                return self.next.get(char)
            res = []
            p = self.next.get(char)
            if p:
                res.append(p)
            if char.isalpha():
                p = self.next.get(trans_case(char))
            if p:
                res.append(p)
            return res
        else:
            return self.next.values()

    def addChar(self, char):
        next = self.getNext(char, ignore=False)
        if not next:
            if char == ' ':
                next = Node('\\ ')
            else:
                next = Node(char)
            self.next[char] = next
        return next

class Trie:

    def __init__(self):
        self.root = Node()

    def add(self, words):
        if type(words) == str:
            words = [words]
        for word in words:
            p = self.root
            for c in word:
                p = p.addChar(c)
            else:   # 最后加上空字符串，表示单词结束
                p.addChar('')

    def getWord(self, word):
        '''获取用word查找(大小写不敏感）的所有前缀及其各自对应的终节点，若word不是该树的前缀，返回None'''
        res = {'': self.root}
        for c in word:
            newres = {}
            for perfix in res:
                ps = res[perfix].getNext(c)
                for p in ps:
                    newres[perfix+p.char] = p
            res = newres
        return res

    def getStartBy(self, word):
        '''提供联想
        返回类型：
        空串-无法联想
        字符串-有单一联想后继
        数组-多个后继
        
        匹配失败：无法进入@1
        获得唯一联想词：@2
        获得多个候选词：@3
        '''
        candidates = self.getWord(word) # 大小写不敏感时，为word匹配到的前缀可能有多个
        single = True   # 联想结果是否唯一
        behind = ''     # 仅用于唯一候选
        flag = True     # flag为True，大循环将继续运行
        while flag:
            tmpchar = ''    # 用于水平扫描比较，作为待比较字符
            flag = False    # 初始将其置为False，若值得继续循环，后续代码会置True
            newcdd = {} # 用于更新候选
            for perfix in candidates:   # 遍历每个前缀 @1
                # 获取perfix对应节点的后继节点
                if candidates[perfix]:
                    ps = candidates[perfix].getNext()
                    if single:
                        if len(ps) == 1:    # 后继唯一，否则后续判断：无后继或者多后继将离开单一联想词模式
                            # 获取唯一的后继字符
                            nextChar = list(ps)[0].char # 后续判断：该字符与待比较字符不同（各路之间出现区别），将离开单一联想词模式
                            if not tmpchar: # 暂无待比较字符
                                # 使该后继上位
                                tmpchar = nextChar
                        if len(ps) != 1 or (tmpchar != nextChar and tmpchar != trans_case(nextChar)):  # 这里是后续判断
                            if behind:
                                # 有联想成果，收工 @2
                                # newcdd = candidates     # 战术修正
                                break
                            else:   # 分叉出现仍无联想成果，切换模式，开始匹配多个候选 @3
                                single = False
                    if ps:
                        flag = True
                        # 为所有后继更新前缀
                        for p in ps:
                            newcdd[perfix+p.char] = p
                    else:
                        newcdd[perfix] = None
                else:
                    newcdd[perfix] = None
            else:
                if single:
                    behind += tmpchar
                # 更新候选
                candidates = newcdd
        if behind:
            return [list(candidates.keys())[0]]
        else:
            return list(candidates.keys())
            

    def getStartWith(self, word, p=None):
        '''提供联想
        返回类型：
        空串-无法联想
        字符串-有单一联想后继
        数组-多个后继
        '''
        behind = ''
        if not p:   # p为后继搜寻的启动节点，若未指定，则从头开始获取p
            p = self.getWord(word)
        if p:
            while True:     # 对单传后代穷追猛打
                nexts = p.getNext()
                if len(nexts) == 1:
                    p = list(nexts)[0]
                    behind += p.char
                else:
                    break
            if behind:  # 有联想成果，收工
                return behind
            elif nexts: # 后继超过1个
                behinds = []
                for next in nexts:
                    # 对每个后继节点启动递归搜寻
                    res = self.getStartWith(None, next)
                    if isinstance(res, str):    # 搜寻结果为字符串：结果+1
                        behinds.append(next.char + res)
                    elif res:   # 搜寻结果为数组，结果+n
                        for s in res:
                            behinds.append(next.char + s)
                return behinds
        return ''

if __name__ == "__main__":
    t = Trie()
    t.add(['leet', 'leetcode', 'leets', 'leeds'])
    r = t.getStartWith('lee')
    print(r)