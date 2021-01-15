import csv

def instancia_csv(FileName, verbose = True):
  " Carrega uma instância do problema de formato CSV."
  if verbose:
   print("Carregando Arquivo CSV " + FileName)

  aux    = []
  Matrix = []

  with open(FileName, newline='') as f:
    reader = csv.reader(f)
    i = 0
    for row in reader:
      if i == 0 :
        if verbose:
          print(row)
      else:
        if row[0][0] != "#":
          aux.append(row) 
        else:
            print(row[0])
      i += 1
    for m in aux:
      aux2 = []
      for j in m:
        aux2.append(int(j))
      Matrix.append(aux2)

  return Matrix
