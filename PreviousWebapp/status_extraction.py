import numpy as np
import xml.etree.ElementTree as ET
import xml.sax
from time import sleep

#f = open("System Statuses.txt","r+")


# Taking "gfg input file.txt" as input file
# in reading mode
with open("dummy.txt", "r") as input:
      
    # Creating "gfg output file.txt" as output
    # file in write mode
    with open("dummy.xml", "w") as output:
          
        # Writing each line from input file to
        # output file using loop
        for line in input:
            output.write(line)


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.CompressorStatus = ""
        self.HighBoundary = ""
        self.LowBoundary = ""
        self.DesiredTemp = ""
        self.ADREnabled = ""
        self.PreCoolingStart = ""
        self.Price = ""

   # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if(tag == "Name"):
            print("*****ADR Parameter*****")
            title = self.CurrentData
            print("System Setting:")

   # Call when an elements ends
    def endElement(self, tag):
        if(self.CurrentData == "Price"):
            print("Price:", self.Price)
        elif(self.CurrentData == "compressor status"):
            print("Compressor Status:", self.CompressorStatus)
        elif(self.CurrentData == "High boundary"):
            print("High Temperature Boundary:", self.HighBoundary)
        elif(self.CurrentData == "Low boundary"):
            print("Low Temperature Boundary:", self.LowBoundary)
        elif(self.CurrentData == "Desired temp"):
            print("Desired Temperature:", self.DesiredTemp)
        elif(self.CurrentData == "ADR enabled"):
            print("ADR Enabled", self.ADREnabled)
        elif(self.CurrentData == "Pre-cooling start"):
            print("Pre-cooling Start Time", self.PreCoolingStart)
        self.CurrentData = ""

   # Call when a character is read
    def characters(self, content):
        if(self.CurrentData == "Price"):
            self.price = content
        elif(self.CurrentData == "compressor status"):
            self.qty = content
        elif(self.CurrentData == "High boundary"):
            self.company = content
        elif(self.CurrentData == "Low boundary"):
            self.company = content
        elif(self.CurrentData == "Desired temp"):
            self.company = content
        elif(self.CurrentData == "ADR enabled"):
            self.company = content
        elif(self.CurrentData == "Pre-cooling start"):
            self.company = content

# create an XMLReader
parser = xml.sax.make_parser()

# turn off namepsaces
parser.setFeature(xml.sax.handler.feature_namespaces, 0)

# override the default ContextHandler
Handler = XMLHandler()
parser.setContentHandler( Handler )
parser.parse("dummy.xml")
