"""
==========================
Utility
==========================
Created on June 26, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide utility class for user to call function.
"""

import configparser

'''
@Function: Manage configuration setting in config.txt file.   
''' 
class UserConfig(object):
    
    def __init__(self):  
        #new a RawConfigParser Objects
        self.myconfig = configparser.RawConfigParser()
        
        #read data from config file
        self.configFilePath = r'Config.txt'

    def getOpencvData(self):
        self.myconfig.read(self.configFilePath)
        _data = self.myconfig.get('Opencv-config', 'opencv_data')
        return _data
    
    def setOpencvData(self,_data):
        self.myconfig.read(self.configFilePath)
        self.myconfig.set('Opencv-config', 'opencv_data', _data)
        self.myconfig.write(open(self.configFilePath, 'w'))


if __name__ == "__main__":

    userconfig = UserConfig()
    
    print(userconfig.getOpencvData()) 
    #userconfig.setOpencvData("D:\ProgramFiles\opencv\sources\data")
    #print(userconfig.getOpencvData()) 
    

    