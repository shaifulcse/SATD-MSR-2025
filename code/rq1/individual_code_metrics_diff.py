import re
import os
from util import utility
from util import graphs
import cliffsDeltaModule
from scipy import stats


SRC_PATH="../../data/cleaned/"

selected_features = ["SLOCStandard",
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
                     "Parameters",
                     "LocalVariables"
                     ]
indicators = [       "NewAdditions",
                     "DiffSizes",
                     "EditDistances",
                     "CriticalEditDistances",
                     "TangledWMoveandFileRename",
                     "Buggycommiit",
                     "PotentiallyBuggycommit",
                     "RiskyCommit",
                     "file"
]

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

def process(feature, indexes):

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
      satds = data[indexes["SATD"]]
      satds = satds.split("#")

      if satd_any_time:
        is_satd = is_SATD_any_time(satds)
      else:
        is_satd = is_SATD_beginning(satds) 
        if not is_satd: # beginning is not true, but later can be found, should be discarded
          if is_SATD_any_time(satds):
            continue      
      feature_values = data[indexes[feature]]
      feature_values = feature_values.split("#")
      if satd_any_time:
        value = getMean(feature_values)
        #print(feature_values, value)
      else:
        value = float(feature_values[len(feature_values)-1])  
      #print(file, data[len(data)-1], feature_values, value)
      
      if is_satd:
        metrics[file]["SATD"].append(value)
        metrics["aggr"]["SATD"].append(value)
      else:
        metrics[file]["NOT_SATD"].append(value) 
        metrics["aggr"]["NOT_SATD"].append(value)
    fr.close()
  return metrics     
    
def getMean(ls):
  sm = 0
  for v in ls:
    sm += float(v)
  return sm / len(ls)
 
def draw_graph(feature, satds, not_satds):  
  X = []
  Y = []
  x_satd, y_satd = utility.ecdf(satds)
  X.append(x_satd)
  Y.append(y_satd)
  x_not_satd, y_not_satd = utility.ecdf(not_satds)
  X.append(x_not_satd)
  Y.append(y_not_satd)

  configs = {}
  if feature == "SLOCStandard":
    feature = "Size"
  configs["x_label"] = feature
  configs["y_label"] = "CDF"
  configs["legends"] = ["SATD", "NOT_SATD"]
  #configs['marker'] = False
  #configs['xscale'] = True
  #configs["x_ticks"] = np.arange(20, 110, 10)
  graphs.draw_line_graph_multiple_with_x(X, Y, configs)


    
def statistics(x, y):
  d, size = cliffsDeltaModule.cliffsDelta(x, y)
  st = stats.mannwhitneyu(x, y)
  p_value = st[1]  
  return p_value, d, size

def calculate_individual(feature, metrics):
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

# def printLatexWithSign(feature, total, insignificant, cliffs):
#   if feature == 'SLOCStandard':
#     feature = 'Size'
#   print("{}&{:.2f}&{:.2f}&{:.2f}&{:.2f}&{:.2f}&{:.2f}&{:.2f}\\\\\n".format(feature, 
#                                               100*(insignificant/total),
#                                               100*(cliffs['+']/total),
#                                               100*(cliffs['-']/total),
#                                               100*(cliffs['negligible']/total),
#                                               100*(cliffs['small']/total),
#                                               100*(cliffs['medium']/total),
#                                               100*(cliffs['large']/total)))
  

def printLatexWithoutSign(feature, total, insignificant, cliffs):
  if feature == 'SLOCStandard':
    feature = 'Size'
  print("{}&{:.2f}&{:.2f}&{:.2f}&{:.2f}&{:.2f}\\\\\n".format(feature, 
                                              100*(insignificant/total),
                                              100*(cliffs['negligible']/total),
                                              100*(cliffs['small']/total),
                                              100*(cliffs['medium']/total),
                                              100*(cliffs['large']/total)))

  
  

if __name__ == "__main__":

  global satd_any_time  

  satd_any_time = False
  indexes = find_index()

  for feature in selected_features:
    #if feature != 'Readability':
    #  continue
    metrics = process(feature, indexes)
    #draw_graph(feature, metrics["aggr"]["SATD"], metrics["aggr"]["NOT_SATD"])
    p, d, size = statistics(metrics["aggr"]["SATD"], metrics["aggr"]["NOT_SATD"])
    #print(feature, p, d, size)
    total, insignificant, cliffs = calculate_individual(feature, metrics)
    #print(feature, insignificant, cliffs)
    printLatexWithoutSign(feature, total, insignificant, cliffs)
    #break