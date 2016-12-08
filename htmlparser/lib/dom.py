# encoding=utf8
from bs4 import BeautifulSoup
import urllib2
import string
import bs4
import sys

def dom_get_text_nodes_by_tag(snode, enode=None, allowedTag=set()):
    """获取指定tag下的所有文本节点
    """
    
    nodes = []
    stop = False
    for node in snode.recursiveChildGenerator():
        if stop == True:
            break
        if node == enode:
            stop = True
        if not isinstance(node, bs4.element.NavigableString):
            continue
        if isinstance(node, bs4.element.Comment):
            continue
        if node.parent == None:
            continue
        if  node.string.strip() == "":
            continue
        tagName = node.parent.name
        if tagName in allowedTag:
            nodes.append(node)
            # print tagName, node.name, type(node), node.string
    return nodes

def dom_get_nearest_ancestor(root, nodes):
    """获取多个node的最近的共同的祖先节点
    """
    
    ancestor = nodes[0]
    for node in nodes[1:]:
        ancestor = _get_nearest_ancestor(root, comParent, node)
        
    return ancestor

def _get_nearest_ancestor(root, node1, node2):
    """获取2个node的最近的共同的祖先节点
    """
    
    pnodesA = []
    pnodesB = []
    
    pnode = node1
    pnodesA.append(pnode)
    while True:
        pnode = pnode.parent
        if pnode == None or pnode == root:
            break
        pnodesA.append(pnode)
    
    pnode = node2
    pnodesB.append(pnode)
    while True:
        pnode = pnode.parent
        if pnode == None or pnode == root:
            break
        pnodesB.append(pnode)
    
    comParent = root
    pnodesA.reverse()
    pnodesB.reverse()
    for i in xrange(len(pnodesA)):
        # print pnodesA[i].name,pnodesB[i].name
        if len(pnodesB) == i:
            break
        if pnodesA[i] == pnodesB[i]:
            comParent = pnodesA[i]
        else:
            break
    return comParent

def dom_get_ancestor_name_set(node):
    """ 获取祖先节点的tag名集合
    """
    tags = set()
    for parent in node.parents:
        if parent is None:
            break
        tags.add(parent.name)
    return tags

def getHtml(url):
    page = urllib2.urlopen(url)
    content = page.read()
    try:
        content = content.decode("utf8")
    except:
        pass
    return content

def letterCount(text):
    count = 0
    for ch in text:
        if ch in string.ascii_letters: count += 1
        elif ch in string.digits: count += 1
        elif ch in string.whitespace: count += 1
    return count

def getBodyNodes(root):
    allowedTag = set(["p"])
    nodes = getAllTextNodes(root, None, allowedTag)
    print nodes
    sys.exit()
    maxGroup = None
    maxLen = 0
    textLen = 0
    for group in getTextNodeGroup(nodes):
        gtext = getNodesText(group)
        textLen += len(gtext)
        if len(gtext) > maxLen:
            maxLen = len(gtext)
            maxGroup = group
            
    return maxGroup
    return getMinCommonParent(root, [maxGroup[0], maxGroup[-1]])

def getBody(bodyNodes):
    pnode = getMinCommonParent(root, [bodyNodes[0], bodyNodes[-1]])
    allowedTag = set("div p h1 h2 h3 h4 h5 h6 span li strong a".strip().split())
    nodes = getAllTextNodes(pnode, bodyNodes[-1], allowedTag)
    return getNodesText(nodes)
    
def getTitleNode(root, bodyNodes):
    bodyNode = getMinCommonParent(root, [bodyNodes[0], bodyNodes[-1]])
    allowedTag = set("div p h1 h2 h3 h4 h5 h6 span strong".strip().split())
    nodes = getAllTextNodes(root, bodyNode, allowedTag)
    scoreNodes = [(node, 0.0) for node in nodes]
    titleTag = set("h1 h2 h3 h4 h5 h6".split())
    for i, (node, score) in enumerate(scoreNodes):
        nodeText = getNodeText(node)
        
        # tag
        weight = 2.0
        ptags = getParentTagSet(node)
        if len(ptags.intersection(titleTag)) > 0:
            score += 1.0 * weight
            
        # 长度
        weight = 1.0
        if len(nodeText) > 5 and len(nodeText) < 20:
            score += 1.0 * weight
        
        # 距离
        weight = 1.0
        dist = getDistance(root, node, bodyNode)
        score += dist / 1000.0 * weight
        
        # 中文字符数
        weight = 1.0
        chineseCount = len(nodeText) - letterCount(nodeText)
        if chineseCount > 5:
            score += 1.0 * weight
        
        scoreNodes[i] = (node, score)
    
    scoreNodes.reverse()
    scoreNodes.sort(cmp=lambda x, y:1 if x[1] < y[1] else -1)
    return scoreNodes[0][0].parent

def getTitle(titleNode):
    return getNodeText(titleNode)

if __name__ == "__main__":
    url = sys.argv[1]
    html = getHtml(url)
    root = BeautifulSoup(html, 'lxml')
    bodyNodes = getBodyNodes(root)
    body = getBody(bodyNodes)
    titleNode = getTitleNode(root, bodyNodes)
    title = getTitle(titleNode)
    
    print url
    print "-"*100
    print title
    print "-"*100
    print body

