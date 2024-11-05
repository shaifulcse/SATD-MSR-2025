import re
import os
from util import utility
from util import graphs
import cliffsDeltaModule
from scipy import stats
from scipy.stats.stats import kendalltau

SRC_PATH="../../data/cleaned/"


def find_index():
  indexes = {}
  fr = open(SRC_PATH + "checkstyle" + ".csv")
  line = fr.readline() 
  line = line.strip()
  data = line.split("\t")
  for i in range(len(data)):
    indexes[data[i]] = i
  return indexes


def process(indexes):

  metrics = {}
  ## aggregated results
  metrics["aggr"] = {}
  metrics["aggr"]["SATD_COUNT"] = 0
  metrics["aggr"]["RESOLVED"] = 0

  for file in os.listdir(SRC_PATH):
    metrics[file] = {}
    metrics[file]["SATD_COUNT"] = 0
    metrics[file]["RESOLVED"] = 0
    
    fr = open(SRC_PATH + file)
    fr.readline()
    for line in fr:
      line = line.strip()
      data = line.split("\t")
      age = int(data[0])

      satds = data[indexes["SATD"]]
      satds = satds.split("#")
     
      change_dates = data[indexes["ChangeAtMethodAge"]]
      change_dates = change_dates.split("#") 
      found, resolved = percent_resolution(satds, change_dates, age)
      metrics[file]["SATD_COUNT"] += found 
      metrics[file]["RESOLVED"] += resolved
      metrics['aggr']["SATD_COUNT"] += found 
      metrics['aggr']["RESOLVED"] += resolved
      #if found >2 :
      #  print (file, data[len(data)-1], age, change_dates, satds, found, resolved)  
    fr.close()

  return metrics     
    
def percent_resolution(satds, change_dates, age):
  index = 0
  count_satd = 0
  count_resolved = 0
  while index < len(satds):
    while ((index < len(satds) and int(satds[index]) != 1)):
      index += 1
    #index == len means no one was found
    if index < len(satds): # 1 was found
      save = index
      index += 1 ## search from next
      count_satd += 1 
      while ((index < len(satds) and int(satds[index]) != 0)):
        index += 1 
    #index == len means no 0 was found 
      if index < len(satds):
        count_resolved += 1 
        index += 1
      elif set_age_threshold and (age - int(change_dates[save])) < age_threshold: 
        count_satd -= 1
  return count_satd, count_resolved
  
def print_results(metrics):
  found = metrics['aggr']['SATD_COUNT']
  resolved = metrics['aggr']['RESOLVED']
  print("Aggr", found, resolved, (100* (found -resolved)) / found)
  
  satds = []
  percents = []
  for project in metrics:
    if project == 'aggr':
      continue
    found = metrics[project]['SATD_COUNT']
    resolved = metrics[project]['RESOLVED']
    percent = (100 * (found -resolved)) / found
    #print(project, found, resolved, (100* (found -resolved)) / found)
    satds.append(found)
    percents.append(percent)
  cr = kendalltau(satds, percents)
    #print (cr, cr[0])
  #print(satds, percents)  
  print(cr[0], cr[1])
  print(sorted(percents))
  draw_graph(percents)
    
def draw_graph(percents):
  X = []
  Y = []

  
  x, y = utility.ecdf(percents)
  
  X.append(x)
  Y.append(y)

 
  configs = {}
 
  configs["x_label"] = "Unresolved SATD (%)"
  configs["y_label"] = "CDF"
  #configs['marker'] = False
  #configs['xscale'] = True
  #configs["x_ticks"] = np.arange(20, 110, 10)
  graphs.draw_line_graph_multiple_with_x(X, Y, configs)


    
if __name__ == "__main__":

  global age_threshold
  global set_age_threshold
  set_age_threshold = True
  age_threshold = 2 * 365
  indexes = find_index()
  
  metrics = process(indexes)
  print_results(metrics)
