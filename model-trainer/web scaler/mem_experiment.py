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


#medium
def swarm_over_data(SWARM_CONFIG):
  return permutations_runner.runWithConfig(SWARM_CONFIG,
    {'maxWorkers': 2, 'overwrite': True})



def run_mem_experiment():
  input_file = "cpu.csv"
  generate_data.run(input_file)
  model_params = swarm_over_data(SWARM_CONFIG)
  if PLOT:
    output = NuPICPlotOutput("final_mem_output")
  else:
    output = NuPICFileOutput("final_mem_output")
  model = ModelFactory.create(model_params)
  model.enableInference({"predictedField": "mem"})

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
      result = model.run({"mem": mem})
      prediction = result.inferences["multiStepBestPredictions"][1]
      anomalyScore = result.inferences['anomalyScore']
      output.write(timestamp, mem, prediction, anomalyScore)

  output.close()



if __name__ == "__main__":
  run_cpu_experiment()
