import re
import os
from util import utility
from util import graphs
import cliffsDeltaModule
from scipy import stats


SRC_PATH="../../data/cleaned/"

indicators = [      
                     "Revisions", 
                     "DiffSizes",
                     "NewAdditions",
                     "EditDistances",
                     "CriticalEditDistances"]

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

def process(indicator, indexes):

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

      diffs = data[indexes["DiffSizes"]]
      diffs = diffs.split("#")

      adds = data[indexes["NewAdditions"]]
      adds = adds.split("#")

      edits = data[indexes["EditDistances"]]
      edits = edits.split("#")

      cedits = data[indexes["CriticalEditDistances"]]
      cedits = cedits.split("#")

      change_dates = data[indexes["ChangeAtMethodAge"]]
      change_dates = change_dates.split("#") 

      if satd_any_time:
        is_satd = is_SATD_any_time(satds)
      else:
        is_satd = is_SATD_beginning(satds) 
        if not is_satd: # beginning is not true, but later can be found, should be discarded
          if is_SATD_any_time(satds):
            continue      
      if indicator == "Revisions":
        value = getValue(indicator, change_dates, diffs)
      if indicator == 'DiffSizes':
        value = getValue(indicator, change_dates, diffs)
      if indicator == 'NewAdditions':
        value = getValue(indicator, change_dates, adds)    
      if indicator == 'EditDistances':
        value = getValue(indicator, change_dates, edits)
      if indicator == 'CriticalEditDistances':
        value = getValue(indicator, change_dates, cedits)    
              
      if is_satd:
        metrics[file]["SATD"].append(value)
        metrics["aggr"]["SATD"].append(value)
      else:
        metrics[file]["NOT_SATD"].append(value) 
        metrics["aggr"]["NOT_SATD"].append(value)

      #print (file, data[len(data)-1], change_dates, diffs, adds, edits, cedits, value)  
    fr.close()

  return metrics     
    
def getValue(indicator, change_dates, values):
  
  count = 0
  for i in range (1, len(values)):
    if set_age_threshold and int(change_dates[i]) > age_threshold:
      return count 
    if indicator == "Revisions":
      if int(values[i]) > 0:
        count += 1
    else:
        count += int(values[i])    
  return count            
 
def draw_graph(indicator, satds, not_satds):  
  X = []
  Y = []
  x_satd, y_satd = utility.ecdf(satds)
  X.append(x_satd)
  Y.append(y_satd)
  x_not_satd, y_not_satd = utility.ecdf(not_satds)
  X.append(x_not_satd)
  Y.append(y_not_satd)

  configs = {}
 
  configs["x_label"] = indicator
  configs["y_label"] = "CDF"
  configs["legends"] = ["SATD", "NOT_SATD"]
  #configs['marker'] = False
  configs['xscale'] = True
  #configs["x_ticks"] = np.arange(20, 110, 10)
  graphs.draw_line_graph_multiple_with_x(X, Y, configs)


    
def statistics(project, x, y):
  #if len(x) == 0:
  #  print(project)
  #print(len(x), len(y))
  d, size = cliffsDeltaModule.cliffsDelta(x, y)

  st = stats.mannwhitneyu(x, y)
  p_value = st[1]  
  return p_value, d, size

def calculate_individual(indicator, metrics):
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
    p, d, size = statistics(project, metrics[project]["SATD"], metrics[project]["NOT_SATD"])
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
  
def printLatexWithoutSign(feature, total, insignificant, cliffs):
 
  print("{}&{:.2f}&{:.2f}&{:.2f}&{:.2f}&{:.2f}\\\\\n".format(feature, 
                                              100*(insignificant/total),
                                              100*(cliffs['negligible']/total),
                                              100*(cliffs['small']/total),
                                              100*(cliffs['medium']/total),
                                              100*(cliffs['large']/total)))

if __name__ == "__main__":

  global satd_any_time  
  global age_threshold
  global set_age_threshold
  
  set_age_threshold = True
  age_threshold = 2 * 365
  satd_any_time = False
  indexes = find_index()

  for indicator in indicators:
    #if indicator != 'CriticalEditDistances':
    #  continue
    metrics = process(indicator, indexes)
    #draw_graph(indicator, metrics["aggr"]["SATD"], metrics["aggr"]["NOT_SATD"])
    #p, d, size = statistics(metrics["aggr"]["SATD"], metrics["aggr"]["NOT_SATD"])
    
    total, insignificant, cliffs = calculate_individual(indicator, metrics)
    #print(indicator, p, d, size)
    printLatexWithoutSign(indicator, total, insignificant, cliffs)
    #break