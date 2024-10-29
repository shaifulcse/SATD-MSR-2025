import re
import os

SRC_PATH="../../data/uncleaned/"
DEST_PATH="../../data/cleaned/"

selected_features = [         "Age",
                     "SLOCStandard",
                     "Readability",
                     "SimpleReadability",
                     "NVAR",
                     "NCOMP",
                     "Mcclure",
                     "McCabe",
                     "IndentSTD",
                     "MaximumBlockDepth",
                     "totalFanOut",
                     "Length",
                     "MaintainabilityIndex",
                     "SATD",
                     "Parameters",
                     "LocalVariables",
                     "ChangeAtMethodAge",
                     "NewAdditions",
                     "DiffSizes",
                     "EditDistances",
                     "CriticalEditDistances",
                     "TangledWMoveandFileRename",
                     "Buggycommiit",
                     "PotentiallyBuggycommit",
                     "RiskyCommit",
                     "file"
                     ]

def convert(indexes):

  for file in os.listdir(SRC_PATH):
    fr = open(SRC_PATH+file,"r")
    line = fr.readline()
    lines = fr.readlines()
    fr.close()
    fw = open(DEST_PATH+file,"w")

    # Writing the header with selected features

    for feature in selected_features:
      fw.write(feature + "\t")
    fw.write("\n")

    c = 0 # number of problems

    for line in lines:
      line = line.strip()
      problem =  check_problem(line, indexes) 
      if problem == 1:
          c+=1
          continue
      data = line.strip().split("\t")
      for feature in selected_features:
        fw.write(data[indexes[feature]] + "\t")
      fw.write("\n")  

    print (file, len(lines)-1, c)
    fw.flush()
    fw.close()

def find_index():
  indexes = {}
  fr = open(SRC_PATH + "checkstyle" + ".csv")
  line = fr.readline()  # headerfeature_index
  line = line.strip()
  data = line.split("\t")
  for i in range(len(data)):
    indexes[data[i]] = i
  return indexes

def check_problem(line, indexes):
  line = line.strip()
  data = line.split("\t")
  age = int(data[indexes["Age"]])
  if age < 0:
    return 1
  dates =  data[indexes["ChangeAtMethodAge"]]
  dates = dates.split("#")
  prev = 0
  for d in dates:
    d = int(d)
    if d < 0:
      return 1
    if d < prev:
      return 1
    prev = d 
  
  return 0

if __name__ == "__main__":
  indexes = find_index()
  convert(indexes) 