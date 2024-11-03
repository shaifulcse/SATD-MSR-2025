import re
import os

SRC_PATH="../../data/cleaned/"
sorted_projects = []

def extractor():
  projects = {}
  fr = open("projects.csv")
  line = fr.readline()
  for line in fr:
    line = line.strip()
    data = line.split(",")
    project = data[0]
    sorted_projects.append(project)
    methods = int(data[1])
    contributors = int(data[2])
    stars = int(data[3])
    snapshot = data[4] 
    
    projects [project] = {}
    projects [project]['methods'] = methods
    projects [project]['cont'] = contributors
    projects [project]['stars'] = stars
    projects [project]['snap'] = snapshot
  fr.close()
  return projects

def parse(projects, indexes):
  total_methods = 0
  total_satd = 0

  for file in sorted_projects:
    fr = open(SRC_PATH + file+".csv")
    fr.readline()
    lines = fr.readlines()
    #if projects[file[:-4]]['methods'] != len(lines):
    #  print (file, projects[file[:-4]]['methods'], len(lines))
    num_satd = count_satd(file, lines, indexes)
    total_satd += num_satd
    total_methods += len(lines)
    #print(file, len(lines), num_satd, num_satd / len(lines))
    print("{}&{}&{} ({:.2f})&{}&{}&\\texttt{{{}}}\\\\".format(file, projects[file]['methods'], num_satd, 100*(num_satd / len(lines)),
                                    projects[file]['cont'], projects[file]['stars'], projects[file]['snap']  ))
    #hadoop & 70,081 & 592 & 14,500  & \texttt{4c5cd7} \\
  print(total_methods, total_satd, 100 *(total_satd / total_methods))

def count_satd(project, lines, indexes):
  count = 0
  for line in lines:
    is_satd = False
    line = line.strip()
    data = line.split("\t")
    satds = data[indexes["SATD"]]
    satds = satds.split("#")
    file = data[len(data)-1]
    for i in satds:
      if int(i) == 1:
        is_satd = True
        break 
    if is_satd:
      count += 1    
  return count    
    #print(project, file, is_satd, count)

   

def find_index():
  indexes = {}
  fr = open(SRC_PATH + "checkstyle" + ".csv")
  line = fr.readline()  # headerfeature_index
  line = line.strip()
  data = line.split("\t")
  for i in range(len(data)):
    indexes[data[i]] = i
  return indexes

if __name__ == "__main__":
  projects = extractor()
  indexes = find_index()
  parse(projects, indexes)
