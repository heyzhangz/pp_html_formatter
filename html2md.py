# -----------------------------------------------------------------------------
# Name:        html2xml.py
# Purpose:     Find and get Chinese Privacy Policy from html
#
# Author:      ZhangZ
#
# Created:     07.05.2021
# Copyright:   
# Licence:     
# -----------------------------------------------------------------------------

import re
import os
import email
import bs4
from xml.etree.ElementTree import Element, SubElement, ElementTree
from bs4 import BeautifulSoup
import html2text as ht
import IPython

def parseMhtml(fpath):
    """
        parse mhtml format
    """

    res = ""
    with open(fpath, "rb") as fb:
        msg = email.message_from_bytes(fb.read())
    
    parts = msg.get_payload()
    if not type(parts) == list:
        parts = [msg]

    for part in parts:
        res += str(part.get_payload(decode=True), encoding="utf-8")

    return res

def readHtml(fpath):
    """
        read html from exist file
    """
    res = None

    basename = os.path.basename(fpath)
    if basename.endswith(".html"):
        with open(fpath, 'r', encoding="utf-8") as f:
            htmltext = f.read()
            htmltext = re.sub(r"\\/", "/", htmltext)
        res = BeautifulSoup(htmltext, "lxml")
    elif basename.endswith(".mhtml") or basename.endswith(".mht"):
        htmltext = parseMhtml(fpath)
        with open(fpath + ".html", 'w', encoding="utf-8") as f:
            f.write(htmltext)
        res = BeautifulSoup(htmltext, "lxml")
    else:
        print("[ERROR] what the hell extension it is: %s" % fpath)
    
    return res

def _hasSameSibling(node):

    tag = node.name
    attrs = node.attrs
    
    nodeSiblings = list(node.previous_siblings)
    for sibling in nodeSiblings:
        if tag == sibling.name and attrs == sibling.attrs:
            return True
    
    nodeSiblings = list(node.next_siblings)
    for sibling in nodeSiblings:
        if tag == sibling.name and attrs == sibling.attrs:
            return True
        

    return False

def findPPBody(soup):
    """
        find the main structure from Privacy Policy
    """

    ppregx = re.compile(r"隐私.*?(政策|声明)")
    body = soup.select_one("body")
    
    chosenPpbody = None
    chosenPpbodyLen = 0

    ppbodies = body.find_all(text=ppregx)
    for ppbody in ppbodies:
        while ppbody != body:
            if ppbody.name == "div" and not _hasSameSibling(ppbody):
                break
            ppbody = ppbody.parent
        
        dlen = len(list(ppbody.descendants))
        if dlen > chosenPpbodyLen:
            chosenPpbodyLen = dlen
            chosenPpbody = ppbody

    return chosenPpbody

def transformHtml(htmltext):
    """
        # TODO change html text to markdown
    """
    text_maker = ht.HTML2Text()
    text_maker.bypass_tables = False
    text_maker.ignore_tables = False
    try:
        markdown = text_maker.handle(str(htmltext))
    except Exception as e:
        print("[ERROR] can not transformer to markdown: " + str(e))
    return markdown

if __name__ == "__main__":

    for root, _, files in os.walk(r"./case"):
        
        for f in files:
            if not f.endswith("html"):
                continue
            
            fpath = os.path.join(root, f)
            print("[INFO] start parse %s" % fpath)
            soup = readHtml(fpath)
            body = findPPBody(soup)
            mdtxt = transformHtml(body)
            open(os.path.join('/home/yh/code/pp_html_formatter/case_out', f+'.md'), 'w').write(mdtxt)



            # basename = os.path.basename(fpath)
            # savename = basename + ".txt"
            # with open(os.path.join(r"./temp", savename), "w", encoding="utf-8") as wf:
            #     wf.write(body.prettify())

            # savexmlname = basename + ".xml"
            # pproot.buildXMLTree().write(os.path.join(r"./tempxml", savexmlname), encoding="utf-8")