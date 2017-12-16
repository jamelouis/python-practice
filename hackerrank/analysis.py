import csv
from matplotlib import pyplot as plt
from collections import defaultdict
from collections import OrderedDict
import os

def readcsv(file_name):
    dt = {} 
    with open(file_name,'r') as csvfile:
        data = csv.DictReader(csvfile)
        for item in data:
            if item['difficulty'] in dt:
                dt[item['difficulty']] += 1
            else:
                dt[item['difficulty']] = 1

    odt = OrderedDict()
    try:
        odt['Easy'] = dt['Easy']
        odt['Medium'] = dt['Medium']
        odt['Hard'] = dt['Hard']
        if 'Advanced' not in dt.keys():
            odt['Advanced'] = 0
        else:
            odt['Advanced'] = dt['Advanced']
    except:
        pass
    return odt

def plotData(data, filename):
    colors = [ '#ed002f', '#ff5c00', '#00a287', '#48dd00']
    plt.clf()
    plt.axis('equal')
    plt.subplot(1,2,1)
    plt.bar(data.keys(),data.values(),color=colors)
    for a,b in zip(data.keys(),data.values()):
        plt.text(a,b+0.1,b,va='bottom',ha='center')
    plt.subplot(1,2,2)
    plt.pie(data.values(),labels=data.keys(),autopct='%1.1f%%', shadow=True, colors=colors)
    plt.savefig(filename)

    
def test_csv():
    data = readcsv('fundamentals.csv')
    plotData(data, 'fundamentals.png')
    print(data)

def main():
    files = [ f for f in os.listdir() if os.path.isfile(f) and f[-3:] == 'csv']
    print(files)
    datas = {'Easy':0, 'Medium': 0, 'Hard': 0, 'Advanced':0} 
    for f in files:
        data = readcsv(f)
        for key in data.keys():
            datas[key] += data[key]
        plotData(data, f[0:-3] + 'png')
    plotData(datas,'mathematic.png')

if __name__ == '__main__':
    #test_csv()
    main()
