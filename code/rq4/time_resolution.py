import re
import os
from util import utility
from util import graphs
from scipy import stats
from numpy import median

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
  metrics["aggr"] = []

  for file in os.listdir(SRC_PATH):
    metrics[file] = []
    
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
      times = resolution_time(satds, change_dates, age)
      if len(times) > 0:
        metrics['aggr'].extend(times)
        metrics[file].extend(times)
        #if len(times) > 2 :
        #  print (file, data[len(data)-1], age, change_dates, satds, times)  
    fr.close()

  return metrics     
    
def resolution_time(satds, change_dates, age):
  index = 0
  count_satd = 0
  count_resolved = 0
  times = []
  while index < len(satds):
    while ((index < len(satds) and int(satds[index]) != 1)):
      index += 1
    #index == len means no one was found
    if index < len(satds): # 1 was found
      save = index
      st = int(change_dates[index])
      index += 1 ## search from next
      count_satd += 1 
      while ((index < len(satds) and int(satds[index]) != 0)):
        index += 1 
    #index == len means no 0 was found 
      if index < len(satds):
        count_resolved += 1 
        end = int(change_dates[index])
        times.append(end - st)
        index += 1
      elif set_age_threshold and (age - int(change_dates[save])) < age_threshold: 
        count_satd -= 1
  return times
  
    
def draw_graph(times):
  X = []
  Y = []
  x, y = utility.ecdf(times)  
  X.append(x)
  Y.append(y)

  configs = {}
  configs['xscale'] = True
  configs["x_label"] = "SATD Removal Time (Days)"
  configs["y_label"] = "CDF"
  graphs.draw_line_graph_multiple_with_x(X, Y, configs)

    
if __name__ == "__main__":

  global age_threshold
  global set_age_threshold
  set_age_threshold = True
  age_threshold = 2 * 365
  indexes = find_index()
  
  metrics = process(indexes)
  #draw_graph(metrics['aggr'])

  avg_times = []
  med_times = []
  for project in metrics:
    avg = sum(metrics[project])/len(metrics[project])
    avg_times.append(avg)
    med = median(metrics[project])
    med_times.append(med)
  draw_graph(med_times)    


  #satds = [1,1,0,0,1,0,1]
  #change_dates = [0, 30, 60, 60, 70, 190, 200]
  #age = 7000
  #print(resolution_time(satds, change_dates, age))