#!/usr/bin/env python

import sys
import os
import struct

endianMap = {"BIG":">","LITTLE":"<"}

'''
class WvsCell(object):
    WvsCellSizeBytes = 14
    def __init__(self,binData,endianess="BIG"):
        self._endianess = endianMap[endianess]
        self.WvsWordsInCell = 0
        self.CellId = 0
        self.SegmentsInCell = 0
        self.ContBit = 0
        self.PointsInSeg = 0
        self.SegStartLatMsb = 0
        self.SegStartLonMsb = 0
        self.SegStartLatLsb = 0
        self.SegStartLonLsb = 0
        self.SegDeltaLat = 0
        self.SegDeltaLon = 0

        if binData and len(binData) >= self.WvsCellSizeBytes:
               self.WvsWordsInCell = struct.unpack("{0}H".format(self._endianess),binData[0:2])[0]
               self.CellId = struct.unpack("{0}H".format(self._endianess),binData[2:4])[0]
               self.SegmentsInCell = struct.unpack("{0}H".format(self._endianess),binData[4:6])[0]
               tmp = struct.unpack("{0}H".format(self._endianess),binData[6:8])[0]
               self.ContBit = tmp & 0x1
               self.PointsInSeg = (tmp >> 1) & 0x1FF
               self.SegStartLatMsb = (tmp >> 10) & 0x7
               self.SegStartLonMsb = (tmp >> 13) & 0x7
               self.SegStartLatLsb = struct.unpack("{0}H".format(self._endianess),binData[8:10])[0]
               self.SegStartLonLsb = struct.unpack("{0}H".format(self._endianess),binData[10:12])[0]
               tmp = struct.unpack("{0}H".format(self._endianess),binData[12:14])[0]
               self.SegDeltaLat = tmp & 0xFF
               self.SegDeltaLon = (tmp >> 8) & 0xFF

    def __str__(self):
        titles = ["WVS Words In Cell","Cell ID","Segments In Cell","Continuation Bit","Points In Segment",
         "Segment Starting Latitude MSB","Segment Starting Longitude MSB","Segment Starting Latitude LSB","Segment Starting Longitude LSB",
         "Segment Point Delta Latitude","Segment Point Delta Longitude"]
        return os.linesep.join(["{0}:  {1}".format(title,value) for title,value in zip(titles,[self.WvsWordsInCell,self.CellId,self.SegmentsInCell,self.ContBit,
                                                                                               self.PointsInSeg,self.SegStartLatMsb,self.SegStartLonMsb,self.SegStartLatLsb,
                                                                                               self.SegStartLonLsb,self.SegDeltaLat,self.SegDeltaLon])])'''

class WvsCell(object):
    WvsCellSizeBytes = 14
    def __init__(self,binData,endianess="BIG"):
        self._endianess = endianMap[endianess]
        self.WvsWordsInDegSq = 0
        self.CellId = 0
        self.SegmentsInCell = 0
        self.ContBit = 0
        self.PointsInSeg = 0
        self.SegStartLatMin = 0
        self.SegStartLonMin = 0
        self.SegDeltaLat = 0
        self.SegDeltaLon = 0

        if binData and len(binData) >= self.WvsCellSizeBytes:
               self.WvsWordsInDegSq = struct.unpack("{0}H".format(self._endianess),binData[0:2])[0]
               self.CellId = struct.unpack("{0}H".format(self._endianess),binData[2:4])[0]
               self.SegmentsInCell = struct.unpack("{0}H".format(self._endianess),binData[4:6])[0]
               tmp = struct.unpack("{0}H".format(self._endianess),binData[6:8])[0]
               self.ContBit = tmp & 0x1
               self.PointsInSeg = (tmp >> 1) & 0x1FF
               segStartLatMsb = (tmp >> 10) & 0x7
               segStartLonMsb = (tmp >> 13) & 0x7
               self.SegStartLatMin = struct.unpack("{0}H".format(self._endianess),binData[8:10])[0] | (segStartLatMsb << 16)
               self.SegStartLonMin = struct.unpack("{0}H".format(self._endianess),binData[10:12])[0] | (segStartLonMsb << 16)
               self.SegDeltaLat = struct.unpack("{0}b".format(self._endianess),binData[12])[0]
               self.SegDeltaLon = struct.unpack("{0}b".format(self._endianess),binData[13])[0]

    def __str__(self):
        titles = ["WVS Words In Degree Square","Cell ID","Segments In Cell","Continuation Bit","Points In Segment",
         "Segment Starting Latitude Mins","Segment Starting Longitude Mins","Segment Point Delta Latitude","Segment Point Delta Longitude"]
        return os.linesep.join(["{0}:  {1}".format(title,value) for title,value in zip(titles,[self.WvsWordsInDegSq,self.CellId,self.SegmentsInCell,self.ContBit,
                                                                                               self.PointsInSeg,self.SegStartLatMin,self.SegStartLonMin,
                                                                                               self.SegDeltaLat,self.SegDeltaLon])])

class WvsFile(object):
    WvsHeaderSizeBytes = 24+2#37
    WvsChecksumSizeBytes = 4
    def __init__(self,filePath,endianess="BIG"):
        self._endianess = endianMap[endianess]
        fData = open(filePath,"rb").read()
        self.Identifier = ""
        self.Version = ""
        self.CntryCode = ""
        self.Header = ""
        self.FileSizeBytes = 0
        self.FileId = ""
        self.WvsDbRcrdSize = 0
        self.WvsCellsInFile = 0 
        self.WvsDataUncertainty = 0
        self.WvsDataScale = 0
        self.WvsThinningThreshold = 0
        self.WvsCells = []           

        if fData:
            #calculate checksum
            validChkSum = struct.unpack("{0}I".format(self._endianess),fData[-4:])[0]
            actualChkSum = sum([ord(b) for b in fData[:-4]])
            if validChkSum == actualChkSum:
                self.Identifier = fData[:10]
                self.Version = fData[10:12]  
                self.CntryCode = fData[12:14]      
                self.Header = fData[14:16]    
                self.FileSizeBytes = struct.unpack("{0}I".format(self._endianess),fData[16:20])[0]
                self.FileId = fData[20:24]
                self.WvsDbRcrdSize = struct.unpack("{0}i".format(self._endianess),fData[24:28])[0]
                self.WvsCellsInFile = struct.unpack("{0}i".format(self._endianess),fData[28:32])[0]
                self.WvsDataUncertainty = struct.unpack("{0}H".format(self._endianess),fData[32:34])[0]
                self.WvsDataScale = struct.unpack("{0}H".format(self._endianess),fData[34:36])[0]
                self.WvsThinningThreshold = struct.unpack("{0}H".format(self._endianess),fData[36:38])[0]

                #read in WVS Cells
                actualCellsInFile,leftOverBytes = divmod((self.FileSizeBytes - self.WvsHeaderSizeBytes - self.WvsChecksumSizeBytes),WvsCell.WvsCellSizeBytes)
                print "FileSize: {0}  ValidFileSize: {1} Cells In File: {2}  Leftover Bytes: {3}".format(len(fData),self.FileSizeBytes,actualCellsInFile,leftOverBytes)
                if actualCellsInFile > 0:
                    for cNum in xrange(actualCellsInFile):
                        cIndex = (WvsCell.WvsCellSizeBytes * cNum) + self.WvsHeaderSizeBytes
                        self.WvsCells.append(WvsCell(fData[cIndex:cIndex+WvsCell.WvsCellSizeBytes],endianess))
            else:
                raise ValueError("Checksum Doesnt Match.  Valid Checksum: {0}  Actual Checksum: {1}".format(validChkSum,actualChkSum))

    def __str__(self):
        titles = ["File Identifier","Version","Country Code","Header","File Size Bytes","File ID","WVS DB Logical Record Size",
                  "Number Of WVS Cells","WVS Data Uncertainty","WVS Data Scale Factor","WVS Thinning Threshold","WVS Cells"]
        wvsCellData = [os.linesep]

        for cellNum,cell in enumerate(self.WvsCells):
            wvsCellData.append("  Cell {0}:".format(cellNum))
            wvsCellData.append(os.linesep.join(["  {0}".format(l) for l in str(cell).split(os.linesep)]))
            wvsCellData.append(os.linesep)

        retVal = os.linesep.join(["{0}:  {1}".format(title,value) for title,value in zip(titles,[self.Identifier,self.Version,self.CntryCode,self.Header,self.FileSizeBytes,
                                                                                               self.FileId,self.WvsDbRcrdSize,self.WvsCellsInFile,self.WvsDataUncertainty,
                                                                                               self.WvsDataScale,self.WvsThinningThreshold,os.linesep.join(wvsCellData)])])

        return retVal
                               


#main method
if "__main__" in __name__:
    filePath = sys.argv[1]
    wvsData = WvsFile(filePath)
    print wvsData
