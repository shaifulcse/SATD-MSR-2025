import re
import os
from util import utility
from util import graphs
import cliffsDeltaModule
from scipy import stats


SRC_PATH="../../data/cleaned/"

indicators = [       "TangledWMoveandFileRename",
                     "Buggycommiit",
                     "PotentiallyBuggycommit",
                     "RiskyCommit"]

def find_index():
  indexes = {}
  fr = open(SRC_PATH + "checkstyle" + ".csv")
  line = fr.readline() 
  line = line.strip()
  data = line.split("\t")
  for i in range(len(data)):
    indexes[data[i]] = i
  return indexes

def is_SATD_any_time(ls):
  is_satd = False
  for v in ls:
    if int(v) == 1:
      is_satd = True
      break
  return is_satd

def is_SATD_beginning(ls):
  if int(ls[0]) == 1:
    return True
  return False 

def process(indexes):

  metrics = {}
  ## aggregated results
  metrics["aggr"] = {}
  metrics["aggr"]["SATD"] = []
  metrics["aggr"]["NOT_SATD"] = []

  for file in os.listdir(SRC_PATH):
    metrics[file] = {}
    metrics[file]["SATD"] = []
    metrics[file]["NOT_SATD"] = []
    
    fr = open(SRC_PATH + file)
    fr.readline()
    for line in fr:
      line = line.strip()
      data = line.split("\t")
      age = int(data[0])
      if set_age_threshold and age < age_threshold:
        continue

      satds = data[indexes["SATD"]]
      satds = satds.split("#")

      tangled = data[indexes["TangledWMoveandFileRename"]]
      tangled = tangled.split("#")

      bugcommits = data[indexes["Buggycommiit"]]
      bugcommits = bugcommits.split("#")

      riskycommits = data[indexes["RiskyCommit"]]
      riskycommits = riskycommits.split("#")

      
      change_dates = data[indexes["ChangeAtMethodAge"]]
      change_dates = change_dates.split("#") 

      if satd_any_time:
        is_satd = is_SATD_any_time(satds)
      else:
        is_satd = is_SATD_beginning(satds) 
        if not is_satd: # beginning is not true, but later can be found, should be discarded
          if is_SATD_any_time(satds):
            continue      
          
      if not conservative_bugs:    
        bugs = riskycommits
      else:
        bugs = bugcommits
      value = get_bug_proneness(tangled, bugs, change_dates)    
      if value > 0:
        value = 1
      if is_satd:
        metrics[file]["SATD"].append(value)
        metrics["aggr"]["SATD"].append(value)
      else:
        metrics[file]["NOT_SATD"].append(value) 
        metrics["aggr"]["NOT_SATD"].append(value)

      #print (file, data[len(data)-1], change_dates, tangled, bugcommits, riskycommits, value)  
    fr.close()

  return metrics     
    
 
def cliffs(metrics):  
  X = []
  Y = []
  satd_ratios = []
  not_satd_ratios = []

  for project in metrics:
    #print(project)
    if project == "aggr":
      continue 
    sm = 0
    for v in metrics[project]["SATD"]:
      sm += v 
    ratio = sm / len(metrics[project]["SATD"])
    satd_ratios.append(ratio)
    
    sm = 0
    for v in metrics[project]["NOT_SATD"]:
      sm += v 
    ratio = sm / len(metrics[project]["NOT_SATD"])
    not_satd_ratios.append(ratio)

  print(statistics(satd_ratios, not_satd_ratios))


    
def statistics(x, y):
  d, size = cliffsDeltaModule.cliffsDelta(x, y)
  st = stats.mannwhitneyu(x, y)
  p_value = st[1]  
  return p_value, d, size

def calculate_individual(metrics):
  cliffs = {}
  cliffs['negligible'] = 0
  cliffs['small'] = 0
  cliffs['medium'] = 0
  cliffs['large'] = 0
  cliffs['+'] = 0
  cliffs['-'] = 0
  insignificant = 0
  total = 0
  for project in metrics:
    if project == "aggr":
      continue 
    p, d, size = statistics(metrics[project]["SATD"], metrics[project]["NOT_SATD"])
    if p > 0.05:
      #print (project, feature, p, len(metrics[project]["SATD"]))
      insignificant += 1
    else:
      total += 1
      cliffs[size] += 1
      if (float(d) < 0):
        cliffs['-'] += 1
      else:
        cliffs['+'] += 1   
  return total, insignificant, cliffs     

  

def printLatex(feature, p, d, size):
  if float(d) < 0:
    d = "-"
  else:
    d = "+"  
  print("{}&{:.2f}&{}&{}\\\\\n".format(feature, 
                                              p,
                                              d,
                                              size))
  

def get_bug_proneness(tangled, bugs, change_dates)  :
  is_buggy = 0
  for i in range (1, len(bugs)):
    if set_age_threshold and int(change_dates[i]) > age_threshold:
      return is_buggy 
    if conservative_bugs:
      if int(bugs[i]) == 1 and int(tangled[i]) <= max_tangled:
        is_buggy += 1
    else:
        if int(bugs[i]) == 1:
          is_buggy += 1    
          
  return is_buggy        


def calculate_aggregate(metrics):
  sm = 0
  for v in metrics["aggr"]["SATD"]:
    sm += v 
  ratio = sm / len(metrics["aggr"]["SATD"])
  print("SATD ratio", ratio)
  sm = 0
  for v in metrics["aggr"]["NOT_SATD"]:
    sm += v 
  ratio = sm / len(metrics["aggr"]["NOT_SATD"])
  print("NOT_SATD ratio", ratio)

if __name__ == "__main__":

  global satd_any_time  
  global age_threshold
  global set_age_threshold
  global conservative_bugs
  global max_tangled

  set_age_threshold = True
  age_threshold = 2 * 365
  satd_any_time = False
  conservative_bugs  = True
  max_tangled = 5
  
  indexes = find_index()
  
  metrics = process(indexes)
  
  
  #calculate_aggregate(metrics)
  cliffs(metrics)
  #p, d, size = statistics(metrics["aggr"]["SATD"], metrics["aggr"]["NOT_SATD"])
    
  #print(indicator, p, d, size)
  #printLatex(indicator, p, d, size)
  #break

