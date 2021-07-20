import re
import os

class Element:
    LINK = "link"
    IMAGE = "img"
    TITLE = "title"
    CONTENT = "content"

def isLink(line):

    # 存在图片超链接嵌套的情况
    res = re.search(r"(?<!\!)\[(?P<text>.*)\]\((?P<link>.*?)\)", line)

    if res == None:
        return None

    text = res.group("text")
    link = res.group("link")
    if len(link.strip()) == 0:
        return None

    return (text, link)

def isImg(line):

    res = re.search(r"(?<=\!)\[(?P<text>.*?)\]\((?P<link>.*?)\)", line)

    if res == None:
        return None

    text = res.group("text")
    link = res.group("link")
    if len(link.strip()) == 0:
        return None

    return (text, link)

def isTitle(line):

    res = re.search(r"^(?P<level>#+) (?P<text>.*)", line)

    if res == None:
        return None
    
    level = len(res.group("level"))
    text = res.group("text")
    if level <= 0:
        return None
    
    return (level, text)

def isBold(line):

    res = re.search(r"^\*\*(?P<text>.*)\*\*", line)

    if res == None:
        return None

    text = res.group("text")

    return text

def preproLine(line):

    line = re.sub(r"^\s", "", line)
    
    return line.strip()

def readMD(fpath):

    with open(fpath, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    return lines

def formatTitle(res):

    return "%s %s\n" % ('#' * res["level"], res["text"])

def formatImage(res):

    return "![img](%s)\n" % res["link"]

def formatLink(res):

    return "[%s](%s)\n" % (res["text"], res["link"])

def formatContent(res):

    text = re.sub(r"\*", "", res["text"])

    return "%s\n" % text

class AbstractParser():

    def __init__(self, lines):

        self.lines = lines
        self.parseRes = []
        self.score = 65535

        pass

    def outputMarkdown(self):
        
        out = ""
        for res in self.parseRes:
            lineType = res["type"]
            out += formatTitle(res)   if lineType == Element.TITLE else \
                   formatLink(res)    if lineType == Element.LINK  else \
                   formatImage(res)   if lineType == Element.IMAGE else \
                   formatContent(res)
        
        return out

    def getScore(self):
        
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
                self.parseRes.append({
                    "type": Element.LINK,
                    "text": res[0],
                    "link": res[1]
                })
                continue
                
            # 判断是否是图片
            res = isImg(line)
            if res:
                self.parseRes.append({
                    "type": Element.IMAGE,
                    "link": res[1]
                })
                continue

            res = isTitle(line)
            if res:
                self.parseRes.append({
                    "type": Element.TITLE,
                    "level": res[0],
                    "text": res[1]
                })
                continue
            
            self.parseRes.append({
                "type": Element.CONTENT,
                "text": line
            })

        pass

if __name__ == "__main__":

    for root, _, files in os.walk(r"./cases"):
        for f in files:
            if not f.endswith(".md"):
                continue
            
            mp = MutiTitleParser(readMD(os.path.join(root, f)))
            mp.parse()
            
            with open(os.path.join(r"./testcases", f), 'w', encoding="utf-8") as g:
                g.write(mp.outputMarkdown())

