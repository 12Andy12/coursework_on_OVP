import os.path
import sqlite3
import sys
import time
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

style = os.path.join(os.path.dirname(__file__), "style.css")

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Экран загрузки')
        self.setFixedSize(1100, 500)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


        self.counter = 0
        self.n = 400 # total instance

        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.loading)
        self.timer.start(30)

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.frame = QFrame()

        layout.addWidget(self.frame)


        # pixmap = QPixmap("startImage.jpg")
        # lbl = QLabel(self)
        # lbl.setPixmap(pixmap)
        # lbl.setObjectName('Fon')
        # layout.addWidget(lbl)

        self.labelTitle = QLabel(self.frame)
        self.labelTitle.setObjectName('LabelTitle')

        # center labels
        self.labelTitle.resize(self.width() - 10, 150)
        self.labelTitle.move(0, 40) # x, y
        self.labelTitle.setText('Менеджер поездов')
        self.labelTitle.setAlignment(Qt.AlignCenter)

        self.labelDescription = QLabel(self.frame)
        self.labelDescription.resize(self.width() - 10, 50)
        self.labelDescription.move(0, self.labelTitle.height())
        self.labelDescription.setObjectName('LabelDesc')
        self.labelDescription.setText('<strong>Если волк молчит то лучше его не перебивать</strong>')
        self.labelDescription.setAlignment(Qt.AlignCenter)

        self.progressBar = QProgressBar(self.frame)
        self.progressBar.resize(self.width() - 200 - 10, 50)
        self.progressBar.move(100, self.labelDescription.y() + 130)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setFormat('%p%')
        self.progressBar.setTextVisible(True)
        self.progressBar.setRange(0, self.n)
        self.progressBar.setValue(20)

        self.labelLoading = QLabel(self.frame)
        self.labelLoading.resize(self.width() - 10, 50)
        self.labelLoading.move(0, self.progressBar.y() + 70)
        self.labelLoading.setObjectName('LabelLoading')
        self.labelLoading.setAlignment(Qt.AlignCenter)
        self.labelLoading.setText('Загрузка...')



    def loading(self):
        self.progressBar.setValue(self.counter)

        if self.counter == int(self.n * 0.2):
            self.labelDescription.setText('<strong>Паймон - лучший компаньон</strong>')
        elif self.counter == int(self.n * 0.4):
            self.labelDescription.setText('<strong>Тераформируем ландшафт</strong>')
        elif self.counter == int(self.n * 0.6):
            self.labelDescription.setText('<strong>Безумно можно быть первым ... </strong>')
        elif self.counter == int(self.n * 0.8):
            self.labelDescription.setText('<strong>Иногда жизнь — это жизнь, а ты в ней иногда</strong>')
        elif self.counter >= self.n:
            self.timer.stop()
            self.close()

            # time.sleep(1)

            self.myApp = App()
            self.myApp.show()

        self.counter += 1

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.currentTrain = "";
        self.currentWagon = "";
        self.currentPrice = "";
        self.absolutSeatNumber = 54;
        self.headerStyle = "::section:pressed {background-color: #323232;\nborder: none;}\n::section {background-color: #323232;\nborder: none;}"
        self.btnCloseStyle = ":hover{\nbackground-color: darkred;\n}\n:pressed{\nbackground-color: red;\n}\nQPushButton{border:none}"
        self.btnChangeStyle = ":hover{\nbackground-color: darkorange;\n}\n:pressed{\nbackground-color: orange;\n}\nQPushButton{border:none}"
        self.btnOpenStyle = ':hover{\nbackground-color: darkgreen;\n}\n:pressed{\nbackground-color: green;\n}\nQPushButton{border:none} '
        self.openTrainsForm()


    def setCurentWagon(self):
        row = self.tableWidget.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            self.currentWagon = self.tableWidget.item(row, 0).text()
            self.currentPrice = self.tableWidget.item(row, 1).text()
            self.tableWidget.selectionModel().clearCurrentIndex()

        self.openPassengersForm()



    def placeIsAccept(self, testPlace):
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM Passengers WHERE train = ? AND wagon = ?;", (self.currentTrain, self.currentWagon))
        allTable = cur.fetchall()
        isAccept = True
        for i in allTable:
            if(i[1] == str(testPlace)):
                isAccept = False
        return isAccept

    def openAddTrainForm(self):
        uic.loadUi('AddForm.ui', self)
        self.btnCancel.clicked.connect(self.openTrainsForm)
        self.btnAdd.clicked.connect(self.addTrain)






    def addTrain(self):
        ret = QMessageBox.question(self, 'Добавить поезд', "Вы уверены?",
                                   QMessageBox.No | QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            row = [self.trainName.text(), self.dateIn.text(), self.dateOut.text()]
            cur.execute("INSERT INTO Trains VALUES(?, ?, ?);", row)
            connection.commit()
            self.openTrainsForm()

    def addPassenger(self):
        thisSeatNumber = -1;
        for i in range(1, self.absolutSeatNumber):
            if(self.placeIsAccept(i) == True):
                thisSeatNumber = i
                break
        if(thisSeatNumber == -1):
            QMessageBox.about(self, 'Ошибка', "К сожалению, свободных мест нет")
            return
        ret = QMessageBox.question(self, 'Добавить пассажира', "Вы уверены? Свободное место: " + str(thisSeatNumber),
                                   QMessageBox.No | QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            row = [self.passengerName.text(), thisSeatNumber, self.currentWagon, self.currentTrain]
            cur.execute("INSERT INTO Passengers VALUES(?, ?, ?, ?);", row)
            connection.commit()
            self.openPassengersForm()

    def openAddWagonForm(self):
        uic.loadUi('AddWagonForm.ui', self)
        self.trainName.setText(self.currentTrain)
        self.btnCancel.clicked.connect(self.openWagonsForm)
        self.btnAdd.clicked.connect(self.addWagon)

    def openAddPassengerForm(self):
        uic.loadUi('AddPassengerForm.ui', self)
        self.trainName.setText(self.currentTrain)
        self.wagonName.setText(self.currentWagon)
        self.price.setText(self.currentPrice)
        self.btnCancel.clicked.connect(self.openPassengersForm)
        self.btnAdd.clicked.connect(self.addPassenger)

    def addWagon(self, newWagon):
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM Wagons WHERE train = ? AND wagon = ?;", (self.currentTrain, self.wagonName.text()))
        allTable = cur.fetchall()
        if len(allTable) !=0:
            print(1)
            QMessageBox.about(self, "Ошибка", "Такой вагон уже есть")
            return

        ret = QMessageBox.question(self, 'Подтвердить', "Вы уверены что хотите добавить новый вагон?",
                                   QMessageBox.No | QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            newRow = [self.currentTrain, self.wagonName.text()]
            cur.execute("INSERT INTO Wagons VALUES(?, ?);", newRow)
            connection.commit()
            self.openWagonsForm()

    def setCurentTrain(self):
        row = self.tableWidget.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            self.currentTrain = self.tableWidget.item(row, 0).text()
            self.tableWidget.selectionModel().clearCurrentIndex()
        self.openWagonsForm()

    def openTrainsForm(self):
        uic.loadUi('firstForm.ui', self)
        self.btnAdd.clicked.connect(self.openAddTrainForm)
        self.btnSort.clicked.connect(self.sort)
        self.btnReset.clicked.connect(self.loadTrainsTable)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.tableWidget.setColumnWidth(5, 40)
        self.tableWidget.setColumnWidth(4, 40)
        self.tableWidget.setColumnWidth(3, 40)
        self.tableWidget.setColumnWidth(2, 150)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger(0))
        self.tableWidget.setHorizontalHeaderLabels(['Номер поезда', 'Дата прибытия', 'Дата отбытия', '', '', '', ''])
        self.loadTrainsTable()

    def openWagonsForm(self):
        uic.loadUi('secondForm.ui', self)
        self.info.setText("Номер поезда: " + self.currentTrain)
        self.btnAdd.clicked.connect(self.openAddWagonForm)
        self.btnBack.clicked.connect(self.openTrainsForm)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.tableWidget.setColumnWidth(4, 40)
        self.tableWidget.setColumnWidth(3, 40)
        self.tableWidget.setColumnWidth(2, 40)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger(0))
        self.tableWidget.setHorizontalHeaderLabels(['Номер вагона','цена', '', '', ''])
        self.loadWagonsTable()


    def openPassengersForm(self):
        uic.loadUi('ThirdForm.ui', self)
        self.btnAdd.clicked.connect(self.openAddPassengerForm)
        self.btnBack.clicked.connect(self.openWagonsForm)
        self.info.setText("Номер поезда: " + self.currentTrain + "\tНомер вагона: " + self.currentWagon)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.tableWidget.setColumnWidth(3, 40)
        self.tableWidget.setColumnWidth(2, 40)
        self.tableWidget.setColumnWidth(1, 60)
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger(0))
        self.tableWidget.setHorizontalHeaderLabels(['Пассажир', 'место','', ''])
        self.loadPassengersTable()

    def sort(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setStyleSheet(self.headerStyle)
        self.tableWidget.verticalHeader().hide()
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        curentRow = 0
        taskStr = "SELECT * FROM Trains WHERE"
        taskList = []
        if(self.checkIn.isChecked() and self.checkOut.isChecked()):
            taskStr += " dataIn = ? AND dataOut = ?;"
            taskList.append(self.sortDateIn.text())
            taskList.append(self.sortDateOut.text())
        elif (self.checkIn.isChecked()):
            taskStr += " dataIn = ?;"
            taskList.append(self.sortDateIn.text())
        elif (self.checkOut.isChecked()):
            taskStr += " dataOut = ?;"
            taskList.append(self.sortDateOut.text())
        if (len(taskList) == 0):
            self.loadTrainsTable()
            return
        print(taskStr, taskList)
        for row in cur.execute(taskStr, taskList):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i in range(0, 3):
                self.tableWidget.setItem(curentRow, i, QtWidgets.QTableWidgetItem(row[i]))

                btnOpen = QPushButton()
                btnOpen.setIcon(QIcon("iconOpen.png"))
                btnOpen.setIconSize(QSize(20, 20))
                btnOpen.setStyleSheet(self.btnOpenStyle)
                btnOpen.clicked.connect(self.setCurentTrain)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 3, btnOpen)

                btnChange = QPushButton()
                btnChange.setIcon(QIcon("iconChange.png"))
                btnChange.setIconSize(QSize(20, 20))
                btnChange.setStyleSheet(self.btnChangeStyle)
                btnChange.clicked.connect(self.ChangeTrain)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 4, btnChange)

                btnClose = QPushButton()
                btnClose.setIcon(QIcon("iconClose.png"))
                btnClose.setIconSize(QSize(20, 20))
                btnClose.setStyleSheet(self.btnCloseStyle)
                btnClose.clicked.connect(self.DelTrain)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 5, btnClose)
            curentRow += 1

    def loadTrainsTable(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setStyleSheet(self.headerStyle)
        self.tableWidget.verticalHeader().hide()
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        curentRow = 0
        for row in cur.execute("SELECT * FROM Trains"):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i in range(0, 3):
                self.tableWidget.setItem(curentRow, i, QtWidgets.QTableWidgetItem(row[i]))
                # self.tableWidget.item(curentRow, i).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

                btnOpen = QPushButton()
                btnOpen.setIcon(QIcon("iconOpen.png"))
                btnOpen.setIconSize(QSize(20, 20))
                btnOpen.setStyleSheet(self.btnOpenStyle)
                btnOpen.clicked.connect(self.setCurentTrain)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 3, btnOpen)

                btnChange = QPushButton()
                btnChange.setIcon(QIcon("iconChange.png"))
                btnChange.setIconSize(QSize(20, 20))
                btnChange.setStyleSheet(self.btnChangeStyle)
                btnChange.clicked.connect(self.ChangeTrain)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 4, btnChange)

                btnClose = QPushButton()
                btnClose.setIcon(QIcon("iconClose.png"))
                btnClose.setIconSize(QSize(20, 20))
                btnClose.setStyleSheet(self.btnCloseStyle)
                btnClose.clicked.connect(self.DelTrain)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 5, btnClose)

            curentRow+=1

    def loadWagonsTable(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setStyleSheet(self.headerStyle)
        self.tableWidget.verticalHeader().hide()
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        curentRow = 0
        for row in cur.execute("SELECT * FROM Wagons WHERE train = ?;", (self.currentTrain, )):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i in range(1, 3):
                self.tableWidget.setItem(curentRow, i-1, QtWidgets.QTableWidgetItem(row[i]))

                btnOpen = QPushButton()
                btnOpen.setIcon(QIcon("iconOpen.png"))
                btnOpen.setIconSize(QSize(20, 20))
                btnOpen.setStyleSheet(self.btnOpenStyle)
                btnOpen.clicked.connect(self.setCurentWagon)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 2, btnOpen)

                btnChange = QPushButton()
                btnChange.setIcon(QIcon("iconChange.png"))
                btnChange.setIconSize(QSize(20, 20))
                btnChange.setStyleSheet(self.btnChangeStyle)
                btnChange.clicked.connect(self.ChangeWagon)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 3, btnChange)

                btnClose = QPushButton()
                btnClose.setIcon(QIcon("iconClose.png"))
                btnClose.setIconSize(QSize(20, 20))
                btnClose.setStyleSheet(self.btnCloseStyle)
                btnClose.clicked.connect(self.DelWagon)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 4, btnClose)

            curentRow += 1

    def loadPassengersTable(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setStyleSheet(self.headerStyle)
        self.tableWidget.verticalHeader().hide()
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        curentRow = 0
        for row in cur.execute("SELECT * FROM Passengers WHERE wagon = ? AND train = ? ", (self.currentWagon, self.currentTrain)):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i in range(0, 2):
                self.tableWidget.setItem(curentRow, i, QtWidgets.QTableWidgetItem(row[i]))

                btnChange = QPushButton()
                btnChange.setIcon(QIcon("iconChange.png"))
                btnChange.setIconSize(QSize(20, 20))
                btnChange.setStyleSheet(self.btnChangeStyle)
                btnChange.clicked.connect(self.ChangePassenger)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 2, btnChange)

                btnClose = QPushButton()
                btnClose.setIcon(QIcon("iconClose.png"))
                btnClose.setIconSize(QSize(20, 20))
                btnClose.setStyleSheet(self.btnCloseStyle)
                btnClose.clicked.connect(self.DelPassenger)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 3, btnClose)

            self.tableWidget.item(curentRow, 1).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            curentRow += 1

    def ChangePassenger(self):
        button = QMessageBox.question(self, "Изменить данные", "Вы уверены?")
        if button == QMessageBox.StandardButton.Yes:
            curentRow = self.tableWidget.currentRow()
            oldPassengerName = self.tableWidget.item(curentRow, 0).text()
            uic.loadUi('AddPassengerForm.ui', self)
            self.btnAdd.setText("Сохранить")
            self.trainName.setText(self.currentTrain)
            self.wagonName.setText(self.currentWagon)
            self.price.setText(self.currentPrice)
            self.passengerName.setText(oldPassengerName)
            self.btnCancel.clicked.connect(self.openPassengersForm)
            self.btnAdd.clicked.connect(lambda: self.updatePassenger(oldPassengerName))

    def updatePassenger(self, oldPassengerName):
        print(oldPassengerName)
        button = QMessageBox.question(self, "Сохранить изменения", "Вы уверены?")
        if button == QMessageBox.StandardButton.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            cur.execute("UPDATE Passengers SET passenger = ? WHERE passenger = ?",
                        (self.passengerName.text(), oldPassengerName))
            connection.commit()
            self.openPassengersForm()

    def ChangeWagon(self):
        button = QMessageBox.question(self, "Изменить данные", "Вы уверены?")
        if button == QMessageBox.StandardButton.Yes:
            curentRow = self.tableWidget.currentRow()
            oldWagonName = self.tableWidget.item(curentRow, 0).text()
            uic.loadUi('addWagonForm.ui', self)
            self.btnAdd.setText("Сохранить")
            self.trainName.setText(self.currentTrain)
            self.wagonName.setText(oldWagonName)
            self.btnCancel.clicked.connect(self.openWagonsForm)
            self.btnAdd.clicked.connect(lambda: self.updateWagon(oldWagonName))

    def updateWagon(self, oldWagonName):
        button = QMessageBox.question(self, "Сохранить изменения", "Вы уверены?")
        if button == QMessageBox.StandardButton.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            cur.execute("UPDATE Passengers SET wagon = ? WHERE wagon = ?",
                        (self.wagonName.text(), oldWagonName))
            connection.commit()
            cur.execute("UPDATE Wagons SET wagon = ? WHERE wagon = ?",
                        (self.wagonName.text(), oldWagonName))
            connection.commit()
            self.openWagonsForm()

    def ChangeTrain(self):
        button = QMessageBox.question(self, "Изменить данные", "Вы уверены?")
        if button == QMessageBox.StandardButton.Yes:
            curentRow = self.tableWidget.currentRow()
            oldTrainName = self.tableWidget.item(curentRow, 0).text()
            oldDateIn = self.tableWidget.item(curentRow, 1).text()
            oldDateOut = self.tableWidget.item(curentRow, 2).text()
            uic.loadUi('AddForm.ui', self)
            self.btnAdd.setText("Сохранить")
            self.trainName.setText(oldTrainName)
            self.dateIn.setDate(QDate.fromString(oldDateIn, "dd.MM.yyyy"))
            self.dateOut.setDate(QDate.fromString(oldDateOut, "dd.MM.yyyy"))
            self.btnCancel.clicked.connect(self.openTrainsForm)
            self.btnAdd.clicked.connect(lambda: self.updateTrain(oldTrainName, oldDateIn, oldDateOut))

    def updateTrain(self, oldTrainName, oldDateIn, oldDateOut):
        button = QMessageBox.question(self, "Сохранить изменения", "Вы уверены?")
        if button == QMessageBox.StandardButton.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            cur.execute("UPDATE Wagons SET train = ? WHERE train = ?",
                        (self.trainName.text(), oldTrainName))
            connection.commit()
            cur.execute("UPDATE Passengers SET train = ? WHERE train = ?",
                        (self.trainName.text(), oldTrainName))
            connection.commit()
            cur.execute("UPDATE Trains SET train = ?,dataIn = ?,dataOut = ?  WHERE train = ? AND dataIn = ? AND dataOut = ?;",
                        (self.trainName.text(), self.dateIn.text(), self.dateOut.text(), oldTrainName, oldDateIn, oldDateOut))
            connection.commit()
            self.openTrainsForm()

    def DelTrain(self):
        button = QMessageBox.question(self, "Удаление данные", "Вы уверены?")
        if button == QMessageBox.StandardButton.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            cur.execute("SELECT * FROM Trains;")
            allMain = cur.fetchall()
            row = self.tableWidget.currentRow()
            delIndex = self.tableWidget.currentRow()
            cur.execute("DELETE FROM Passengers WHERE train = ?",
                        (allMain[delIndex][0], ))
            cur.execute("DELETE FROM Wagons WHERE train = ?",
                        (allMain[delIndex][0], ))
            cur.execute("DELETE FROM Trains WHERE train = ? AND dataIn = ? AND dataOut = ?",
                        (allMain[delIndex][0], allMain[delIndex][1], allMain[delIndex][2]))
            connection.commit()

            if row > -1:  # Если есть выделенная строка/элемент
                self.tableWidget.removeRow(row)
                self.tableWidget.selectionModel().clearCurrentIndex()

    def DelWagon(self):
        button = QMessageBox.question(self, "Удаление строки", "Вы уверены?")
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM Wagons;")
        allMain = cur.fetchall()
        if button == QMessageBox.StandardButton.Yes:
            row = self.tableWidget.currentRow()
            delIndex = self.tableWidget.currentRow()
            cur.execute("DELETE FROM Wagons WHERE wagon = ? AND train = ?",
                        (allMain[delIndex][0], self.currentTrain))
            cur.execute("DELETE FROM Passengers WHERE wagon = ? AND train = ?",
                        (allMain[delIndex][0], self.currentTrain))
            connection.commit()
            if row > -1:  # Если есть выделенная строка/элемент
                self.tableWidget.removeRow(row)
                self.tableWidget.selectionModel().clearCurrentIndex()

    def DelPassenger(self):
        button = QMessageBox.question(self, "Удаление строки", "Вы уверены?")
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM Passengers;")
        allMain = cur.fetchall()
        if button == QMessageBox.StandardButton.Yes:
            row = self.tableWidget.currentRow()
            delIndex = self.tableWidget.currentRow()
            cur.execute("DELETE FROM Passengers WHERE passenger = ? AND seatingPosition = ?",
                        (allMain[delIndex][0], allMain[delIndex][1]))
            connection.commit()
            if row > -1:  # Если есть выделенная строка/элемент
                self.tableWidget.removeRow(row)
                self.tableWidget.selectionModel().clearCurrentIndex()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet('''
        
            #LabelTitle {
                font-size: 60px;
                color: #93deed;
            }

            #LabelDesc {
                font-size: 30px;
                color: #c2ced1;
            }
            
            #Fon{
                border-radius: 10px;
            }

            #LabelLoading {
                font-size: 30px;
                color: #e8e8eb;
            }

            QFrame {
                color: rgb(220, 220, 220);
                border-radius: 10px;
            }

            QProgressBar {
                background-color: #DA7B93;
                color: rgb(200, 200, 200);
                border-style: none;
                border-radius: 10px;
                text-align: center;
                font-size: 30px;
            }

            QProgressBar::chunk {
                border-radius: 10px;
                background-color: qlineargradient(spread:pad x1:0, x2:1, y1:0.511364, y2:0.523, stop:0 #1C3334, stop:1 #376E6F);
            }
        ''')

    splash = SplashScreen()
    splash.show()

    # splash = QtWidgets.QSplashScreen(QPixmap('startImage.jpg'))  # Загружаем изображение;
    #
    # splash.setFixedWidth(960)
    # splash.setFixedHeight(600)
    # splash.setStyleSheet("{border-radius: 6px}")
    # splash.show()  # Отображаем заставку;
    #
    # for i in range(0,100):
    #     splash.showMessage('Загрузка данных... '+ str(i) +' %',
    #                    Qt.AlignBottom | Qt.AlignBottom, Qt.black)
    #     time.sleep(0.001)
    #     QtWidgets.qApp.processEvents()  # Оборот цикла;

    # ex = App()
    # ex.show()
    # splash.finish(ex)
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')


