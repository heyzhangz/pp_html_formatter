import re
import os

class Element:
    LINK = "link"
    IMAGE = "img"
    TITLE = "title"
    CONTENT = "content"

def isLink(line):
    """
        判断markdown单行是否为超链接
    """
    # 存在图片超链接嵌套的情况
    res = re.search(r"(?<!\!)\[(?P<text>.*)\]\((?P<link>.*?)\)", line)

    if res == None:
        return None

    text = res.group("text")
    link = res.group("link")
    if len(link.strip()) == 0:
        return None

    return {
                "type": Element.LINK,
                "text": text,
                "link": link
           }

def isImg(line):
    """
        判断markdown单行是否为图片
    """
    res = re.search(r"(?<=\!)\[(?P<text>.*?)\]\((?P<link>.*?)\)", line)

    if res == None:
        return None

    text = res.group("text")
    link = res.group("link")
    if len(link.strip()) == 0:
        return None

    return {
                "type": Element.IMAGE,
                "text": text,
                "link": link
           }

def isMDTitle(line):
    """
        判断markdown单行是否为markdown格式标题(#)
    """
    res = re.search(r"^(?P<level>#+) (?P<text>.*)", line)

    if res == None:
        return None
    
    level = len(res.group("level"))
    text = res.group("text")
    if level <= 0:
        return None
    
    return {
                "type": Element.TITLE,
                "level": level,
                "text": text
           }

def isBold(line):
    """
        判断markdown单行是否为黑体
    """
    res = re.search(r"^\*\*(?P<text>.*)\*\*$", line)

    if res == None:
        return None

    text = res.group("text")

    return text

def parseContent(line):

    return {
                "type": Element.CONTENT,
                "text": line
           }

def parseTitle(level, text):

    return {
                "type": Element.TITLE,
                "level": level,
                "text": text
           }

def preproLine(line):
    """
        预处理markdown单行, 删除首位空白符
    """

    line = re.sub(r"^\s", "", line)
    
    return line.strip()

def delMDTag(line):
    """
        去除markdown的特殊标记
    """
    line = re.sub(r"\*", '', line)
    line = re.sub(r"\\\.", '.', line)

    return line

def readMarkdown(fpath):

    with open(fpath, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    return lines

"""
    根据解析结果格式化文本
"""
def formatTitle(res):

    return "%s %s\n" % (('#' * res["level"]), res["text"])

def formatImage(res):

    return "![img](%s)\n" % res["link"]

def formatLink(res):

    return "[%s](%s)\n" % (res["text"], res["link"])

def formatContent(res):

    # 对于content, 剔除部分无效字符
    text = re.sub(r"\*", "", res["text"])

    return "%s\n" % text


class AbstractParser():

    def __init__(self, lines):

        self.lines = lines
        self.parseRes = []
        self.score = 65535

        pass

    def outputMarkdown(self):
        """
            输出解析后的markdown文本
        """
        self._formatParseRes()
        out = ""
        for res in self.parseRes:
            lineType = res["type"]
            out += formatTitle(res)   if lineType == Element.TITLE else \
                   formatLink(res)    if lineType == Element.LINK  else \
                   formatImage(res)   if lineType == Element.IMAGE else \
                   formatContent(res)
        
        return out

    def getScore(self):
        """
            计算解析分数
        """
        maxscore = 0
        for res in self.parseRes:
            if res["type"] == Element.TITLE:
                maxscore = max(res["level"], maxscore)
        
        return maxscore
    
    def _formatParseRes(self):
        """
            去除无效标题节点
        """
        preLevel = -1
        for idx, node in enumerate(self.parseRes):
            if node["type"] == Element.TITLE:
                if node["level"] >= preLevel:
                    self.parseRes[idx - 1]["type"] = Element.CONTENT
                preLevel = node["level"]
            else:
                preLevel = -1

        pass

    pass

class MutiTitleParser(AbstractParser):
    """
        Html多级标题的parser, 用于解析标准的<h>标签的隐私政策
    """
    def __init__(self, lines):
        super().__init__(lines)
        pass

    def parse(self):

        for line in self.lines:
            line = preproLine(line)

            if len(line) == 0:
                continue

            # 先判断是不是超链接, 存在超链接嵌套的情况
            res = isLink(line)
            if res:
                self.parseRes.append(res)
                continue
                
            # 判断是否是图片
            res = isImg(line)
            if res:
                self.parseRes.append(res)
                continue

            res = isMDTitle(line)
            if res:
                self.parseRes.append(res)
                continue
            
            self.parseRes.append(parseContent(line))

        pass

ALL_SERIAL_NUM_PATTERN = [
    r"^[(（][一二三四五六七八九十]+[)）]", # (一)
    r"^[一二三四五六七八九十]+[)）]", # 一)
    r"^[一二三四五六七八九十]+[、.．]", # 一、
    r"^[㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩]",
    r"^[(（][0-9]{1,2}[)）]", # (1)
    r"^[0-9]{1,2}[)）]", # (1
    r"^[0-9]{1,2}[、.．](?!\d)", # 1.
    r"^[0-9]{1,2}[、.．][0-9]{1,2}[、.．]?(?!\d)", # 1.1
    r"^[0-9]{1,2}([、.．][0-9]{1,2}){2}[、.．]?(?!\d)", # 1.1.1
    r"^[0-9]{1,2}([、.．][0-9]{1,2}){3}[、.．]?(?!\d)", # 1.1.1.1
    r"^[0-9]{1,2}([、.．][0-9]{1,2}){4}[、.．]?(?!\d)", # 1.1.1.1.1
    r"^[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]",
    r"^[(（]?[⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛]",
    r"^[(（]?[❶❷❸❹❺❻❼❽❾❿⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴]",
    r"^[ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ]",
    r"^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ][、.．]",
    r"^[(（][a-zA-Z][)）]", # (a)
    r"^[a-zA-Z][)）]", # a)
    r"^[a-zA-Z][、.．]", # a.
    r"^[(（]?[ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ]",
    r"^[(（]?[ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ]"

    # markdown标题也算进行, 但是单独处理, 格式对应为
    # "MARKDOWN_<lv>"
]

def isSerialTitle(line):

    res = isMDTitle(line)
    if res:
        return ("MARKDOWN_%d" % res["level"], res["text"])

    # 去除加粗, 斜体
    line = delMDTag(line)
    for regx in ALL_SERIAL_NUM_PATTERN:
        if re.match(regx, line):
            return (regx, line)
    
    return None

class SerialNumAdapter(AbstractParser):
    """
        序号标题适配器, 用于解析带序号标题格式的隐私政策
    """

    def __init__(self, lines):
        super().__init__(lines)

        self.nowLevelList = {} # 保存现有标题等级结构
        self.nowMaxLevel = 0
        pass
    
    def _isAlreadyTitle(self, line):
        # 判断是否是已有的标题结构

        md = isMDTitle(line)
        if md:
            # 如果是<h>标签
            nowType = "MARKDOWN_%d" % md["level"]
            for level, regx in self.nowLevelList.items():
                if not regx.startswith("MARKDOWN"):
                    continue
                if regx == nowType:
                    return (level, md["text"])
        else:
            # 去除加粗, 斜体
            line = delMDTag(line)
            for level, regx in self.nowLevelList.items():
                if regx.startswith("MARKDOWN"):
                    continue
                if re.search(regx, line):
                    return (level, line)
        
        return None

    def parse(self):

        for line in self.lines:
            line = preproLine(line)

            if len(line) == 0:
                continue
            
             # 先判断是不是超链接, 存在超链接嵌套的情况
            res = isLink(line)
            if res:
                self.parseRes.append(res)
                continue
                
            # 判断是否是图片
            res = isImg(line)
            if res:
                self.parseRes.append(res)
                continue

            res = self._isAlreadyTitle(line)
            if res:
                # 如果是已有的标题
                self.parseRes.append(parseTitle(res[0], res[1]))
                continue

            # 如果不是已有标题, 判断是不是序号标题
            res = isSerialTitle(line)
            if res:
                self.nowMaxLevel += 1
                self.nowLevelList[self.nowMaxLevel] = res[0]
                self.parseRes.append(parseTitle(self.nowMaxLevel, res[1]))
                continue
            
            self.parseRes.append(parseContent(line))

        pass

if __name__ == "__main__":

    for root, _, files in os.walk(r"./cases"):
        for f in files:
            if not f.endswith(".md"):
                continue
            
            # par = MutiTitleParser(readMarkdown(os.path.join(root, f)))
            par = SerialNumAdapter(readMarkdown(os.path.join(root, f)))
            par.parse()
            
            with open(os.path.join(r"./testcases", f), 'w', encoding="utf-8") as g:
                g.write(par.outputMarkdown())

