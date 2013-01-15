#coding=utf-8
#author:u'王健'
#Date: 13-1-6
#Time: 下午8:18
__author__ = u'王健'


aa={"11":"A \u80a1","12":"B \u80a1","13":"\u6743\u8bc1","14":"\u671f\u8d27","15":"\u503a\u5238","21":"\u5f00\u57fa","22":"ETF","23":"LOF","24":"\u8d27\u57fa","25":"QDII","26":"\u5c01\u57fa","31":"\u6e2f\u80a1","32":"\u7a9d\u8f6e","33":"\u6e2f\u6307\u6570","41":"\u7f8e\u80a1","42":"\u5916\u671f"}
l=[]
for k in aa.keys():
    print '"%s":"'%k,
    names=aa[k].split('\\')
    for c in names:
        if len(c)==0:
            continue
        if c[0]=='u':
            print 'u"\\'+c+'"',
            l.append(c)
        else:
            print c,
    print '"',
print ''
print l
for c in l:
    print '"%s":u"\\%s",'%(c,c),
print '\n'

charmap={"u80a1":u"\u80a1", "u8d27":u"\u8d27", "u57fa":u"\u57fa", "u6743":u"\u6743", "u8bc1":u"\u8bc1", "u80a1":u"\u80a1", "u503a":u"\u503a", "u5238":u"\u5238", "u671f":u"\u671f", "u8d27":u"\u8d27", "u6e2f":u"\u6e2f", "u6307":u"\u6307", "u6570":u"\u6570", "u7a9d":u"\u7a9d", "u8f6e":u"\u8f6e", "u6e2f":u"\u6e2f", "u80a1":u"\u80a1", "u5916":u"\u5916", "u671f":u"\u671f", "u5c01":u"\u5c01", "u57fa":u"\u57fa", "u7f8e":u"\u7f8e", "u80a1":u"\u80a1", "u5f00":u"\u5f00", "u57fa":u"\u57fa"}
str=''
for k in aa.keys():
    str+= '"%s":"'%k
    names=aa[k].split('\\')
    for c in names:
        if len(c)==0:
            continue
        if c[0]=='u':
            str+= charmap[c]
        else:
            str+= c
    str+= '",'

print '\n'

print "{"+str[:-1].replace(' ','')+"}"

chardict={"11":"A股","24":"货基","13":"权证","12":"B股","15":"债券","14":"期货","22":"ETF","23":"LOF","33":"港指数","32":"窝轮","31":"港股","42":"外期","26":"封基","41":"美股","25":"QDII","21":"开基"}
for k in chardict:
    print k,':',chardict[k]

