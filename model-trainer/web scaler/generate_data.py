#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""A simple script to generate a CSV with sine data."""

import csv
import math
import psutil
import datetime
import time
import requests
ROWS = 300
SECONDS_PER_STEP= 30
DATE_FORMAT = "%m/%d/%y %H:%M"
def run(filename="cpu.csv"):
  filename1="mem.csv"
  filename2="disk.csv"
  print "Generating sine data into %s" % filename
  print "Generating sine data into %s" % filename1
  print "Generating sine data into %s" % filename2

  fileHandle = open(filename,"w")
  writer = csv.writer(fileHandle)
  writer.writerow(["timestamp","cpu"])
  writer.writerow(["datetime","float"])
  writer.writerow(["",""])
  
  fileHandle1 = open(filename1,"w")
  writer1 = csv.writer(fileHandle1)
  writer1.writerow(["timestamp","mem"])
  writer1.writerow(["datetime","float"])
  writer1.writerow(["",""])

  fileHandle2 = open(filename2,"w")
  writer2 = csv.writer(fileHandle2)
  writer2.writerow(["timestamp","disk"])
  writer2.writerow(["datetime","float"])
  writer2.writerow(["",""])

  for i in range(ROWS):
              response = requests.get('http://admin:admin@192.168.99.105:9090/api/v1/query?query=sum(irate(node_cpu%7Bmode%3D%22idle%22%7D%5B30s%5D)%20*%20on(instance)%20group_left(node_name)%20node_meta%7Bnode_id%3D~%22.%2B%22%7D)%20*%20100%20%2F%20count(node_cpu%7Bmode%3D%22user%22%7D%20*%20on(instance)%20group_left(node_name)%20node_meta%7Bnode_id%3D~%22.%2B%22%7D)%20&start=1538182792&end=1538182852&step=30')
              response1 = requests.get('http://admin:admin@192.168.99.105:9090/api/v1/query?query=sum((node_memory_MemAvailable%20%2F%20node_memory_MemTotal)%20*%20on(instance)%20group_left(node_name)%20node_meta%7Bnode_id%3D~%22.%2B%22%7D%20*%20100)%20%2F%20count(node_meta%20*%20on(instance)%20group_left(node_name)%20node_meta%7Bnode_id%3D~%22.%2B%22%7D)&start=1538181656&end=1538182556&step=30')
              response2 = requests.get('http://admin:admin@192.168.99.105:9090/api/v1/query?query=sum((node_filesystem_free%7Bmountpoint%3D%22%2F%22%7D%20%2F%20node_filesystem_size%7Bmountpoint%3D%22%2F%22%7D)%20*%20on(instance)%20group_left(node_name)%20node_meta%7Bnode_id%3D~%22.%2B%22%7D%20*%20100)%20%2F%20count(node_meta%20*%20on(instance)%20group_left(node_name)%20node_meta%7Bnode_id%3D~%22.%2B%22%7D)&start=1538181830&end=1538182730&step=30')

              #get Disk 
              diskResult = response2.json()
              diskData = diskResult['data']['result']
              if len(diskData) > 0:
                print 'disk: ', diskData[0]['value']
                diskValue = diskData[0]['value']
                timestamp = datetime.datetime.fromtimestamp(
                  float(diskValue[0])).strftime('%m/%d/%y %H:%M')
                disk = float(diskValue[1])
                writer2.writerow([timestamp, disk])

              # get MEM   
              
              memResult = response1.json()
              memData = memResult['data']['result']
              if len(memData) > 0:
                print 'Mem: ' ,memData[0]['value']
                memValue = memData[0]['value']
                timestamp = datetime.datetime.fromtimestamp(
                  float(memValue[0])).strftime('%m/%d/%y %H:%M')
                mem = float(memValue[1])
                writer1.writerow([timestamp, mem])

              #git CPU 
              results = response.json()
              cpuData = results['data']['result'] 
              if len(cpuData) > 0:
                cpuValue = cpuData[0]['value']
                print 'cpuValue: ',diskData[0]['value']
                timestamp = datetime.datetime.fromtimestamp(
                  float(cpuValue[0])).strftime('%m/%d/%y %H:%M')
                cpu_value = float(cpuValue[1])
                writer.writerow([timestamp, cpu_value])
              
              time.sleep(1)
               
  fileHandle.close()
  fileHandle1.close()
  fileHandle2.close()
  print "Generated %i rows of output data into %s" % (ROWS, filename)
  print "Generated %i rows of output data into %s" % (ROWS, filename1)
  print "Generated %i rows of output data into %s" % (ROWS, filename2)


if __name__ == "__main__":
  run()
