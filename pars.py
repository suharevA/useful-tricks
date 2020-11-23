#!/usr/bin/env python
import sys, os

def head():
    file = '/src/settings/'
    author = ''
    name = ''
    pa = os.path.dirname(file)
    s = ' --------------'
    shap = "{}\n @author: {}\n @name: {}\n @path: {}\n".format(s,author,name,pa)
    return shap

def main():
    folder = sys.argv[1] # argument contains path
    with open('result.txt', 'a') as result: # result file will be in current working directory
        for path in os.walk(folder).next()[2]: # list all files in provided path
            with open(os.path.join(folder, path), 'r') as source:
                result.write(head() +"\n" + source.read() + "\n") # write to result eachi file

main()
