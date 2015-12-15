import re

def getCleanRegex(regex):
    if '.*' in regex:
        regex = regex.replace('.*', '[a-z]*')
    if '/' in regex:
        regex = regex.replace('/', '\/')
    return regex

def getName(regex):
    if regex[0] != '(':
        return regex
    else:
        output = ''
        for c in regex:
            if c == '(':
                continue
            elif c == '|':
                return output
            else:
                output += c
        return regex

if __name__ == '__main__':
    with open("symptoms_regex_rough.txt") as f:
        content = f.readlines()

    clean_regexes = {}
    for i in range(0, len(content), 2):
        line = content[i]
        name, regexes = line.split(' - ')
        name = name[1:]
        for regex in regexes.strip().split(', '):
            clean_regexes[getName(regex)] = getCleanRegex(regex)

    for name in clean_regexes:
        print(name + ': ' + clean_regexes[name])



            
            
