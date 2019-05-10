# Creator Name : Faizan Ahmed
#

# These are Python libraries that we need to run this program.
import nltk
from nltk.corpus import stopwords
from PyQt5 import QtCore, QtGui, QtWidgets
from scipy import spatial
from nltk.corpus import wordnet
import pymysql.cursors
import easygui


# This is User interface Class
class Ui_MainWindow(object):

    def buttonclicked(self):
        database=''
        database=self.lineEdit.text()
        if database=='':
            easygui.msgbox("Since no Database was provided.. Program will terminate.!")
            sys.exit(-1)

        # Connection to database
        # Give correct database credentials here of your own database
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='faizan',
                                     db=database,
                                     #charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        # Lists used in Program
        operator = []
        symbols = []
        filtered_result = []
        cos_sim_list = []
        column = []
        table = []
        condition = []
        noun_nv = []
        cols = []
        tabs = []
        wnlist = []
        ag_functions = []
        ag_func_list=[]
        order=[]
        orderbyfunc=[]
        list1=['is','are','equals','equal','or','greater','bigger','higher','above','over','lower','smaller','lesser','less','under','below']# words to be converted into symbols
        list2=['ordered', 'order','ascending','increasing','decreasing','descending', 'ordering','sort','sorted','sorting','arranged','arrange','arranging']
        list3=['not','in','between','from']
        mytext = self.textEdit.toPlainText()

        tokens = nltk.word_tokenize(mytext)

        # Operators
        for u in tokens:
            if u in list1 or u in list3:
                operator.append(u)
            if u in list2:
                order.append(u)
        # Conversion of operators in symbols
        count=0
        for t in operator:
            count+=1
            if t=='is' or t=='are':
                if count == len(operator):
                    symbols.append('=')
                else:
                    for u in operator[operator.index(t)+1:]:
                        if u=='or':
                            for v in operator[operator.index(u)+1:]:
                                if v == 'greater' or v == 'bigger' or v == 'larger' or v == 'higher' or v == 'above' or v == 'over':
                                    symbols.append(">=")
                                if v=='smaller' or v=='lower' or v=='lesser' or v=='less' or v=='under' or v=='below':
                                    symbols.append("<=")
                            break

                        elif u == 'greater' or u == 'bigger' or u == 'larger' or u == 'higher' or u == 'above' or u == 'over':
                            for v in operator[operator.index(u):]:
                                if v=='or' or v=='equal':
                                    symbols.append(">=")
                                    break
                                if operator.index(v) == len(operator)-1:
                                    symbols.append(">")
                                    break
                            break

                        elif u=='smaller' or u=='lower' or u=='lesser' or u=='less' or u=='under' or u=='below':
                            for v in operator[operator.index(u):]:
                                if v=='or' or v=='equal':
                                    symbols.append("<=")
                                    break
                                if operator.index(v) == len(operator)-1:
                                    symbols.append("<")
                                    break
                            break


                        elif u == 'not':
                            for v in operator[operator.index(u) + 1:]:
                                if v == 'in':
                                    symbols.append("NOT IN")
                                    break
                                elif v == 'between' or v=='from':
                                    symbols.append("NOT BETWEEN")
                                    break

                            break

                        elif u=='equal':
                            symbols.append('=')
                            break

                        elif u=='between' or u=='from':
                            symbols.append("BETWEEN")
                            break

                        elif u=='in':
                            symbols.append("IN")
                            break
                        else:
                            continue

                break
            elif t=='equals':
                symbols.append('=')

            elif t == 'greater' or t == 'bigger' or t == 'larger' or t == 'higher' or t == 'above' or t == 'over':
                symbols.append(">")

            elif t == 'smaller' or t == 'lower' or t == 'lesser' or t == 'less' or t == 'under' or t == 'below':
                symbols.append("<")
            elif t=='not':
                for u in operator[operator.index(t)+1:]:
                    if u =='in':
                        symbols.append("NOT IN")
                        break
                    elif u=='between' or u=='from':
                        symbols.append("NOT BETWEEN")
                        break
                    else:
                        symbols.append("!=")
            elif t=='between' or t=='from':
                symbols.append("BETWEEN")

            elif u == 'in':
                symbols.append("IN")

            else:
                symbols.append("=")

        # Stemming Words
        #ps = PorterStemmer()
        #stm=[]
        #for word in tokens:
            #stm.append((ps.stem(word)))

        tagged_words = nltk.pos_tag(tokens)

        stop_words = set(stopwords.words("english"))

        for word, pos in tagged_words:
            if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS' or pos == 'JJ' or pos == 'CD'):
                filtered_result.append(word)

        for f in filtered_result:
            i=filtered_result.index(f)
            for f2 in filtered_result:
                j = filtered_result.index(f2)
                if f==f2 and i!=j:
                    filtered_result.remove(f)

        # Creating Vector Matrix
        a = len(filtered_result)
        vector_list=[[]for x in range(a)]

        counter=0
        for fi in filtered_result:
            i=filtered_result.index(fi)
            for fj in filtered_result:
                j=filtered_result.index(fj)

                if i == j:
                    vector_list[counter].append(0)
                elif i + 1 == j or i - 1 == j:
                    vector_list[counter].append(5)
                elif i + 2 == j or i - 2 == j:
                    vector_list[counter].append(4)
                elif i + 3 == j or i - 3 == j:
                    vector_list[counter].append(3)
                elif i + 4 == j or i - 4 == j:
                    vector_list[counter].append(2)
                elif i + 5 == j or i - 5 == j:
                    vector_list[counter].append(1)
                else:
                    vector_list[counter].append(0)


            vector_list[counter]*=2

            counter += 1

            #Prints Vectors of every words except Stopwords
            #print(fi,' = ', vector_list[i])

        #Calculating Cosine Similarity

        for fi in filtered_result:
            i=filtered_result.index(fi)
            for fj in filtered_result:
                j=filtered_result.index(fj)
                j+=1

                if j<len(filtered_result) and j>i:
                    result = 1 - spatial.distance.cosine(vector_list[i], vector_list[j])
                    result = str(round(result, 4))
                    cos_sim_list.append(result)
                    #print('Cosine similarity b/w  "', filtered_result[i],
                          #'" and "', filtered_result[j], '" is: ', result)

        #print(max(cos_sim_list))

        # Query Generation Code


        for s in filtered_result:
            for syn in wordnet.synsets(s):
                for l in syn.lemmas():
                    wnlist.append(l.name())
        wnlist=list(set(wnlist))

        # Getting Table and Column Names from Database
        sql = "show tables from " + database
        # Execute query.
        cursor.execute(sql)
        for row in cursor:
            tabs.append(row["Tables_in_"+database])
            # print(row)


        for i in wnlist:
            if i in tabs:
                table.append(i)
        for i in table:
            sql = "show columns from " + i
            cursor.execute(sql)
            for row in cursor:
                cols.append(row["Field"])
                # print(row)


        for t in wnlist:
            for u in cols:
                if t in u or t.upper() in u or t.capitalize() in u or t.lower() in u:
                #print(t,"= ",len(t),",,,",u,"= ",len(u),",,, Same =",count)
                    column.append(u)


        table = list(set(table))
        column = list(set(column))


          # list of aggregrate function words

        for f,pos in nltk.pos_tag(filtered_result):
            if (pos=='JJ'):
                ag_func_list.append(f)

        for i in ag_func_list:
            if i=='maximum':
                ag_functions.append('max')
            elif i=='minimum':
                ag_functions.append('min')
            elif i=='average':
                ag_functions.append('avg')

        newlist=[]
        for w in tokens:
            if w not in stop_words:
                newlist.append(w)

        nlist=nltk.pos_tag(newlist)
        print(nlist)

        for f,pos in nlist:
            i=nlist.index((f,pos))
            if pos=='NN' or pos=='NNS' or pos=='JJ' or pos=='VBP':
                for ff,pos1 in nlist:
                    j = nlist.index((ff,pos1))
                    if pos1=='CD' or pos1=='NNP' or pos1=='NNPS':
                        if j==i+1 or j==i+2:
                            for v in cols:
                                if f in v:
                                    condition.append(v)
                                    condition.append('"'+ff+'"')

        # Code for order by function
        for t in tagged_words:
            if t[0] in list2:
                order.append(t[0])
                for t1,pos1 in tagged_words[tagged_words.index(t):]:
                    if pos1 == 'NN' or pos1 == 'NNS':
                        for u in cols:
                            if t1 in u:
                                orderbyfunc.append(u)
                break


        # Converting lists to strings
        s="".join(symbols)
        s=' ' + s + ' '
        #print(s)
        column = ", ".join(column)
        table=", ".join(table)
        if "BETWEEN" in symbols or 'NOT BETWEEN' in symbols:
            condition.pop(2)
            condition.insert(2,'and')
            condition.insert(1, s)
            condition = " ".join(condition)
        else:
            condition = s.join(condition)

        print(condition)

        ag_functions="".join(ag_functions)
        orderbyfunc=", ".join(orderbyfunc)


        # Code to select all records
        for i in tokens:
            if i=='all' or i =='every':
                column='*'

        if not column:
            column="*"



        #SQL Query
        if condition and ag_functions and orderbyfunc:
            if 'descending' in order:
                sql_query = "SELECT " + ag_functions + column + " FROM " + table + " WHERE " + condition + " ORDER BY " + orderbyfunc + "DESC"
            else:
                sql_query = "SELECT " + ag_functions + column + " FROM " + table + " WHERE " + condition + " ORDER BY " + orderbyfunc + "DESC"


        elif condition and ag_functions:
            sql_query = "SELECT " + ag_functions + "(" + column  + ") FROM " + table + " WHERE " + condition


        elif condition and orderbyfunc:
            if 'descending' in order:
                sql_query = "SELECT " + column + " FROM " + table + " WHERE " + condition + " ORDER BY " + orderbyfunc + "DESC"
            else:
                sql_query = "SELECT " + column + " FROM " + table + " WHERE " + condition + " ORDER BY " + orderbyfunc


        elif ag_functions and orderbyfunc:
            if 'descending' in order:
                sql_query = "SELECT " + ag_functions + "(" + column + ") FROM " + table + " WHERE " + condition + "ORDER BY " + orderbyfunc + "DESC"
            else:
                sql_query = "SELECT " + ag_functions + "(" + column + ") FROM " + table + " WHERE " + condition + "ORDER BY " + orderbyfunc


        elif condition:
            sql_query = "SELECT " + column + " FROM " + table + " WHERE " + condition


        elif ag_functions:
            sql_query = "SELECT " + ag_functions + "(" + column + ") FROM " + table


        elif orderbyfunc:
            if 'descending' in order:
                sql_query = "SELECT " + column +  " FROM " + table + " ORDER BY " + orderbyfunc + " DESC"
            else:
                sql_query = "SELECT " + column + " FROM " + table + " ORDER BY " + orderbyfunc


        else:
            sql_query = "SELECT " + column + " FROM " + table

        print(mytext)
        #print(tokens)
        print(operator)
        print(symbols)
        print(tagged_words)
        print(filtered_result)
        #print(wnlist)
        #print(tabs)
        #print(cols)
        print(table)
        print(column)
        #print(ag_functions)
        print(condition)
        print(sql_query)

        try:
            try:
                cursor.execute(sql_query)
            except (pymysql.Error, pymysql.Warning) as e:
                easygui.msgbox(e)
            try:
                result = cursor.fetchall()
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    # print(row_data)
                    for column_number, data in enumerate(row_data.values()):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            except TypeError as e:
                easygui.msgbox(e)
        finally:
            connection.close()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(797, 604)
        MainWindow.setFocusPolicy(QtCore.Qt.WheelFocus)
        MainWindow.setToolTipDuration(-1)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Label_1
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(160, 10, 441, 51))
        self.label.setMinimumSize(QtCore.QSize(161, 0))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setFrameShape(QtWidgets.QFrame.Panel)
        self.label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label.setObjectName("label")

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(10, 35, 120, 31))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(12)
        self.lineEdit.setFont(font)
        self.lineEdit.setMouseTracking(True)
        self.lineEdit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.lineEdit.setToolTipDuration(4)
        self.lineEdit.setAutoFillBackground(False)
        self.lineEdit.setReadOnly(False)
        self.lineEdit.setObjectName("lineEdit")


        #Text_Editor
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(10, 140, 601, 71))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.textEdit.setMouseTracking(True)
        self.textEdit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.textEdit.setToolTipDuration(4)
        self.textEdit.setAutoFillBackground(False)
        self.textEdit.setFrameShape(QtWidgets.QFrame.Box)
        self.textEdit.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.textEdit.setTabChangesFocus(True)
        self.textEdit.setReadOnly(False)
        self.textEdit.setOverwriteMode(True)
        self.textEdit.setObjectName("textEdit")

        #Evaluate_Button
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(650, 140, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.buttonclicked)

        #Table_View
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 250, 771, 301))
        self.tableWidget.setRowCount(20)
        self.tableWidget.setColumnCount(20)
        self.tableWidget.setObjectName("tableWidget")
        #self.tableWidget.verticalHeader().setHighlightSections(True)

        #Label_2
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(350, 220, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(30, 10, 100, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")

        #Clear_Button
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(650, 182, 131, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setAutoFillBackground(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.textEdit.clear)


        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 797, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar_2 = QtWidgets.QToolBar(MainWindow)
        self.toolBar_2.setObjectName("toolBar_2")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_2)
        self.toolBar_3 = QtWidgets.QToolBar(MainWindow)
        self.toolBar_3.setObjectName("toolBar_3")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_3)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "NLIDB"))
        self.label.setText(_translate("MainWindow", "Natural Language Interface to DataBase"))
        self.textEdit.setPlaceholderText(_translate("MainWindow", "Type Expression Here..."))
        self.pushButton.setText(_translate("MainWindow", "Evaluate"))
        self.label_2.setText(_translate("MainWindow", "RESULT"))
        self.label_3.setText(_translate("MainWindow", "DB Name"))
        self.pushButton_2.setText(_translate("MainWindow", "Clear"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.toolBar_2.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.toolBar_3.setWindowTitle(_translate("MainWindow", "toolBar_3"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
