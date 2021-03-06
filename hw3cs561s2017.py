import math
import copy
from copy import deepcopy
from decimal import *
import sys

file_read = open('input00.txt', 'r')
file_write = open('output.txt', 'w')
query_flag = 0
input_val = []

output_query = []
utility = []
dec_network = []
table = {}
bayesNet = []
orgBayesNat = []
file_log = ""
eutility = {}
cutBayesNet = set()

dec_graph = {}
for line in file_read.read().strip().split("\n"):
    if line == "******" and not query_flag:
        output_query = input_val
        input_val = []
        query_flag = 1
    elif line == "******" and query_flag:
        dec_network = input_val
        input_val = []
    else:
        input_val.append(line)

if input_val and dec_network:
    utility = input_val
elif input_val:
    dec_network = input_val

new_var = 1
new_lst = []
name = ""
for dec in dec_network:
    if dec == "***":
        new_var = 1
        table[name] = new_lst
        new_lst = []
    elif new_var == 1:
        new_var = 0
        # dec = ''.join(dec.split())
        i = 0
        for ele in list(dec.split()):
            if i == 0:
                name = ele
                orgBayesNat.insert(0, name)
            if i > 1:
                new_lst.append(ele)
            i += 1
        dec_graph[name] = new_lst
        new_lst = []
    else:
        # dec = ''.join(dec.split())
        new_lst.append(dec.split())

if new_lst:
    table[name] = new_lst

flag = 0
rest = []
name = []
for x in utility:
    if flag == 0:
        first = x.split('|')
        name = first[1].split()
        flag = 1
    else:
        rest.append(x.split())
eutility["nodes"] = name
eutility["values"] = rest


def Prb(var, val, e):
    parents = dec_graph[var]
    if len(parents) == 0:
        truePrb = table[var][0][0]
    else:
        parentVals = []
        for parent in parents:
            parentVals.append(e[parent])
        var_table = table[var]
        count = len(parentVals)
        for tab in var_table:
            itr = 0
            flag = 1
            while itr < count:
                if tab[itr+1] != parentVals[itr]:
                    flag = 0
                    break
                itr += 1
            if flag:
                truePrb = tab[0]
    if truePrb == 'decision':
        return 1.0
    if val == '+':
        return float(truePrb)
    else:
        return 1.0 - float(truePrb)


def normalize(QX):
    tot = 0.0
    for val in QX.values():
        tot += val
    if not (1.0 - 0.001 < tot < 1.0 + 0.001):
        for key in QX.keys():
            QX[key] /= tot
    return QX


def enumerateAll(evars, e):
    if len(evars) == 0:
        return 1.0
    Y = evars.pop()

    if Y in e:
        val = Prb(Y, e[Y], e)
        if val != 0:
            enum_val = enumerateAll(evars, e)
            val *= enum_val
        evars.append(Y)
        return val
    else:
        total = 0
        e[Y] = '+'
        val = Prb(Y, '+', e)
        if val != 0:
            enum_val = enumerateAll(evars, e)
            val *= enum_val
        total += val

        e[Y] = '-'

        # total += Prb(Y, '-', e) * enumerateAll(evars, e)
        val = Prb(Y, '-', e)
        if val != 0:
            enum_val = enumerateAll(evars, e)
            val *= enum_val
        total += val

        del e[Y]
        evars.append(Y)
        return total


def enumeration_ask(X, e, bn):
    QX = {}
    parents = dec_graph[X]
    if len(parents) == 0:
        truePrb = table[X][0][0]
        if truePrb == 'decision':
            QX['-'] = 1.0
            QX['+'] = 1.0
            return QX

    # bayesNet = deepcopy(orgBayesNat)
    # temp_query = deepcopy(new_query)
    # temp_bn = set()
    # lst = temp_query.strip().split("|")
    # for lt in lst[0].strip().split(','):
    #     x_split = lt.strip().split()
    #     temp_bn.add(x_split[0])
    # if len(lst) > 1:
    #     for lt in lst[1].strip().split(","):
    #         x_split = lt.strip().split()
    #         temp_bn.add(x_split[0])
    #
    # for node in eutility["nodes"]:
    #     temp_bn.add(node)
    #
    # for node in temp_bn:
    #     cutBayesNet.add(node)
    #     addToCut(node)
    #
    # toRemove = []
    # for node in bayesNet:
    #     if node not in cutBayesNet:
    #         toRemove.append(node)
    #
    # for ele in toRemove:
    #    bayesNet.remove(ele)

    for xi in ['-', '+']:
        e[X] = xi
        QX[xi] = enumerateAll(bn, e)
        del e[X]

    return normalize(QX)


def sendForEnumerationAsk(x_split, edict):
    QX = {}
    if x_split[2] == '+':
        QX = enumeration_ask(x_split[0], edict, bayesNet)
        edict.update({x_split[0]: '+'})
        return QX['+']
    else:
        QX = enumeration_ask(x_split[0], edict, bayesNet)
        edict.update({x_split[0]: '-'})
        return QX['-']


def findProbability(query):
    global file_log
    lst = query.strip().split("|")
    value = 1.0;
    ovar = lst[0].split(',')
    if len(lst) > 1:
        e = lst[1].strip().split(",")
        edict = dict((x.strip()[0], '+' if x.strip()[4] == '+' else '-') for x in e)
        for x in ovar:
            x_split = x.split()
            value *= sendForEnumerationAsk(x_split, edict)
        file_log += '\n'
        file_log += str(Decimal(str(value)).quantize(Decimal('.01')))
    else:
        edict = {}
        for x in ovar:
            x_split = x.split()
            value *= sendForEnumerationAsk(x_split, edict)
        file_log += '\n'
        file_log += str(Decimal(str(value)).quantize(Decimal('.01')))
    return


def update_split_value(x_split, dict_ele):
    if x_split[2] == '+':
        dict_ele.update({x_split[0]: '+'})
    else:
        dict_ele.update({x_split[0]: '-'})


def findExpectedUtility(query):
    global eutility
    global file_log
    dict_ele = {}
    prob = 0

    lst = query.strip().strip().split("|")
    for x in lst[0].strip().split(','):
        x_split = x.strip().split()
        update_split_value(x_split, dict_ele)

    if len(lst) > 1:
        for x in lst[1].strip().split(","):
            x_split = x.strip().split()
            update_split_value(x_split, dict_ele)
    util_nodes = eutility["nodes"]
    util_values = eutility["values"]

    for val in util_values:
        newQuery = []
        itr = 1
        newDict = deepcopy(dict_ele)
        flag = 0
        for node in util_nodes:
            tempQuery = []
            tempQuery.append(node)
            tempQuery.append(' ')
            tempQuery.append(val[itr])
            # newQuery[node] = val[itr]
            if node in dict_ele:
                if val[itr] != dict_ele.get(node):
                    flag = 1
                    break
            itr += 1
            newQuery.append(tempQuery)
        if flag == 1:
            continue;
        value = 1
        for q in newQuery:
            value *= sendForEnumerationAsk(q, newDict)
        prob += value * int(val[0])
    prob += + 0.00000001
    file_log += '\n'
    file_log += str(int(round(prob)))

    return


def decisionPosbVal(type):
    if type == 1:
        return [['+'],['-']]
    elif type == 2:
        return [['+','-'],['+','+'],['-','-'],['-','+']]
    else:
        return [['+', '+', '+'], ['+', '+', '-'], ['+', '-', '+'], ['+', '-', '-'], ['-', '+', '+'], ['-', '+', '-'], ['-', '-', '+'], ['-', '-', '-']]


def findMaxExpectedUtility(query):
    global eutility
    global file_log
    dict_ele = {}
    outputDict = {}
    decisionNode = []
    prob = 0

    lst = query.strip().strip().split("|")
    first_part =  lst[0].strip().split(',')
    if len(lst) > 1:
        for x in lst[1].strip().split(","):
            x_split = x.strip().split()
            update_split_value(x_split, dict_ele)

    dec_count = 0
    for tab in table:
        if table[tab][0][0] == "decision":
            decisionNode.insert(0, tab)
            dec_count += 1
    oldProb = -sys.maxint - 2
    for pos in decisionPosbVal(dec_count):
        itr = 0

        for dec in decisionNode:
            x_split = []
            x_split.append(dec.strip())
            x_split.append(" ")
            x_split.append(pos[itr])
            update_split_value(x_split,dict_ele)
            itr += 1
        value = 1
        prob = 0
        util_nodes = eutility["nodes"]
        util_values = eutility["values"]

        for val in util_values:
            newQuery = []
            itr = 1
            flag = 0
            newDict = deepcopy(dict_ele)
            for node in util_nodes:
                tempQuery = []
                tempQuery.append(node)
                tempQuery.append(' ')
                tempQuery.append(val[itr])
                # newQuery[node] = val[itr]
                if node in dict_ele:
                    if val[itr] != dict_ele.get(node):
                        flag = 1
                        break
                itr += 1
                newQuery.append(tempQuery)
            if flag == 1:
                continue;
            value = 1
            for q in newQuery:
                value *= sendForEnumerationAsk(q, newDict)
            prob += value * int(val[0])
        if (oldProb < prob):
            oldProb = prob
            inspect_ele = eutility["nodes"]
            for finval in first_part:
                outputDict.update({finval.strip(): dict_ele.get(finval.strip())})
                if inspect_ele:
                    new_var = inspect_ele[0]
    prob_str = ""
    for finval in first_part:
        inspect_ele = eutility["nodes"]
        if outputDict.get(finval.strip()) == '+':
            prob_str += '+' + ' '
            if inspect_ele:
                new_var = inspect_ele[0]
        else:
            prob_str += '-' + ' '
            if inspect_ele:
                new_var = inspect_ele[0]
    oldProb += 0.00000001
    prob_str += str(int(round(oldProb)))
    file_log += '\n'
    file_log += prob_str
    return


def addToCut(ele):
    lst = dec_graph[ele]
    if not lst:
        return
    for l in lst:
        cutBayesNet.add(l)
        addToCut(l)


qtype = ""
new_query = ""
for query in output_query:
    flag = 0
    i = 0
    while 1:
        if query[i] == '(':
            flag = 1
        elif flag == 0:
            qtype += query[i]
        elif flag == 1:
            if query[i] == ')':
                break
            if query[i] != "=" or (query[i-1] != "=" and query[i] != " "):
                new_query += query[i]
        i += 1

    bayesNet = deepcopy(orgBayesNat)
    temp_query = deepcopy(new_query)
    temp_bn = set()
    lst = temp_query.strip().split("|")
    for lt in lst[0].strip().split(','):
        x_split = lt.strip().split()
        temp_bn.add(x_split[0])
    if len(lst) > 1:
        for lt in lst[1].strip().split(","):
            x_split = lt.strip().split()
            temp_bn.add(x_split[0])

    if qtype != 'P':
        for node in eutility["nodes"]:
            temp_bn.add(node)

    for node in temp_bn:
        cutBayesNet.add(node)
        addToCut(node)

    toRemove = []
    for node in bayesNet:
        if node not in cutBayesNet:
            toRemove.append(node)

    for ele in toRemove:
        bayesNet.remove(ele)

    if qtype == 'P':
        findProbability(new_query)
    elif qtype == 'EU':
        findExpectedUtility(new_query)
    elif qtype == 'MEU':
        findMaxExpectedUtility(new_query)
    qtype = ""
    new_query = ""
print "Final Output: ", file_log

file_write.write(file_log[1:])