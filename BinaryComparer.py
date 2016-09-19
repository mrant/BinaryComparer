# -*- coding: utf-8 -*-
# Experiment with wxPython's HtmlWindow
# tested with Python24 and wxPython26 vegaseat 17may2006

import os,sys,stat,time,binascii,random
import wx
import wx.grid
import threading
import Compare

        
fileList = {"F1":"","F2":"","CUT":"","RST":""}
TT = {"F1":0,"F2":1,"CUT":2,"RST":3}
nLines = {"F1":0,"F2":0}
big_table = {}

class WorkerThread(threading.Thread):
    """
    Send message to the GUI thread.
    """
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        self.messageDelay = 0.0000001

    def stop(self):
        self.timeToQuit.set()

    def run(self):
        for i in range(self.window.count, len(big_table)):
            if i % 30 == 0:
                self.timeToQuit.wait(self.messageDelay)
            #wx.CallAfter(self.window.UpdateTableRst, i, "")
            #big_table[i][TT["RST"]] = ""
            diff_str = ""
            for j in range(16):
                if big_table[i][TT["F1"]][j:j+1] != big_table[i][TT["F2"]][j:j+1]:
                    #wx.CallAfter(self.window.UpdateTableRst, i, big_table[i][TT["RST"]] + "," + str(j))
                    diff_str += "," + str(j)
            big_table[i][TT["RST"]] = diff_str
            if self.timeToQuit.isSet():
                break
            wx.CallAfter(self.window.UpdateCount, i)
        else:
            wx.CallAfter(self.window.ThreadFinished, self)
            

class MyComparePanel(wx.Panel):
    """
    class MyComparePanel inherits wx.Panel
    """
    def __init__(self, parent, id):
        ####################
        self.CurrentSel = "Str"
        self.setting_path = ""
        self.max_file_size = 20*1024*1024
        self.line_byte_number = 16

        self.curren_page = 0
        self.start_row = 1  #0 row is header
        self.grid_lines = 200
        self.base_line = 0  # start_row shows this line
        
        self.threads = []
        self.count = 0
        ############################
        # default pos is (0, 0) and size is (-1, -1) which fills the frame
        wx.Panel.__init__(self, parent, id)
        #self.SetBackgroundColour("yellow")
        # add menu bar

        #self.html1 = wx.html.HtmlWindow(self, id, pos=(5,70), size=(785,430))
        self.btn_load1 = wx.Button(self, -1, "导入文件1", pos=(10,10))
        self.btn_load1.Bind(wx.EVT_BUTTON, self.OnLoadFile1)
        
        self.btn_load2 = wx.Button(self, -1, "导入文件2", pos=(10,40))
        self.btn_load2.Bind(wx.EVT_BUTTON, self.OnLoadFile2)

        self.path1 = wx.TextCtrl(self, -1, value="", pos=wx.Point(90, 12), size=wx.Size(500, 20))
        self.path1.SetEditable(0)
        self.path2 = wx.TextCtrl(self, -1, value="", pos=wx.Point(90, 42), size=wx.Size(500, 20))
        self.path2.SetEditable(0)

        self.grid = wx.grid.Grid(self, -1, style=wx.LC_REPORT
                                | wx.LC_NO_HEADER
                                | wx.LC_EDIT_LABELS
                                | wx.LC_SINGLE_SEL
                                ,pos=(10,80), size=(825, 620))
        
        self.grid.CreateGrid(self.grid_lines+1,35)
        #self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelSize(0)
        self.grid.EnableEditing(0)
        self.grid.EnableDragGridSize(0)
        #self.grid.EnableGridLines(0)
        #####HEADERS
        self.grid.SetRowLabelValue(0, "行号")
        
        self.grid.SetCellSize(0, 0, 1, 16)
        self.grid.SetCellValue(0, 0, "文件1")
        self.grid.SetRowSize(0, 40)
        self.grid.SetCellSize(0, 17, 1, 16)
        self.grid.SetCellValue(0, 17, "文件2")
        self.grid.SetCellValue(0, 34, "备注")

        attr = wx.grid.GridCellAttr()
        attr.SetBackgroundColour("gray")
        attr.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.grid.SetRowAttr(0, attr)
##        self.grid.SetColAttr(16, attr)
##        self.grid.SetColAttr(33, attr)
        
        for col in range(16):
            self.grid.SetColSize(col, 18)
            self.grid.SetColSize(17 + col, 18)
            
        self.grid.SetColSize(16, 16)
        self.grid.SetColSize(33, 16)
        self.grid.SetColSize(34, 100) 

        self.btn_compare = wx.Button(self, -1, "比较", pos=(600,42))
        self.btn_compare.Bind(wx.EVT_BUTTON, self.OnCompare)
        self.btn_compare = wx.Button(self, -1, "暂停", pos=(680,42))
        self.btn_compare.Bind(wx.EVT_BUTTON, self.OnPause)
        self.btn_compare = wx.Button(self, -1, "停止", pos=(760,42))
        self.btn_compare.Bind(wx.EVT_BUTTON, self.OnStop)

        self.btn_compare = wx.Button(self, -1, "上一页", pos=(680,710))
        self.btn_compare.Bind(wx.EVT_BUTTON, self.OnUp)
        self.btn_compare = wx.Button(self, -1, "下一页", pos=(760,710))
        self.btn_compare.Bind(wx.EVT_BUTTON, self.OnNext)
        self.page_index = wx.TextCtrl(self, -1, value="0", pos=wx.Point(550, 712), size=wx.Size(50, 20))
        self.total_page = wx.StaticText(self, -1, "/0", (600, 715))
        self.processing = wx.StaticText(self, -1, "0/0", (700, 16))

        self.b = wx.Button(self, -1, "GO", pos=wx.Point(500, 712), size=wx.Size(30, 20))
        self.b.Bind(wx.EVT_BUTTON, self.OnPageGo)
        accelTable = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_RETURN, self.b.GetId())])
        self.SetAcceleratorTable(accelTable)

        self.current_table = big_table
        self.RefreshGrid()

    def RefreshTable(self, rlist):      
        for r in rlist:
            for item in big_table.keys():
                    big_table[item][TT[r]] = ""

            if r == "F1" or r == "F2":
                fileStats = os.stat(fileList[r])
                # open file
                try:
                    fs = open(fileList[r], 'rb')
                except IOError, eStr:
                    fs_report.write( "<br>Cannot open %s: %s<br>" % (fileList[r], eStr) )
                    return
                dt = fs.read(self.max_file_size)
                fs.close()
                
                
                nLines[r] = fileStats[stat.ST_SIZE]/self.line_byte_number
                if len(big_table) <= nLines[r]:
                    for i in range(len(big_table), nLines[r]):
                        big_table[i] = ["","","",""]
                else:
                    max_lines = max(nLines["F1"], nLines["F2"])
                    if len(big_table) > max_lines:
                        for i in range(max_lines, len(big_table)):
                            del big_table[i]
                    
                for i in range(len(big_table)):
                    big_table[i][TT[r]] = dt[i * self.line_byte_number:i * self.line_byte_number+self.line_byte_number]
            if r == "CUT":
                if os.path.isfile(fileList[r]):       
                    fs = open(fileList[r], "r")
                    lines = fs.readlines()
                    fs.close()

                    cut_line = []
                    for m in lines:
                        cutList = m.split(",")
                        for n in cutList:
                            if n.find("~") > -1:
                                i, j = n.strip().split("~")
                            else:
                                i = j = n

                            cut_line = cut_line + range(int(i), int(j))
##                    if len(big_table) < max(cut_line):
##                        for i in range(len(big_table), max(cut_line)):
##                            big_table[i] = ["","","",""]

                    for line in cut_line:
                        if line > len(big_table):
                            continue
                        big_table[line-1][TT[r]] = "1"
                else:
                    for i in range(len(big_table)):
                        big_table[i][TT[r]] = ""
            #########clear compare results
            for item in big_table.keys():
                big_table[item][TT["RST"]] = ""
            self.curren_page = 0
            self.RefreshGrid()
       
    def RefreshGrid(self):
        self.base_line = self.curren_page*self.grid_lines
        self.page_index.SetLabel(str(self.curren_page+1))
        self.total_page.SetLabel("/" + str(len(big_table)/self.grid_lines+1))
        #print self.grid.GetGridCursorRow(), self.grid.GetScrollLineX(), self.grid.GetScrollLineY()
        
        for row in range(self.grid_lines):
##            for col in range(16):
##                attr = wx.grid.GridCellAttr()
##                attr.SetBackgroundColour(self.grid.GetDefaultCellBackgroundColour())
##                self.grid.SetAttr(row+self.start_row, int(col), attr)
##                self.grid.SetAttr(row+self.start_row, int(col)+17, attr)
            
            k = self.current_table.keys()
            k.sort()
            
            if row + self.base_line >= len(self.current_table):
                # nothing to show
                self.grid.SetRowLabelValue(row+self.start_row, "")
                for col in range(35):
                    self.grid.SetCellValue(row+self.start_row, col, "")
                continue
            # set line number         
            self.grid.SetRowLabelValue(row+self.start_row, "0"*(6-len(str(k[row+self.base_line]+1))) + str(k[row+self.base_line]+1))

            #print row, self.base_line
            #print self.current_table 
            if len(self.current_table[k[row+self.base_line]][TT["RST"]]):
                # there are some diffs, set colour
                for col in range(16):
                    if str(col) in self.current_table[k[row+self.base_line]][TT["RST"]].split(","):
                        #print self.grid.GetLabelBackgroundColour(), self.grid.GetDefaultCellBackgroundColour()                        
                        self.grid.SetCellTextColour(row+self.start_row, int(col), "red")
                        self.grid.SetCellTextColour(row+self.start_row, int(col)+17, "red")
##                        attr = wx.grid.GridCellAttr()
##                        attr.SetTextColour("red")
##                        self.grid.SetAttr(row+self.start_row, int(col), attr)
##                        self.grid.SetAttr(row+self.start_row, int(col)+17, attr)
                    else:
##                        attr = wx.grid.GridCellAttr()
##                        attr.SetTextColour("black")
##                        self.grid.SetAttr(row+self.start_row, int(col), attr)
##                        self.grid.SetAttr(row+self.start_row, int(col)+17, attr)
                        self.grid.SetCellTextColour(row+self.start_row, int(col), "black")
                        self.grid.SetCellTextColour(row+self.start_row, int(col)+17, "black")
                # set result value
                if len(self.current_table[k[row+self.base_line]][TT["CUT"]]):
                    self.grid.SetCellValue(row+self.start_row, 34, "排除区->有差别")
                    #self.grid.SetCellValue(row+self.start_row, 34, "Cut area->Diff")
                else:
                    self.grid.SetCellValue(row+self.start_row, 34, "            ->有差别")
                    #self.grid.SetCellValue(row+self.start_row, 34, "            ->Diff")
            else:
                # no diff, set black
                for col in range(16):
                    self.grid.SetCellTextColour(row+self.start_row, int(col), "black")
                    self.grid.SetCellTextColour(row+self.start_row, int(col)+17, "black")
                #set result value
                if len(self.current_table[k[row+self.base_line]][TT["CUT"]]):
                    self.grid.SetCellValue(row+self.start_row, 34, "排除区")
                    #self.grid.SetCellValue(row+self.start_row, 34, "Cut")
                else:
                    self.grid.SetCellValue(row+self.start_row, 34, "")

            
            f1_Hex = binascii.hexlify(self.current_table[k[row+self.base_line]][TT["F1"]])
            for col in range(16):
                if col >= len(f1_Hex)/2:
                    self.grid.SetCellValue(row+self.start_row, col, "")
                else:
                    self.grid.SetCellValue(row+self.start_row, col, f1_Hex[col*2:col*2+2])

            f2_Hex = binascii.hexlify(self.current_table[k[row+self.base_line]][TT["F2"]])            
            for col in range(17, 33):
                if (col-17) >= len(f2_Hex)/2:
                    self.grid.SetCellValue(row+self.start_row, col, "")
                else:
                    self.grid.SetCellValue(row+self.start_row, col, f2_Hex[(col-17)*2:(col-17)*2+2])
   

    def OnLoadFile1(self, event):
        dlg = wx.FileDialog(self, wildcard = '*.*', style=wx.OPEN)
        if dlg.ShowModal():
            path = dlg.GetPath()
            if not os.path.isfile(path):
                return
            fileStats = os.stat(path)
            if fileStats[stat.ST_SIZE] > self.max_file_size:
                dlg = wx.MessageDialog(None, message =  '文件大于' + str(self.max_file_size) + '字节',  caption = '错误', style = wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.path1.SetValue(path)
            fileList["F1"] = path
            self.RefreshTable(["F1"])
        dlg.Destroy()

    def OnLoadFile2(self, event):
        dlg = wx.FileDialog(self, wildcard = '*.*', style=wx.OPEN)
        if dlg.ShowModal():
            path = dlg.GetPath()
            if not os.path.isfile(path):
                return
            fileStats = os.stat(path)
            if fileStats[stat.ST_SIZE] > self.max_file_size:
                dlg = wx.MessageDialog(None, message =  '文件大于' + str(self.max_file_size) + '字节',  caption = '错误', style = wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.path2.SetValue(path)
            fileList["F2"] = path
            self.RefreshTable(["F2"])
        dlg.Destroy()

    def OnDefaultSetting(self, event):
        fileList["CUT"] = ""
        self.RefreshTable(["CUT"])
        
    def OnSetting(self, event):
        dlg = wx.FileDialog(self, wildcard = '*.txt', style=wx.OPEN)
        if dlg.ShowModal():
            path = dlg.GetPath()
            fileList["CUT"] = path
            self.RefreshTable(["CUT"])
        dlg.Destroy()

    def OnCompare(self, event):
        if len(self.threads):
            return
        if len(big_table) == 0:
            dlg = wx.MessageDialog(None, message =  '文件为空，没有比较内容', style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        thread = WorkerThread(self)
        self.threads.append(thread)
        thread.start()
        
    def OnPause(self, event):
        while self.threads:
            thread = self.threads[0]
            thread.stop()
            self.threads.remove(thread)

    def ThreadFinished(self, thread):
        while self.threads:
            thread = self.threads[0]
            thread.stop()
            self.threads.remove(thread)
        #self.threads.remove(thread)
        self.RefreshGrid()
        self.count = 0
        diff_line = 0
        cut_line = 0
        for i in range(len(big_table)):
            if len(big_table[i][TT["CUT"]]):
                cut_line += 1
            if len(big_table[i][TT["RST"]]):
                diff_line += 1 
        dlg = wx.MessageDialog(None, message =  '本次比较了: ' + str(len(big_table)) + ' 行\n' +\
                                                '其中排除的有: ' + str(cut_line) + ' 行\n' +\
                                                '相同的有: ' + str(len(big_table)-diff_line) + ' 行\n'+\
                                                '不同的有: ' + str(diff_line) + ' 行\n',  caption = '比较完成', style = wx.OK)
	dlg.ShowModal()
        dlg.Destroy()		
        

    def OnStop(self, event):
        self.count = 0
        self.processing.SetLabel("0/" + str(len(big_table)))
        if len(self.threads) == 0:
            return
        while self.threads:
            thread = self.threads[0]
            thread.stop()
            self.threads.remove(thread)
        
    def UpdateCount(self, count):
        self.count = count
        self.processing.SetLabel(str(self.count+1) + "/" + str(len(big_table)))

##        if count in range(self.base_line, self.base_line + self.grid_lines):
##            self.RefreshGrid()               

    def UpdateTableRst(self, index, val):
        big_table[index][TT["RST"]] = val
        
    def OnNext(self, event):
        if self.grid_lines * (self.curren_page + 1) >= len(big_table):
            return
        self.curren_page += 1
        self.page_index.SetLabel(str(self.curren_page+1))
        self.total_page.SetLabel("/" + str(len(big_table)/self.grid_lines+1))
        self.RefreshGrid()
        
    def OnUp(self, event):
        if self.curren_page == 0:
            return
        self.page_index.SetLabel(str(self.curren_page+1))
        self.total_page.SetLabel("/" + str(len(big_table)/self.grid_lines+1))
        self.curren_page -= 1
        self.RefreshGrid()

    def OnPageGo(self, event):
        p = int(self.page_index.GetLabel())
        if p < 0 or p > int(self.total_page.GetLabel()[1:]):
            return
        self.curren_page = p-1
        self.RefreshGrid()

    def OnAllStat(self, event):
        self.current_table = big_table
        self.curren_page = 0
        self.RefreshGrid()

    def OnCutStat(self, event):
        cut_table = {}
        for i in range(len(big_table)):
            if len(big_table[i][TT["CUT"]]):
                cut_table[i] = big_table[i]
        self.current_table = cut_table
        self.curren_page = 0
        self.RefreshGrid()

    def OnDiffStat(self, event):
        diff_table = {}
        for i in range(len(big_table)):
            if len(big_table[i][TT["RST"]]):
                diff_table[i] = big_table[i]
        self.current_table = diff_table
        self.curren_page = 0
        self.RefreshGrid()

    def OnOutput(self, event):
        #print "Output"
        self.RealExport(self)

    def RealExport(self, event):
        export_path = os.path.join(os.getcwd(), time.strftime("%Y%m%d%H%M%S") + "_export.txt")
        fs = open(export_path, "w")
        fs.write("++++++++++++++++++++++++++++++++++++++++++++Compare Result Export++++++++++++++++++++++++++++++++++++++++++++\n\n")
        fs.write("File1: " +  fileList["F1"] + "\n")
        fs.write("File2: " +  fileList["F2"] + "\n\n")
        for i in range(len(big_table)):
            strF1 = binascii.hexlify(big_table[i][TT["F1"]]) + " "*(32-len(binascii.hexlify(big_table[i][TT["F1"]])))
            strF2 = binascii.hexlify(big_table[i][TT["F2"]]) + " "*(32-len(binascii.hexlify(big_table[i][TT["F2"]])))
            fs.write(strF1 + "    " + strF2 + "    " + big_table[i][TT["RST"]] + "\n")
        fs.close()
        dlg = wx.MessageDialog(None, message = '导出文件为:\n'
                                                + export_path, caption = '导出成功', style = wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnAbout(self, event):
        dlg = wx.MessageDialog(None, message =  'Binary Compare v1.0',  caption = '关于', style = wx.OK)
	dlg.ShowModal()
        dlg.Destroy()

class BinaryComparor(wx.Frame):
    """
    BinaryComparor
    """
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, None, -1, title, size=(850, 800), style = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER |wx.MAXIMIZE_BOX))

        # ---------------------create a menu ---------------------------	
        menubar=wx.MenuBar()
        m_file=wx.Menu()
        m_conf=wx.Menu()
        m_compare=wx.Menu()
        m_table=wx.Menu()
        m_help=wx.Menu()

        m_file.Append(101, '&文件1')
        m_file.Append(102, '&文件2')
        m_file.AppendSeparator()
        m_file.Append(103, '&退出')

        m_conf.Append(111, '&默认配置')
        m_conf.Append(112, '&排除区设置')

        m_compare.Append(121, '&比较')
        m_compare.Append(122, '&暂停')
        m_compare.Append(123, '&停止')

        m_table.Append(131, '&全部报表')
        m_table.Append(132, '&排除区域')
        m_table.Append(133, '&差别区域')
        m_table.Append(134, '&导出')
        

        m_help.Append(141, '&关于')

        menubar.Append(m_file, '&文件')
        menubar.Append(m_conf, '&配置')
        menubar.Append(m_compare, '&比较')
        menubar.Append(m_table, '&报表')
        menubar.Append(m_help, '&帮助')

        self.SetMenuBar(menubar)
        ############# PANEL
        self.panel = MyComparePanel(self,wx.ID_ANY)

        wx.EVT_MENU(self, 101, self.panel.OnLoadFile1)
        wx.EVT_MENU(self, 102, self.panel.OnLoadFile2)
        wx.EVT_MENU(self, 103, self.OnQuit)        
        wx.EVT_MENU(self, 111, self.panel.OnDefaultSetting)
        wx.EVT_MENU(self, 112, self.panel.OnSetting)
        wx.EVT_MENU(self, 121, self.panel.OnCompare)
        wx.EVT_MENU(self, 122, self.panel.OnPause)
        wx.EVT_MENU(self, 123, self.panel.OnStop)

        wx.EVT_MENU(self, 131, self.panel.OnAllStat)
        wx.EVT_MENU(self, 132, self.panel.OnCutStat)
        wx.EVT_MENU(self, 133, self.panel.OnDiffStat)
        wx.EVT_MENU(self, 134, self.panel.OnOutput)

        wx.EVT_MENU(self, 141, self.panel.OnAbout)
        
        ##    wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        ##    wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)

    def OnQuit(self, event):
        self.Close(True)

        
if __name__=='__main__':
	app = wx.PySimpleApp()
	frame = BinaryComparor(None, -1, "Binary Comparer V1.0")
	frame.Show(True)
	app.MainLoop()
