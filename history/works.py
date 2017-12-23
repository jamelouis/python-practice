import  re
import  csv
import  numpy as np
import  xml.etree.ElementTree as ET
import  operator
import  copy
from    matplotlib  import pyplot as plt
from    collections import OrderedDict


def data_preprocess_for_svn():
    with open('log_svn.csv', 'w', encoding='utf-8') as f:
        f.write('author,date,msg\n')
        tree = ET.parse('log_svn.xml')
        root = tree.getroot()

        for child in root:
            author = ''
            date = ''
            msg = ''
            for subchild in child:
                #print(subchild.tag, subchild.text)
                if subchild.tag == 'author':
                    author = subchild.text
                elif subchild.tag == 'date':
                    date = subchild.text
                elif subchild.tag == 'msg':
                    msg = subchild.text
                
            #print(author, date, msg)
            date_re = re.match(r'\d{4}-\d{2}-\d{2}', date)
            if msg:
                msg_re = re.match(r'.*】(.*)', msg)
            else:
                msg = None
            if msg_re and len(msg_re.group(1)) > 0:
                f.write(author+','+ ''.join(date_re.group(0).split('-'))+','+ msg_re.group(1)+'\n')
                
def data_preprocess_for_p4v():
    content = ''
    with open('log_p4v.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    with open('log_p4v.csv', 'w', encoding='utf-8') as f:
        f.write('author,date,msg\n')
        change_list = content.split('Change')
        for change in change_list:
            t = change.split('\n')
            if len(t)>1:
                m = re.search(r'(\d{4}/\d{2}/\d{2})', t[0])
                author = re.search(r' ([a-zA-Z0-9]+)@', t[0])
                msg = ''.join(t[1:]).strip()
                if m and author:
                    f.write(author.group(1)+','+ ''.join(m.group(0).split('/'))+','+ msg+'\n')
                    
def counter(rows, months, filters='month'):
    if filters == 'year':
        l = 4
    elif filters == 'month':
        l = 6
    else:
        l = 8
    
    data = OrderedDict()
    for month in months:
        try:
            data[int(month[:l])] = 0
        except:
            pass
        
    for row in rows:  
        try:
            t = int(row[1][:l])
            if t not in data:
                data[t] = 1
            else:
                data[t] += 1
        except:
            pass
    return data
    
def filter_data(rows, name, filters):
    namerows = [ row for row in rows if row[0]==name]
    otherrows = [row for row in rows if row[0] != name]
    months = [row[1] for row in rows]
    print(len(months))
    return counter(namerows, months, filters), counter(otherrows, months, filters)

def analysis(rows, name, top=5, length=1):
    namerows = [row for row in rows if row[0] == name]

    data = {}
    for row in namerows:
        msg = row[2]
        #print(msg)
        for i in range(len(msg)-length):
            if msg[i:i+length+1] not in data:
                data[msg[i:i+length+1]] = 1
            else:
                data[msg[i:i+length+1]] += 1
    data = sorted(data.items(), key=operator.itemgetter(1),reverse=True)[0:top]
    return data

def data_process(developer, filters):
    wq = OrderedDict()
    other = OrderedDict()
    rows = []
    with open('log_all.csv', 'r', encoding='utf-8') as csvfile:
        rows = csv.reader(csvfile)
        rows = [ row for row in rows]

        wq, other = filter_data(rows, developer, filters)
        #print(wq)
        #print(other)
        #print(analysis(rows,developer,10))
        #print(analysis(rows,developer,10,2))
        #print(analysis(rows,developer,5,3))
        #print(analysis(rows,developer,3,4))
        #print(analysis(rows,developer,2,5))
    return rows, wq, other

def data_visualization(rows, wq, other, developer): 
    tc = len(rows)
    yc = len([row for row in rows if row[0] == developer])
    print('total commits:', tc)
    print('your commits:', yc)

    fig = plt.figure()
    ax = fig.add_subplot(121)
    
    ax.bar(np.arange(len(wq.keys())), list(wq.values()))
    #ax.bar(np.arange(len(other.keys())), list(other.values()), bottom=list(wq.values()))
    ax.set_xticks(np.arange(len(wq.keys())))
    ax.set_xticklabels(list(wq.keys()),rotation='vertical')
    ax.set_xlabel('months')
    ax.set_ylabel('commits')
    
    ax2 = fig.add_subplot(122)
    ax2.pie([tc,yc],explode=(0.01,0.0), labels=('total commits', 'my commits'), autopct='%1.1f%%', shadow=True, startangle=90)
    ax2.axis('equal')

    plt.savefig('my_work_experience.pdf')
    plt.show()

def counter_topic(rows, keywords, value):
    data = OrderedDict()
    months = [row[1] for row in rows]
    for month in months:
        data[int(month)] = [0,0]

    for row in rows:
        dt = int(row[1])
        msg = row[2]
        for kw in keywords:
            if kw in msg:
                data[dt][0] = value
                data[dt][1] += 1
    return data
    
def data_visualization2(rows, wq, other, developer):

    w1 = [ row for row in rows if row[0] == developer ]
    keywords_list = [
        ['Shadowmap','阴影', 'Shadow'],
        ['decal','贴花'],
        ['light', '点光', '点光源', '方向光','聚光'],
        ['postprocess', 'AA', 'HBAO', 'Bokeh', 'DOF', '后期','lensflare'],
        ['bug','修复']
        ]
    colors = ['red','green','blue', 'brown', 'black']
    datas = []
    for i, keywords in enumerate(keywords_list):
        datas.append(counter_topic(w1,keywords,i))
    
    
            
    for i, data in enumerate(datas):
        yvalues = [ val[0] for val in data.values()]
        yvalues = list(reversed(yvalues))
        ss=list(reversed([val[1] for val in data.values()]))
        plt.scatter(yvalues , np.arange(len(data.keys())),s=ss , c=colors[i])

    plt.yticks(np.arange(6))
    plt.yticks([],[])
    plt.xticks(np.arange(len(keywords_list)),[ keywords[0] for keywords in keywords_list])
    plt.ylabel('commit date')
    plt.xlabel('topics')
    #plt.legend([ keywords[0] for keywords in keywords_list])
    plt.title('my working experience')
    #plt.savefig('my_working_experience.jpg')
    plt.show()
    
if __name__ == '__main__':
    #data_preprocess_for_svn()
    #data_preprocess_for_p4v()
    developer = 'zhangsan'
    rows, wq, other = data_process(developer,'month')
    data_visualization(rows, wq, other, developer)
    #rows, wq, other = data_process(developer,'day')
    #data_visualization2(rows, wq, other, developer)
    
