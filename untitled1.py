#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 09:31:43 2019

@author: suharevA
Python Script to monitor disk space
"""
import subprocess

threshold = 20
partition = '/'

# поверьте название раздела df -h
result = subprocess.Popen(['df', '-h', '/dev/sda1'], stdout=subprocess.PIPE, encoding='utf-8')

for line in result.stdout:
   splitline = line.split()
   if splitline[-1] == partition:
       if int(splitline[-2][:-1]) > threshold:
           ''' Меняем на другую комманду
           
           например
           
           docker_prune = subprocess.run('docker system prune -f', shell=True)
           
           '''
           
           docker_prune = subprocess.run('df -h', shell=True)
               
   

              
                
                
    
    

            
            
    
    
    
 
