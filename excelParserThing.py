from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QScrollArea, QMessageBox, QSizePolicy
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
import sip
from openai import OpenAI

import pandas as pd
import sys
import re
import os
import random


client = OpenAI(
    api_key='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'
)

positionList = [""]

#dictionary with codes for sexes
sexTrans = {"Unknown": 3, "Male": 1, "Female": 2, "Could be Either": 4, "Probably Male": 5, "Probably Female": 6}

#instrument codes
instrumentTrans = { "Plz Fill me in" : 0, "First Violin": 1, "First Violin & Percussion, Including Keyboard" : 1.1, "Second Violin" : 2, "Second Violin & Keyboard Instruments" : 2.1, "Second Violin & Percussion" : 2.2, "Violas" : 3, 
                   "Violas & Piano & Celeste": 31, "Violas & Celeste" : 32, "Violas & Organ": 33, "Cello / Violoncello" : 4, "Cello & Fretted Instruments" : 41, "Cello & Keyboard Instruments" : 42,
                   "Bass" : 5, "Basses & Percussion" : 51, "Harps" : 6, "Harps & Keyboard" : 61, "Flutes" : 7, "Piccolo & Flutes" : 71, "Piccolo Only"  : 72, "Oboes" : 8, "English Horns & Other Oboes" : 81, 
                   "Only English Horn" : 82, "Clarinet" : 9, "Clarinet & Bass Clarinet" : 91, "Bass Clarinet Only" : 92, "EFlat Clarinet & Clarinets" : 93, "EFlat Clarinet Only" : 94, "EFlat Clarinet & Bass Clarinet" : 95,
                   "Bass Clarinet & Saxophone" : 96, "Clarinet & Saxophone" : 97, "Clarinet & piano & celesta" : 98, "Clarinet, Piano, Celesta, & Saxophone" : 99, "Bassoons" : 10, "Bassoons & Contra Bassoon" : 101, 
                   "Contra Bassoon Only" : 102, "Horn ( & French Horn)" : 11, "Wagnerian Tuben & Horns" : 111, "Wagnerian Tuben Only" : 112, "Trumpet" : 12, "Trumpet & Second Violin" : 121, "Bass Trumpet & Trumpets" : 122, 
                   "Bass Trumpet Only" : 123, "Trumpets & Cornets" : 124, "Trumpets & Percussion" : 125, "Trombones" : 13, "Trombones & Bass Trombone" : 131, "Bass Trombone Only" : 132, "Trombones & Bass Trumpet" : 133, 
                   "Tuba" : 14, "Percussion" : 15, "Percussion & Tympani" : 151, "Tympani Only" : 152, "Percussion, Piano & Celeste" : 153, "Piano" : 16, "Piano & Celeste or other keyboard Instruments" : 161, "Celeste" : 17,
                   "Organ" : 18, "Saxophones" : 19, "Keyboard" : 20, "Fretted Instruments" : 21
                   }

#special position codes
positionTrans = { "None" : "", "Principal": 1, "Concertmaster" : 1, "Associate Principal" : 2, "Associate Concertmaster" : 2, "Assistant Principal" : 3, "Assistant Concertmaster" : 3, "Acting Principal" : 4, "Acting Concertmaster" : 4, 
                 "Acting Assistant Concermaster" : 5, "Acting Assistant Principal" : 5, "Acting co-Concertmaster" : 6, "Concertmaster Emeritus" : 10, "Principal Emeritus" : 10, "Substitute Musician" : 11, "Leave of Absence / Sabbatical" : 12,
                 "Orchestra Fellow" : 13, "Alternate" : 14, "Apprentice Conductor" : 15, "Guest Concertmaster" : 16, "Guest Principal" : 16, "Guest" : 17, "Concertmaster Laureate" : 18, "Principal Laureate" : 18, "Alternating Principals" : 19,
                 "In italics" : 20
                }

#class that stores musican data in a close-to-desired format to be cast into excel
class Musician():
    def __init__(self):
        firstCatList = ["Last Name", "First Name", "Sex1", "Sex2"]
        yearsList = []
        data = ["", "", "", ""]
        for i in range(1881, 2023, 1):
            yearsList.append("I" + str(i) + "-" + str(i + 1))
            yearsList.append("P" + str(i) + "-" + str(i + 1))
            data.append("")
            data.append("")
        indices = firstCatList + yearsList
        self.data = pd.Series(data, index = indices)


#Parent class kind of of the widgets that display information imported from the excel sheet
class ImportedInfoBox(QWidget):
    def __init__(self, name, data, horizontal = True):
        super().__init__()
        
        layout = QVBoxLayout()
        if(horizontal):
            layout = QHBoxLayout()

        self.title = QtWidgets.QLabel()
        self.title.setText(name)
        self.title.setStyleSheet("background-color: lightgreen")
        self.title.setAlignment(Qt.AlignTop)
        print(self.title.sizeHint())
        print(self.title.sizePolicy())
        self.title.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        # self.title.setMaximumHeight(50)
        layout.addWidget(self.title)

        self.dataB = QtWidgets.QLabel()
        if(not horizontal):
            self.dataB.setWordWrap(True)
        self.dataB.setText(data)
        self.dataB.setAlignment(Qt.AlignTop)
        layout.addWidget(self.dataB)
        

        self.setLayout(layout)
        if horizontal: 
            self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
            self.dataB.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)

        else:
            self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            self.dataB.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
    
    #changes displayed information to data
    def updateData(self, data):
        self.dataB.setText(str(data))

    #returns the text stored in that section
    def returnData(self):
        return self.dataB.text()


#defines the building block widget that is used in user input side
class LabelInputPair(QWidget):
    def __init__(self, name, isInt = False):
        super().__init__()
        self.name = name
        layout = QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText(name)
        layout.addWidget(label)
        self.input = QtWidgets.QLineEdit()
        if(isInt):
            self.input.setValidator(QIntValidator())
        layout.addWidget(self.input)

        self.setLayout(layout)

    #returns information the user input
    def getInfo(self, isInt = False):
        if(isInt):
            try: 
                return int(self.input.text().strip())
            except: 
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Incorrect Data Type")
                msg.setInformativeText(self.name + " entry expects a number but got a string")
                msg.setWindowTitle("Error")
                msg.exec_()
        else:
            return self.input.text().strip()
    
    #clears the input region 
    def clear(self):
        self.input.clear()


#another building block widget that has the dropdown used for like sex and instrument and position and stuff
class LabelDropdownPair(QWidget):
    def __init__(self, name, options):
        super().__init__()

        layout = QHBoxLayout()

        label = QtWidgets.QLabel()
        label.setText(name)
        layout.addWidget(label)

        self.options = list(options)
        self.dropDown = QComboBox()
        self.dropDown.addItems(options)
        self.dropDown.setCurrentText("None")
        layout.addWidget(self.dropDown)

        self.setLayout(layout)

    #returns the selected option from the dropdown as a string
    def getInfo(self):
        return self.dropDown.currentText()

    #clears the dropdown selected option
    def clear(self):
        self.dropDown.setCurrentText(self.options[0])

#Defines the individual era widget  code
class ComplexData(QWidget):
    def __init__(self, num):
        super().__init__()
        layout = QVBoxLayout()
        
        sectionTitle = QtWidgets.QLabel()
        sectionTitle.setText("Era " + str(num))
        sectionTitle.setStyleSheet("background-color: lightgreen")
        sectionTitle.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        layout.addWidget(sectionTitle)

        startYr = LabelInputPair("Start Year: ", True)
        layout.addWidget(startYr)
        startYr.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.startYr = startYr

        endYr = LabelInputPair("End Year: ", True)
        layout.addWidget(endYr)
        endYr.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.endYr = endYr

        instrumentChoice = LabelDropdownPair("Instrument (choose one): ", instrumentTrans.keys())
        layout.addWidget(instrumentChoice)
        self.instrumentChoice = instrumentChoice

        positionChoice = LabelDropdownPair("Position", positionTrans.keys())
        layout.addWidget(positionChoice)
        self.positionChoice = positionChoice

        self.setLayout(layout)
    
    def getInfo(self):
        data = {
            "Start": self.startYr.getInfo(),
            "End" : self.endYr.getInfo(),
            "Instr" : self.instrumentChoice.getInfo(),
            "Position" : self.positionChoice.getInfo()
        }
        return data
        
        







class InputData(QWidget):
    def __init__(self):
        super().__init__()

        self.fName = LabelInputPair("First Name: ")
        self.lName = LabelInputPair("Last Name: ")
        self.sex = LabelDropdownPair("Sex", sexTrans.keys())
        self.eras = ActiveEras()
        self.addButton = QtWidgets.QPushButton("Add Era")
        self.remButton = QtWidgets.QPushButton("Remove Era")
        self.remButton.clicked.connect(self.remEra)


        topLayout = QVBoxLayout()
        
        topLayout.addWidget(self.fName)

        topLayout.addWidget(self.lName)

        topLayout.addWidget(self.sex)

        topLayout.addWidget(self.eras)
        
        self.addButton.clicked.connect(self.addEra)

        btnLayoutWidget = QWidget()
        btnLayout = QHBoxLayout()
        btnLayoutWidget.setLayout(btnLayout)

       

        btnLayout.addWidget(self.addButton)
        btnLayout.addWidget(self.remButton)

        topLayout.addWidget(btnLayoutWidget)

        self.setLayout(topLayout)


    def returnData(self):
        toRet = {"fn": self.fName.getInfo(), 
                 "ln": self.lName.getInfo(), 
                 "sex": self.sex.getInfo(),
                 "eras": self.eras.getInfo()}
        return toRet

    
    def addEra(self):
        self.eras.addEra()

    def remEra(self):
        self.eras.remEra()
    
    def resetEras(self):
        self.eras.reset()
    
    def clearInputs(self):
        self.resetEras()
        self.fName.clear()
        self.lName.clear()
        self.sex.clear()


    


class ActiveEras(QScrollArea):
    def __init__(self):
        super(ActiveEras, self).__init__()
        widget = QWidget()
        self.layout = QVBoxLayout(widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.eras = []
        
        newEra = ComplexData(1)
        self.eras.append(newEra)
        self.layout.addWidget(newEra)
        
        self.setWidget(widget)
        self.setWidgetResizable(True)
        
    
    #clears out all the eras in the app
    def reset(self):
        for era in self.eras:
            self.layout.removeWidget(era)
            sip.delete(era)
        self.eras = []
        self.eras.append(ComplexData(1))
        self.layout.addWidget(self.eras[-1])

    #adds a new instrument area on the interface
    def addEra(self):
        self.eras.append(ComplexData(len(self.eras) + 1))
        self.layout.addWidget(self.eras[-1])

    #removes the most recently added instrument era on the interface
    def remEra(self):
        if(len(self.eras) > 1):
            self.layout.removeWidget(self.eras[-1])
            sip.delete(self.eras[-1])
            self.eras.pop()
    
    #
    def getInfo(self):
        info = []
        for era in self.eras:
            info.append(era.getInfo())
        return info

        



class ImportedSection(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        

        titleBox = QtWidgets.QLabel("Given data")
        # titleBox.setMaximumHeight(50)
        titleBox.setStyleSheet("background-color: lightblue")
        titleBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        layout.addWidget(titleBox)

        self.nameInfo = ImportedInfoBox("Name: ", "initialize")
        # self.nameInfo.setMaximumHeight(50)
        layout.addWidget(self.nameInfo)
        

        self.datesInfo = ImportedInfoBox("Active Dates (There can be stops in between): ", "initialize lul")
        layout.addWidget(self.datesInfo)
        # self.datesInfo.setMaximumHeight(50)

        self.orchInfo = ImportedInfoBox("For Orchestra: ", "lolxd chamber orch")
        layout.addWidget(self.orchInfo)
        # self.orchInfo.setMaximumHeight(50)

        self.instrInfo = ImportedInfoBox("Instrument / Position (Good Luck)", "initialize lul", False)
        layout.addWidget(self.instrInfo)
        

        self.setLayout(layout)

    def updateInfo(self, name, data, dates, orch):
        self.nameInfo.updateData(name)
        self.instrInfo.updateData(data)
        self.orchInfo.updateData(orch)
        self.datesInfo.updateData(dates)

    def getInfo(self):
        return self.orchInfo.returnData()




class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.df = pd.read_excel("./data.xlsx")
        self.idx = -1

        try:
            with open("./progress.txt", "r") as f:
                self.idx = int(f.read().strip())
                f.close()
        except:
            with open("./progress.txt", "w") as f:
                f.write("-1")
                f.close()
        
        
        
        
        self.setWindowTitle("Goldin's godly work")
        GivenLayout = QHBoxLayout()


        self.importedSec = ImportedSection()
        GivenLayout.addWidget(self.importedSec)

        self.inputSec = InputData()
        GivenLayout.addWidget(self.inputSec)

        # LeftTitle = QtWidgets.QLabel()
        # LeftTitle.setText("Data Given")
        # GivenLayout.addWidget(LeftTitle)

        # self.NameInfo = ImportedInfoBox("Name: ", "herro world i like coffee and cake lul xd")
        # GivenLayout.addWidget(self.NameInfo)

        # self.InstrumentInfo = ImportedInfoBox("Instrument / Position info: ", "lorem ipsum blah blah fjpasdgiopodgfiqwpeifjisojsfiapasojdfiqwjeipofjasdfljasd;fjsadfkljasdfk;asd")
        # GivenLayout.addWidget(self.InstrumentInfo)

        progressWidget = QWidget()
        progressLayout = QVBoxLayout()
        
        self.progLabel = QtWidgets.QLabel(str(self.idx) +  "/" + str(len(self.df.index)))
        progressLayout.addWidget(self.progLabel)

        self.button = QtWidgets.QPushButton("Next", self)
        self.button.clicked.connect(self.logInfo)
        progressLayout.addWidget(self.button)

        

        progressWidget.setLayout(progressLayout)
        GivenLayout.addWidget(progressWidget)
        self.setLayout(GivenLayout)


        self.nextInfoset()

    
    def logInfo(self):
        orchName = "".join(self.importedSec.getInfo().split(" "))
        fileName = "./" + orchName + ".csv"
        outFrame = None
        if(not os.path.exists(fileName)):
            f = open(fileName, "w")
            f.close()
            player = Musician()
            outFrame = pd.DataFrame(player.data).transpose()
        else: 
            try: 
                outFrame = pd.read_csv(fileName, index_col=0)
            except:
                os.rename(fileName, "recov" + str(random.randint(0, 100000)))
                f = open(fileName, "w")
                f.close()
                player = Musician()
                outFrame = pd.DataFrame(player.data).transpose()

        newPlayer = Musician()
        
        analysisData = self.inputSec.returnData()

        firstName = analysisData["fn"]
        if(firstName.strip() == ""):
            msg = QMessageBox(self)
            msg.setWindowTitle("error")
            msg.setText("be sure to fill in first name")
            msg.exec_()
            return
        lastName = analysisData["ln"]
        if(lastName.strip() == ""):
            msg = QMessageBox(self)
            msg.setWindowTitle("error")
            msg.setText("be sure to fill in last name")
            msg.exec_()
            return
        sex = sexTrans[analysisData["sex"]]
        sex1 = sexTrans[analysisData["sex"]]
        sex2 = sexTrans[analysisData["sex"]]
        eras = analysisData["eras"]

        newPlayer.data._set_value('First Name', firstName)
        newPlayer.data._set_value("Last Name", lastName)
        if sex == 3 or sex == 4 or sex == 5 or sex == 1:
            sex1 = 1
        else:
            sex1 = 2
        
        if sex == 1 or sex == 2:
            sex2 = ""

        newPlayer.data._set_value("Sex1", sex1)
        newPlayer.data._set_value("Sex2", sex2)

        for era in eras:
            if(era["Start"] == "" or era["End"] == ""):
                msg = QMessageBox(self)
                msg.setWindowTitle("error")
                msg.setText("be sure to fill in valid start and end years")
                msg.exec_()
                return

            i = int(era["Start"])
            e = int(era["End"])
            if(i < 1882 or e > 2023 or i > e):
                msg = QMessageBox(self)
                msg.setWindowTitle("error")
                msg.setText("be sure to fill in valid start and end years")
                msg.exec_()
                return
            while i < e or (int(era["Start"]) == e and i == e):
                if(instrumentTrans[era["Instr"]] == 0):
                    msg = QMessageBox(self)
                    msg.setWindowTitle("error")
                    msg.setText("be sure to choose an instrument for each era")
                    msg.exec_()
                    return
                newPlayer.data._set_value("I" + str(i) + "-" + str(i + 1), instrumentTrans[era["Instr"]])
                newPlayer.data._set_value("P" + str(i) + "-" + str(i + 1), positionTrans[era["Position"]])
                i += 1

        outFrame = pd.concat([outFrame, newPlayer.data.to_frame().T])
        outFrame.to_csv(fileName)

        with open("./progress.txt", "w") as f:
            f.write(str(self.idx))
            f.close()


        self.nextInfoset()

    def predictValues(self, name, data, orch, dates):
        try: 
            messages = [{"role" : "system", "content" : "Role: You are an assistant parsing through a database of orchestra player biographies to find out information about them, including what instruments they played at a specific orchestra and when they played them, their name, and sex."}]
            firstName = ""
            lastName = ""
            sex = ""
            bio = "Dates Active " +  dates +   " biography excerpt: " + data + " Please try your best to tell me what instruments this person played throughout their lives. If it is unclear, please try to make a guess. Please follow this format exactly and do not add words like \"assistant\" or \"principal\" or anything about the places they played. 1 word or numbers at each please: \"Era: startyear, endyear instrument, Era: start-year, end-year, instrument \"  etc. "
            messages.append({"role": "user", "content": bio})
            
            chat = client.chat.completions.create(
                model="gpt-4", messages=messages
            )
            print(chat.choices[0].message.content)
            first = True
            wordNum = 0
            pos = 0
            done = False
            collec = chat.choices[0].message.content.split(" ")
            while(wordNum < len(collec)):
                try:
                    if(collec[wordNum] == "Era:"):
                        if(not first):
                            self.inputSec.eras.addEra()
                        first = False
                        pos = 0
                        print("got here")
                    elif (pos == 1) :
                        self.inputSec.eras.eras[-1].startYr.input.setText(collec[wordNum])
                        print("got here 2")
                    elif (pos == 2):
                        self.inputSec.eras.eras[-1].endYr.input.setText(collec[wordNum])
                        print("got here 3")
                    elif (pos == 3):
                        self.inputSec.eras.eras[-1].instrumentChoice.setCurrentText(collec[wordNum])
                    elif (pos == 4):
                        self.inputSec.eras.eras[-1].positionChoice.setcurrentText(collec[wordNum])
                    wordNum += 1
                    pos += 1
                except:
                    break




            namePrompt = "Name excerpt: " + name +  " Could you tell me what this person's First and Last Name are in the following format (please follow it exactly and do not write \"First Name\" or \"Last Name\"): \"First Name, Last Name\" (If you don't know one or both of them, write idk in that field and ignore middle initials)"

            messages.append({"role": "user", "content": namePrompt})

            chat = client.chat.completions.create(
                model="gpt-4", messages = messages
            )

            print(chat.choices[0].message.content)
            
            try:
                # print(self.inputSec.fName.input.setTExt)
                self.inputSec.fName.input.setText(chat.choices[0].message.content.split(", ")[0])
                self.inputSec.lName.input.setText(chat.choices[0].message.content.split(", ")[1])
            except:
                print("lol")
            messages.append({"role": "user", "content": "Based on the biography and the name, what is the person's sex? Please respond with 1 word out of the following (no explanation needed) Male, Female, Uknown, Probably Male, or Probably Female"})
            chat = client.chat.completions.create(
                model="gpt-4", messages = messages
            )
            print(chat.choices[0].message.content)
            try:
                self.inputSec.sex.dropDown.setCurrentText(chat.choices[0].message.content)
            except:
                print("whoops3")
        except:
            print("whoops")
        



    def nextInfoset(self):
        self.idx = 0 if self.idx < 0 else self.idx + 1
        if(self.idx >= (len(self.df.index))):
            msg = QMessageBox(self)
            msg.setWindowTitle("Congrats")
            msg.setText("Congrats you're done")
            msg.exec_()
            return
        self.progLabel.setText(str(self.idx) +  "/" + str(len(self.df.index)))
        name = self.df.loc[self.idx, "Musician Name"]
        data = self.df.loc[self.idx, "Instrument"]
        orch = self.df.loc[self.idx, "Orchestra"]
        dataWords = data.split(" ")
        for i in reversed(range(len(dataWords))):
            if(dataWords[i] == "\t" or dataWords[i] == "\n" or dataWords[i] == "\t\n" or dataWords[i] == "\n\t"):
                dataWords.pop(i)
        data = ""
        for word in dataWords:
            data += (word + " ")
        dataWords = data.split("\t")
        data = ""
        for word in dataWords:
            data += word
        dates = self.df.loc[self.idx, "Dates"]
        self.importedSec.updateInfo(name, data, dates, orch)
        self.inputSec.clearInputs()
        self.predictValues(name, data, orch, dates)


    

        
        


def window():
    # openai.my_api_key = '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'
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

window()