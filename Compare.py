#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: cmpImages.py file1 file2
#
# This script attempts to compare 2 binary files
# and give a summary on the offsets where they
# differ.
#

import os
import stat
import sys
import time
import struct

def printError(msg):
    sys.stderr.write( "%s<br>" % msg )

#convert string to hex
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    return reduce(lambda x,y:x+y, lst)

#convert hex repr to string
def toStr(s):
    return s and chr(atoi(s[:2], base=16)) + toStr(s[2:]) or ''


def compare_all(data1, data2, fileList, temp_path, cut_type):
    differ = 0
    differCount = 0
    differStart, differStop = 0, 0
    currByteOffset = 0
    larger = 0

    ### Check the 2 orignal files
    if len(data1) > len(data2):
        bytesTobeRead = len(data1)
        maxCompare = len(data2)
        larger = 1
    else:
        bytesTobeRead = len(data2)
        maxCompare = len(data1)
        larger = 2
    maxLength = bytesTobeRead
    currReadblock = bytesTobeRead
    
    if cut_type == 0:
        f_all_str = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "allstr.html"), "w")
        f_all_hex = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "allhex.html"), "w")

        fileList["Compare All"]["Str"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "allstr.html")
        fileList["Compare All"]["Hex"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "allhex.html")

        f_all_str.write("<br>++++++++++++++++++Compare on whole files++++++++++++++++++++<br>")
        f_all_hex.write("<br>++++++++++++++++++Compare on whole files++++++++++++++++++++<br>")
    elif cut_type == 1:
        f_all_str = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "tempstr.html"), "w")
        f_all_hex = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temphex.html"), "w")

        fileList["Compare Temp File"]["Str"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "tempstr.html")
        fileList["Compare Temp File"]["Hex"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temphex.html")

        f_all_str.write("<br>++++++++++++++++++Compare on temp files++++++++++++++++++++<br>")
        f_all_hex.write("<br>++++++++++++++++++Compare on temp files++++++++++++++++++++<br>")
    else:
        return
    
    if (differ != 0 or cmp(data1, data2) != 0):

        for index in range(currReadblock):
            # print "%d : %s, %s" % (index, data1[index], data2[index])

            if (data1[index] != data2[index]):
                if (differ == 0):
                    differ = 1
                    differCount += 1
                    differStart = differStop = currByteOffset + index
                else:
                    differStop = currByteOffset + index
            else:
                if (differ != 0):
                    differ = 0
                    if (differStart == differStop):
                        ss = "Differ at byte %s<br>" % differStart
                        f_all_str.write(ss)
                        f_all_hex.write(ss)
                        
                        f_all_str.write('<font color="#ff0000">' + data1[differStart] + '</font>')
                        #f_all_hex.write(hex(ord(data1[differStart])))
                        f_all_hex.write('<font color="#ff0000">' + toHex(data1[differStart])+ '</font>')
                        f_all_str.write("<br>")
                        f_all_hex.write("<br>")

                        f_all_str.write(data2[differStart])
                        f_all_hex.write(toHex(data2[differStart]))
                        f_all_str.write("<br>")
                        f_all_hex.write("<br>")
                    else:
                        ss = "Differ from byte %s to %s (%d bytes)<br>"  \
                                     % (differStart, differStop, differStop - differStart + 1)

                        f_all_str.write(ss)
                        f_all_hex.write(ss)
                        
                        f_all_str.write('<font color="#ff0000">' + data1[int(differStart):int(differStop)+1] + '</font>')
                        f_all_hex.write('<font color="#ff0000">' + toHex(data1[int(differStart):int(differStop)+1]) + '</font>')
                        f_all_str.write("<br>")
                        f_all_hex.write("<br>")

                        f_all_str.write(data2[int(differStart):int(differStop)+1])
                        f_all_hex.write(toHex(data2[int(differStart):int(differStop)+1]))
                        f_all_str.write("<br>")
                        f_all_hex.write("<br>")

            if differStop >= maxCompare - 1:
                if (differ != 0):
                    differ = 0
                    if (differStart == differStop):
                        ss = "Differ at byte %s<br>" % differStart
                        f_all_str.write(ss)
                        f_all_hex.write(ss)
                        
                        f_all_str.write('<font color="#ff0000">' + data1[differStart] + '</font>')
                        f_all_hex.write('<font color="#ff0000">' + toHex(data1[differStart]) + '</font>')
                        f_all_str.write("<br>")
                        f_all_hex.write("<br>")

                        f_all_str.write(data2[differStart])
                        f_all_hex.write(toHex(data2[differStart]))
                        f_all_str.write("<br>")
                        f_all_hex.write("<br>")
                    else:
                        ss = "Differ from byte %s to %s (%d bytes)<br>"  \
                                     % (differStart, differStop, differStop - differStart + 1)

                        f_all_str.write(ss)
                        f_all_hex.write(ss)
                        
                        f_all_str.write('<font color="#ff0000">' + data1[int(differStart):int(differStop)+1] + '</font>')
                        f_all_hex.write('<font color="#ff0000">' + toHex(data1[int(differStart):int(differStop)+1]) + '</font>')
                        f_all_str.write("<br>")
                        f_all_hex.write("<br>")

                        f_all_str.write(data2[int(differStart):int(differStop)+1])
                        f_all_hex.write(toHex(data2[int(differStart):int(differStop)+1]))
                        f_all_str.write("<br>")
                        f_all_hex.write("<br>")
                        
                        if larger == 1:
                            ss = "File %d have extra data from %s to %s (%d bytes)<br>"\
                                 % (larger, maxCompare, maxLength, maxLength-maxCompare)

                            f_all_str.write(ss)
                            f_all_hex.write(ss)
                            
                            f_all_str.write('<font color="#ff0000">' + data1[maxCompare:] + '</font>')
                            f_all_hex.write('<font color="#ff0000">' + toHex(data1[maxCompare:]) + '</font>')
                            f_all_str.write("<br>")
                            f_all_hex.write("<br>")


                        elif larger == 2:
                            ss = "File %d have extra data from %s to %s (%d bytes)<br>"\
                                 % (larger, maxCompare, maxLength, maxLength-maxCompare)

                            f_all_str.write(ss)
                            f_all_hex.write(ss)

                            f_all_str.write(data2[maxCompare:])
                            f_all_hex.write(toHex(data2[maxCompare:]))
                            f_all_str.write("<br>")
                            f_all_hex.write("<br>")


                break
    #currByteOffset += currReadblock
    f_all_str.close()
    f_all_hex.close()
    return differCount

def get_chars(data, a1):
    getchars = ""
    for i in range(0, len(data)):
        if i in range(a1[0], a1[1]):
            getchars += data[i]
        if len(getchars) == len(range(a1[0], a1[1])):
            break

    return getchars

def cut_data(data1, data2, arealist1, arealist2, fileList, temp_path):
    f_cut_str = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "cutstr.html"), "w")
    f_cut_hex = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "cuthex.html"), "w")

    fileList["Compare Cut Area"]["Str"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "cutstr.html")
    fileList["Compare Cut Area"]["Hex"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "cuthex.html")

    f_cut_str.write("<br>++++++++++++++++++File1 Cut Areas++++++++++++++++++++<br>")
    f_cut_hex.write("<br>++++++++++++++++++File1 Cut Areas++++++++++++++++++++<br>")
    
    for a1 in arealist1:
        file1_chars = get_chars(data1, a1)
        file2_chars = get_chars(data2, a1)
        rst_String = "Same!!"
        if file1_chars != file2_chars:
            rst_String = "Different!!"
        f_cut_str.write("<br>" + str(a1[0]) + "~" + str(a1[1]) + " == " + rst_String + "<br>")
        f_cut_str.write('<font color="#ff0000">' + file1_chars + '</font>')
        f_cut_str.write("<br>")
        f_cut_str.write(file2_chars)
        f_cut_str.write("<br>")
        
        f_cut_hex.write("<br>" + str(a1[0]) + "~" + str(a1[1]) + " == " + rst_String + "<br>")
        f_cut_hex.write('<font color="#ff0000">' + toHex(file1_chars) + '</font>')
        f_cut_hex.write("<br>")
        f_cut_hex.write(toHex(file2_chars))
        f_cut_hex.write("<br>")

    f_cut_str.write("<br>++++++++++++++++++File2 Cut Areas++++++++++++++++++++<br>")
    f_cut_hex.write("<br>++++++++++++++++++File2 Cut Areas++++++++++++++++++++<br>")


    for a2 in arealist2:
        file1_chars = get_chars(data1, a2)
        file2_chars = get_chars(data2, a2)
        rst_String = "Same!!"
        if file1_chars != file2_chars:
            rst_String = "Different!!"
        f_cut_str.write("<br>" + str(a2[0]) + "~" + str(a2[1]) + " == " + rst_String + "<br>")
        f_cut_str.write('<font color="#ff0000">' + file1_chars + '</font>')
        f_cut_str.write("<br>")
        f_cut_str.write(file2_chars)
        f_cut_str.write("<br>")
        
        f_cut_hex.write("<br>" + str(a2[0]) + "~" + str(a2[1]) + " == " + rst_String + "<br>")
        f_cut_hex.write('<font color="#ff0000">' + toHex(file1_chars) + '</font>')
        f_cut_hex.write("<br>")
        f_cut_hex.write(toHex(file2_chars))
        f_cut_hex.write("<br>")    


    f_cut_str.close()
    f_cut_hex.close()
        



    ############# Return Left #################
    cut_positions1 = []
    left1 = ''
    for a1 in arealist1:
        cut_positions1 = cut_positions1 + range(a1[0], a1[1])
    for i in range(0, len(data1)):
        if i in cut_positions1:
            continue
        left1 += data1[i]
    #############
    cut_positions2 = []
    left2 = ''
    for a2 in arealist2:
        cut_positions2 = cut_positions2 + range(a2[0], a2[1])
    for i in range(0, len(data2)):
        if i in cut_positions2:
            continue
        left2 += data2[i]

    return left1, left2

maxReadBlock = 16 * 1024 * 1024

def go_compare(fileList, temp_path, cut_path):
    try:
        file1Stats = os.stat(fileList["File1"]["Str"]) 
    except os.error, value:
        printError("Cannot get stat on %s: %s" % (fileList["File1"]["Str"], value[1]))
        sys.exit(value[0])

    file1Info = {
        'Path' : fileList["File1"]["Str"],
        'Name' : os.path.basename(fileList["File1"]["Str"]),
        'Size' : file1Stats [ stat.ST_SIZE ],
        'LastModified' : time.ctime ( file1Stats [ stat.ST_MTIME ] ),
        'LastAccessed' : time.ctime ( file1Stats [ stat.ST_ATIME ] ),
        'CreationTime' : time.ctime ( file1Stats [ stat.ST_CTIME ] ),
        'Mode' : file1Stats [ stat.ST_MODE ]
    }

    try:
        file2Stats = os.stat(fileList["File2"]["Str"]) 
    except os.error, value:
        printError("Cannot get stat on %s: %s" % (fileList["File2"]["Str"], value[1]))
        sys.exit(value[0])

    file2Info = {
        'Path' : fileList["File2"]["Str"],
        'Name' : os.path.basename(fileList["File2"]["Str"]),
        'Size' : file2Stats [ stat.ST_SIZE ],
        'LastModified' : time.ctime ( file2Stats [ stat.ST_MTIME ] ),
        'LastAccessed' : time.ctime ( file2Stats [ stat.ST_ATIME ] ),
        'CreationTime' : time.ctime ( file2Stats [ stat.ST_CTIME ] ),
        'Mode' : file2Stats [ stat.ST_MODE ]
    }

    f_report_path = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_report.html")
    fileList["Report"]["Str"] = f_report_path    
    fs_report = open(f_report_path, "w")

    ################Basic Check###################################
    if  file2Info['Name'] != file1Info['Name']:
        fs_report.write( "Files have different names (%s and %s)<br>" \
                    % (file1Info['Name'], file2Info['Name']) )

    if (file1Info['Size'] != file2Info['Size']):
        fs_report.write( "Files have different sizes (%d and %d)<br><br>" \
                    % (file1Info['Size'], file2Info['Size']) )
    if file1Info['Size'] > maxReadBlock or file2Info['Size'] > maxReadBlock:
        fs_report.write( "<br>File is too large!<br>")
        return
    ################################################################

    # open file
    try:
        file1 = open(fileList["File1"]["Str"], 'rb')
    except IOError, eStr:
        fs_report.write( "<br>Cannot open %s: %s<br>" % (fileList["File1"]["Str"], eStr) )
        return

    try:
        file2 = open(fileList["File2"]["Str"], 'rb')
    except IOError, eStr:
        fs_report.write( "<br>Cannot open %s: %s<br>" % (fileList["File2"]["Str"], eStr) )
        return
    
    data1 = file1.read(maxReadBlock)
    data2 = file2.read(maxReadBlock)

    file2.close()
    file1.close()
    ###########Write HEX for file1 and file2
    f1_hex_path = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + file1Info['Name'])
    f1_hex = open(f1_hex_path, "w")
    f1_hex.write(toHex(data1))
    f1_hex.close()

    fileList["File1"]["Hex"] = f1_hex_path

    f2_hex_path = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + file2Info['Name'])
    f2_hex = open(f2_hex_path, "w")
    f2_hex.write(toHex(data2))
    f2_hex.close()

    fileList["File2"]["Hex"] = f2_hex_path

    ############
    #areas to compare
    #[filename, from, to]
    areaList1 = []
    areaList2 = []
    if os.path.isfile(cut_path):       
        fs = open(cut_path, "r")
        lines = fs.readlines()
        for m in lines:
            fName, areaStr = m.split(":")
            if fName == "File1":
                for n in areaStr.split(","):
                    i, j = n.strip().split("~")
                    areaList1 = areaList1 + [[int(i), int(j)],]
            if fName == "File2":
                for n in areaStr.split(","):
                    i, j = n.split("~")
                    areaList2 = areaList2 + [[int(i), int(j)],]

    #fs_report.write( "<br>文件1包含%d个排除区域<br>" % (len(areaList1)) )
    #fs_report.write( "<br>文件2包含%d个排除区域<br>" % (len(areaList2)) )
    fs_report.write( "File 1 includes %d cut sections<br>" % (len(areaList1)) )
    fs_report.write( "File 2 includes %d cut sections<br><br>" % (len(areaList2)) )   

    #print "<br>++++++++++++++++++Compare on whole files++++++++++++++++++++<br>"
    all_rst = compare_all(data1, data2, fileList, temp_path, 0)
    #fs_report.write( "<br>两个文件内容有%d处不相同<br>" % (all_rst) )
    fs_report.write( "The 2 files are different at total %d blocks<br>" % (all_rst) )

    left1, left2 = cut_data(data1, data2, areaList1, areaList2, fileList, temp_path)

    f_temp1_str = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temp1str.html"), "w")
    f_temp2_str = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temp2str.html"), "w")
    f_temp1_hex = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temp1hex.html"), "w")
    f_temp2_hex = open(os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temp2hex.html"), "w")

    fileList["Temp1"]["Str"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temp1str.html")
    fileList["Temp1"]["Hex"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temp1hex.html")
    fileList["Temp2"]["Str"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temp2str.html")
    fileList["Temp2"]["Hex"] = os.path.join(temp_path, time.strftime("%Y%m%d%H%M%S") + "_" + "temp2hex.html")

    f_temp1_str.write(left1)
    f_temp2_str.write(left2)
    f_temp1_hex.write(toHex(left1))
    f_temp2_hex.write(toHex(left2))

    f_temp1_str.close()
    f_temp2_str.close()
    f_temp1_hex.close()
    f_temp2_hex.close()
    
    #print "<br>++++++++++++++++++Compare after CUTS++++++++++++++++++++<br>"
    temp_rst = compare_all(left1, left2, fileList, temp_path, 1)
    #fs_report.write("<br>两个文件比较区域内容有%d处不相同<br>" % (all_rst) )
    fs_report.write("The 2 temp are different at total %d blocks<br>" % (all_rst) )


##
##
##for area in areaList:
##    # get block for file1
##    file1block = get_block_from_data(data1, area[1], area[2])
##    file2block = get_block_from_data(data2, area[1], area[2])
##
##    compare_area(file1block, file2block)
##
##
##
##maxLength = bytesTobeRead
##
##print maxLength, maxCompare
##currReadblock = 0
##currByteOffset = 0
##
##
##
##
##   
##while bytesTobeRead > 0:
##
##    
##        #currReadblock = maxReadBlock
##    
##
##    data1 = file1.read(currReadblock)
##    data2 = file2.read(currReadblock)
##    bytesTobeRead -= currReadblock
##
##    # print "%d read, %d to go..." % (currReadblock, bytesTobeRead)
##    # print "%dk read, %dk to go..." % (currReadblock / 1024, bytesTobeRead / 1024)
##
##    # use (quick) compare routine if we can to save us from iterating
##    # through lots of bytes individually
##    if (differ != 0 or cmp(data1, data2) != 0):
##
##        for index in range(currReadblock):
##            # print "%d : %s, %s" % (index, data1[index], data2[index])
##
##            if (data1[index] != data2[index]):
##                if (differ == 0):
##                    differ = 1
##                    differCount += 1
##                    differStart = differStop = currByteOffset + index
##                else:
##                    differStop = currByteOffset + index
##            else:
##                if (differ != 0):
##                    differ = 0
##                    if (differStart == differStop):
##                        print "Differ at byte %s" % differStart
##                        print data1[differStart]
##                        print data2[differStart]
##                        print hex(ord(data1[differStart]))
##                    else:
##                        print "Differ from byte %s to %s (%d bytes)" \
##                              % (differStart, differStop, differStop - differStart + 1)
##                        
##                        #print data1[int(differStart):int(differStop)+1]
##                        #print data2[int(differStart):int(differStop)+1]
##                        print toHex(data1[int(differStart):int(differStop)+1])
##                        print toHex(data2[int(differStart):int(differStop)+1])
##            if differStop >= maxCompare - 1:
##                if (differ != 0):
##                    differ = 0
##                    if (differStart == differStop):
##                        print "Differ at byte %s" % differStart
##                        print data1[differStart]
##                        print data2[differStart]
##                    else:
##                        print "Differ from byte %s to %s (%d bytes)" \
##                              % (differStart, differStop, differStop - differStart + 1)
##
##                        #print data1[int(differStart):int(differStop)+1]
##                        #print data2[int(differStart):int(differStop)+1]
##                        print toHex(data1[int(differStart):int(differStop)+1])
##                        print toHex(data2[int(differStart):int(differStop)+1])                        
##                        if larger:
##                            print "File %d have extra data from %s to %s (%d bytes)" \
##                                  % (larger, maxCompare, maxLength, maxLength-maxCompare)
##                            if larger > 1:
##                                print data2[maxCompare:]
##                            else:
##                                print data1[maxCompare:]
##
##                break
##                
##
##    currByteOffset += currReadblock
##
### do a final check to cover cases where files differ up to last byte
##if (differ != 0):
##    differ = 0
##    if (differStart == differStop):
##        print "Differ at byte %s" % differStart
##    else:
##        print "Differ from byte %s to %s (%d bytes)" \
##              % (differStart, differStop, differStop - differStart + 1)
##        print toHex(data1[int(differStart):int(differStop)+1])
##        print toHex(data2[int(differStart):int(differStop)+1]) 
##        if larger:
##            print "File %d have extra data from %s to %s (%d bytes)" \
##                  % (larger, maxCompare, maxLength, maxLength-maxCompare)
##            if larger > 1:
##                print data2[maxCompare:]
##            else:
##                print data1[maxCompare:]
##file2.close()
##file1.close()
##
##if (differCount == 0):
##    sys.exit(0)
##
##print ""
##print "Total diff blocks %d" % differCount
##
##sys.exit(251)
