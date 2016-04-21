import Tkinter as tk
import tkFileDialog as filedialog
import tkSimpleDialog as simpledialog
import re
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'meta_file_reader'))
sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'python_dialogs'))
from read_meta_file import read_meta_file
from getCollars import *
from getDir import getDir

import fileinput
import shutil

from newFrequencyPanel import frequencyPanel


class newDataEntryPanel(tk.Frame):
    #TODO: Need to add functionality for collecting collar frequencies
    buttonColor = "#CCCCCC"
    doCalculations = 0

    updatedFrequencyList = []
    #to be used in tandem with getCollarFrequencies
    def __init__(self, parent, width, color, calculationHandler):
        self.bgcolor = color
        self.parent = parent
        data_dir = tk.StringVar()
        tk.Frame.__init__(self, parent, bg = self.bgcolor)
        self.width = width
        self.doCalculations = calculationHandler

        #pack frames in order
        self.currframe = tk.Frame(self)
        self.currframe.pack(side = "left")
        self.botframe = tk.Frame(self)
        self.botframe.pack(side = "bottom")

        self.initializeWidgets()
        #TODO: decide where CONFIGCOLPath file is written to
        #Probably in toplevel

        #self.config(bg=self.bgcolor)

        self.update()

    def initializeWidgets(self):
        self.dirFrame = directoryPanel(self.currframe, self.width, self.bgcolor, self.initializeFields)
        self.runFrame = runIDPanel(self.currframe, self.width, self.bgcolor)
        self.altFrame = altitudePanel(self.currframe, self.width, self.bgcolor)
        self.colFrame = frequencyPanel(self.currframe, self.width, self.bgcolor)
        self.calculateButton = tk.Button(self.currframe, text = 'Calculate', command = self.prepareForCalc, bg = self.buttonColor)


        self.dirFrame.grid(row=0,column=0,sticky="nw")
        self.runFrame.grid(row=1,column=0,sticky="nw")
        self.altFrame.grid(row=2,column=0,sticky="nw")
        self.colFrame.grid(row=3,column=0,sticky="nw")
        self.calculateButton.grid(row=4,column=0,sticky="w")


    def prepareForCalc(self):
        proceed = 1;
        dirTBPath = self.dirFrame.getDirectory()
        print("dirTBPath is: %s" %(dirTBPath))
        if(os.path.isdir(dirTBPath) != 1):
            proceed=0

        inString = self.runFrame.getRunID()
        runValue = 0
        try:
            runValue = int(inString)
        except ValueError:
            runValue = 0

        if(runValue == 0):
            proceed=0

        inString = self.altFrame.getAlt()
        altValue = 0

        try:
            altValue = int(inString)
        except ValueError:
            altValue = 0


        if(altValue == 0):
            proceed=0



        frequencyList = self.colFrame.getCollarFrequencies()


        self.updatedFrequencyList = frequencyList


        i = 0
        while i < len(frequencyList ):
            print(frequencyList[i])
            i = i+1

        colValue = 0
        try:
            colValue = len(frequencyList)
        except ValueError:
            colValue = 0

        if(colValue == 0):
            proceed=0




        if(proceed == 1):
            #prepares the config file for calculations
            self.prepareConfigCOLFile(dirTBPath)
            self.doCalculations(dirTBPath,runValue,altValue,colValue,frequencyList);

    def initializeFields(self):
        #This function is called by the directoryPanel when a new directory is set
        self.updatedFrequencyList = []

        data_dir = self.dirFrame.getDirectory()

        #TODO: Move these out to their own .py files
        RUNPath = data_dir + '/RUN'
        ALTPath = data_dir + '/ALT'
        COLPath = data_dir + '/COL'

        run = 0; alt = 0; col = 0;
        if os.path.exists(RUNPath):
            run = read_meta_file(RUNPath, 'run_num')

        if os.path.exists(ALTPath):
            alt =  read_meta_file(ALTPath, 'flt_alt')

        if os.path.exists(COLPath):
            self.updatedFrequencyList = getOldCollarsClean(COLPath);


        self.runFrame.setRunID(run)
        self.altFrame.setAlt(alt)
        self.colFrame.setCollarFrequencies(self.updatedFrequencyList)



    def prepareConfigCOLFile(self,data_dir):

        COLPath = data_dir + '/COL'
        CONFIGPath = os.path.dirname(os.path.realpath(__file__))
        CONFIGPath = CONFIGPath.replace("\\","/")
        lastIndex = CONFIGPath.rindex('/')
        CONFIGPath = CONFIGPath[0:lastIndex]
        programPath = CONFIGPath
        CONFIGPath = CONFIGPath + '/config'
        ConfigCOLPath = CONFIGPath + '/COL'
        col = 0

        if(len(self.updatedFrequencyList) == 0):
            if os.path.exists(COLPath):
                shutil.copyfile(COLPath,ConfigCOLPath)
        else: #frequency list was updated, use these values
            with open(ConfigCOLPath,'w') as concolFile:
                print("len(self.updatedFrequencyList) = %d" %(len(self.updatedFrequencyList)))
                while col < len(self.updatedFrequencyList):
                    concolFile.write("%d: %s\n" %(col+1,self.updatedFrequencyList[col]))
                    col = col+1


class directoryPanel(tk.Frame):
    buttonColor = '#CCCCCC'
    data_dir = ""
    def __init__(self, parent, width, color, updateDirectoryFunction):
        self.bgcolor = color
        self.parent = parent;
        tk.Frame.__init__(self, parent, width = width, bg = color)
        self.updateDirFunc = updateDirectoryFunction
        self.initializeWidgets()

    def initializeWidgets(self):
        self.dirText = tk.Label(self, text = "Data Directory/Folder", bg = self.bgcolor)
        self.dirTB = tk.Entry(self, width = 29)
        self.selectDirButton = tk.Button(self, text = '...', command = self.updateDirectory, width = 3, bg = directoryPanel.buttonColor)

        self.dirText.grid(row=0,column=0,sticky="w")
        self.dirTB.grid(row=0,column=1,sticky="w")
        self.selectDirButton.grid(row=0,column=2,sticky="w")

    def updateDirectory(self):
        #self.dirTB.config(state='normal')
        self.data_dir = getDir() #'C:/Users/Work/Documents/Files/Projects/RadioCollar/SampleData/RCT_SAMPLE/RUN_002027-copy'\
        #self.parent.parent.quitter()
        self.dirTB.delete(0, 'end')
        self.dirTB.insert(0, self.data_dir)
        #Decided not to disable dirTB

        self.updateDirFunc()

    def getDirectory(self=None):
        return self.data_dir

class runIDPanel(tk.Frame):
    bgcolor = 0
    runID = 0
    runIDText = 0
    runIDTB = 0
    #errorText = 0
    def __init__(self,parent,width,color):
        self.bgcolor = color
        tk.Frame.__init__(self,parent,width=width,bg=color)
        self.initializeWidgets()

    def initializeWidgets(self):
        self.runID = tk.StringVar()
        self.runID.trace("w", lambda name, index, mode, runID = self.runID.get() : self.changeRunID())

        self.runIDText = tk.Label(self, text = "Run ID: ", width = 12, bg = self.bgcolor)
        self.runIDTB = tk.Entry(self,width = 23, textvariable = self.runID)

        #self.errorText = tk.Text(self,height=1,width = 23,bd=0,bg=self.bgcolor)
        #self.errorText.insert('insert','Please input an integer')
        #self.errorText.config(bg=self.bgcolor)
        #self.errorText.config(foreground=self.bgcolor)

        self.runIDText.grid(row=0,column=0,sticky="w")
        self.runIDTB.grid(row=0,column=1,sticky="w")
        #self.errorText.pack(side='left',padx=3)

    def setRunID(self,newID='-1'):
        #Changing this should call changeRunID automatically
        self.runID.set(newID)


    def changeRunID(self=None):
        run = -1
        try:
            run = int(self.runID.get())
        except ValueError:
            run = -1
        print('run = %d' %(run))
        if run < 0:
            #self.errorText.config(foreground='red')
            self.runIDTB.config(bg='red')
            #self.runID.set('-1')

        else:
            #self.runID.set(newID)
            self.runIDTB.config(bg='white')
            #self.errorText.config(foreground=self.bgcolor)


    def getRunID(self=None):
        return self.runID.get()

class altitudePanel(tk.Frame):
    bgcolor = 0
    alt = 0
    altText = 0
    altTB = 0
    #errorText = 0
    def __init__(self,parent,width,color):
        self.bgcolor = color
        tk.Frame.__init__(self,parent,width=width,bg=color)
        self.initializeWidgets()

    def initializeWidgets(self):
        self.alt = tk.StringVar()
        self.alt.trace("w", lambda name, index, mode, alt=self.alt.get(): self.changeAlt())

        self.altText = tk.Label(self,text="Run altitude: ",width=12,bg=self.bgcolor)
        self.altTB = tk.Entry(self,width = 23,textvariable=self.alt)

        #self.errorText = tk.Text(self,height=1,width = 23,bd=0,bg=self.bgcolor)
        #self.errorText.insert('insert','Please input an integer')
        #self.errorText.config(bg=self.bgcolor)
        #self.errorText.config(foreground=self.bgcolor)

        self.altText.grid(row=0,column=0,sticky="w")
        self.altTB.grid(row=0,column=1,sticky="w")
        #self.errorText.pack(side='left',padx=3)

    def setAlt(self,newalt='-1'):
        #Changing this should call changeRunID automatically
        self.alt.set(str(newalt))


    def changeAlt(self=None):
        alt = -1
        try:
            alt = int(self.alt.get())
        except ValueError:
            alt = -1

        if alt < 0:
            #self.errorText.config(foreground='red')
            self.altTB.config(bg='red')
            #self.alt.set ('-1')

        else:
            #self.alt.set(newID)
            self.altTB.config(bg='white')
            #self.errorText.config(foreground=self.bgcolor)

    def getAlt(self=None):
        return self.alt.get()

class collarFreqPanel(tk.Frame):
    buttonColor = '#CCCCCC'
    frequencyList = []
    num_cols = 0
    num_colsTB = 0
    updateFrequenciesButton = 0
    #collarFrequencyList = 0 #Saro's object, wait till get working

    def __init__(self,parent,width,color):
        self.bgcolor = color
        tk.Frame.__init__(self,parent,width=width,bg=color)
        self.initializeWidgets()


    def initializeWidgets(self):
        self.num_cols = tk.StringVar()

        self.num_colsText = tk.Text(self,height=1,width = 15,bd=0,bg=self.bgcolor)
        self.num_colsTB = tk.Entry(self,width = 8,textvariable=self.num_cols)
        #self.errorText = tk.Text(self,height=1,width = 23,bd=0,bg=self.bgcolor)
        self.updateFrequenciesButton = tk.Button(self,text='View Collar Frequencies',command=self.getNewFreqs,bg=self.buttonColor)

        self.num_colsText.insert('insert','Num. Collars: ')
        #self.errorText.insert('insert','Please select at least 1 collar frequency')

        #self.errorText.config(bg=self.bgcolor)
        #self.errorText.config(foreground=self.bgcolor)

        self.num_colsTB.config(state='disabled')

        self.num_colsText.pack(side = 'left',padx=3)
        self.num_colsTB.pack(side='left')
        self.updateFrequenciesButton.pack(side='bottom',padx=5)
        #self.errorText.pack(side='left',padx=3)

        #collarFrequencyList must be called after everything else

        #self.collarFrequencyList = frequencyPanel(self)
        #self.collarFrequencyList.pack(side='bottom',pady=3)

    def getNewFreqs(self):
        print("inGetNewFreqs")
        frequencyArray = getNewCollarsClean()
        self.setNewFreqs(frequencyArray)



    def setNewFreqs(self,newFrequencyList):
        self.frequencyList = newFrequencyList
        num_col = len(newFrequencyList);


        if num_col < 1:
            self.num_colsTB.config(bg='red',state='normal')
            self.num_colsTB.delete(0, 'end')
            self.num_colsTB.insert(0,0)
            self.num_colsTB.config(state='disabled')
        else:
            self.num_colsTB.config(state='normal')
            self.num_colsTB.delete(0, 'end')
            self.num_colsTB.insert(0,num_col)
            self.num_colsTB.config(bg='white',state='disabled')


    def getCollarFrequencies(self=None):
        return self.frequencyList


