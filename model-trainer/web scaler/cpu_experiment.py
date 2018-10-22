#!/usr/bin/python

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
import csv
from nupic.frameworks.opf.model_factory import ModelFactory
from nupic_output import NuPICFileOutput, NuPICPlotOutput
from nupic.swarming import permutations_runner
import datetime
import generate_data
import model_params
import meme_params
from multiprocessing import Process

# Change this to switch from a matplotlib plot to file output.
DATE_FORMAT = "%m/%d/%y %H:%M"
PLOT = False
MEM_SWARM_CONFIG = {
  "includedFields": [
    {
      "fieldName": "mem",
      "fieldType": "float",
      "maxValue": 100.0,
      "minValue": 0.0
    }
  ],
  "streamDef": {
    "info": "cpu",
    "version": 1,
    "streams": [
      {
        "info": "mem.csv",
        "source": "file://cpu.csv",
        "columns": [
          "*"
        ]
      }
    ]
  },
  "inferenceType": "TemporalAnomaly",
  "inferenceArgs": {
    "predictionSteps": [
      1
    ],
    "predictedField": "mem"
  },
  "swarmSize": "medium"
}

SWARM_CONFIG = {
  "includedFields": [
    {
      "fieldName": "cpu",
      "fieldType": "float",
      "maxValue": 100.0,
      "minValue": 0.0
    }
  ],
  "streamDef": {
    "info": "cpu",
    "version": 1,
    "streams": [
      {
        "info": "cpu.csv",
        "source": "file://cpu.csv",
        "columns": [
          "*"
        ]
      }
    ]
  },
  "inferenceType": "TemporalAnomaly",
  "inferenceArgs": {
    "predictionSteps": [
      1
    ],
    "predictedField": "cpu"
  },
  "swarmSize": "medium"
}


#medium
def swarm_over_data(SWARM_CONFIG):
  return permutations_runner.runWithConfig(SWARM_CONFIG,
    {'maxWorkers': 2, 'overwrite': True})



def run_cpu_experiment():
  input_file = "cpu.csv"
  #generate_data.run(input_file)
  model_params = swarm_over_data(SWARM_CONFIG)
  model = ModelFactory.create(model_params)
  model.enableInference({"predictedField": "cpu"})
  #To load with no swarming 
  #model = ModelFactory.create(model_params)


  

  if PLOT:
    output = NuPICPlotOutput("final_cpu_output")
  else:
    output = NuPICFileOutput("final_cpu_output")

  with open(input_file, "rb") as cpu_input:
    csv_reader = csv.reader(cpu_input)

    # skip header rows
    csv_reader.next()
    csv_reader.next()
    csv_reader.next()

    # the real data
    sumOfUtilityFitness=0.0
    sumOfWeaight = 0.0 
    for row in csv_reader:
      timestamp = datetime.datetime.strptime(row[0], DATE_FORMAT)
      cpu = float(row[1])
      result = model.run({"cpu": cpu})
      prediction = result.inferences["multiStepBestPredictions"][1]
      anomalyScore = result.inferences['anomalyScore']
      anomalyLikelihood = anomalyLikelihoodHelper.anomalyProbability(cpu, anomalyScore, timestamp)
      uc= (anomalyLikelihood * cpu + prediction * anomalyLikelihood )/(anomalyScore + anomalyLikelihood) 
      sumOfUtilityFitness= sumOfUtilityFitness + (float(cpu) * float(anomalyLikelihood))
      sumOfWeaight = sumOfWeaight + float(anomalyLikelihood)
      output.write(timestamp, cpu, prediction, anomalyScore)

  output.close()

  print 'sumOfWeaight: ', sumOfWeaight, 'sumOfUtilityFitness: ', sumOfUtilityFitness
  result_output = 'final_cpu_output'
  with open(input_file, "rb") as result_input:
    csv_reader = csv.reader(result_input)

    # skip header rows
    csv_reader.next()
    csv_reader.next()
    csv_reader.next()
    for row in csv_reader:
      anomalyLikelihood = float(row[4])
      utilityOfCpu= utilityOfCpu + (anomalyLikelihood * sumOfUtilityFitness)/sumOfWeaight
    print 'utilityOfCpu: ', utilityOfCpu


def run_mem_experiment():
  input_file = "mem.csv"
  #generate_data.run(input_file)
  meme_params = swarm_over_data(SWARM_CONFIG)
  model_mem = ModelFactory.create(meme_params)
  model_mem.enableInference({"predictedField": "mem"})


  if PLOT:
    output = NuPICPlotOutput("final_mem_output")
  else:
    output = NuPICFileOutput("final_mem_output")
  
  with open(input_file, "rb") as sine_input:
    csv_reader = csv.reader(sine_input)

    # skip header rows
    csv_reader.next()
    csv_reader.next()
    csv_reader.next()

    # the real data
    for row in csv_reader:
      timestamp = datetime.datetime.strptime(row[0], DATE_FORMAT)
      mem = float(row[1])
      result_mem = model_mem.run({"mem": mem})
      prediction = result_mem.inferences["multiStepBestPredictions"][1]
      anomalyScore = result_mem.inferences['anomalyScore']
      output.write(timestamp, mem, prediction, anomalyScore)
      sumOfUtilityFitness= sumOfUtilityFitness + (float(mem) * float(anomalyLikelihood))
      sumOfWeaight = sumOfWeaight + float(anomalyLikelihood)

  output.close()
  print 'sumOfWeaight: ', sumOfWeaight, 'sumOfUtilityFitness: ', sumOfUtilityFitness
  result_output = 'final_cpu_output'
  with open(input_file, "rb") as result_input:
    csv_reader = csv.reader(result_input)

    # skip header rows
    csv_reader.next()
    csv_reader.next()
    csv_reader.next()
    for row in csv_reader:
      anomalyLikelihood = float(row[3])
      utilityOfmem= utilityOfCpu + (anomalyLikelihood * sumOfUtilityFitness)/sumOfWeaight
    print 'utilityOfCpu: ', utilityOfmem

def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()
if __name__ == "__main__":
   runInParallel(run_cpu_experiment, run_mem_experiment )
