#encoding=utf-8
import requests
import warnings
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')

def wf(filename, data):
	fp = open(filename, "ab")
	fp.write(data)
	fp.close()

def get_string(data, start, end):
	if data.upper().find(start.upper())== -1:
		return ""
	temp = data[data.upper().find(start.upper())+len(start):]
	if temp.upper().find(end.upper())== -1:
		return ""
	value = temp[:temp.upper().find(end.upper())]
	return value

if __name__ == "__main__":
    # ip_scope_list = []
    res = requests.get("http://ip.bczs.net/country/HK")
    soup = BeautifulSoup(res.content)
    for i in soup.body.div.children:
        if str(i).find('id="result"') > -1:
            div_result = str(i)
    soup2 = BeautifulSoup(div_result)
    for i in soup2.div.table.tbody:
        ip_scope = get_string(str(i),'中国香港IP地址段:','">').split('-')
        if len(ip_scope) == 2:
            wf("hk_ip.txt", "%-15s    %-15s\n" % (ip_scope[0], ip_scope[1]))
            # ip_scope_list.append(ip_scope)
    # print(ip_scope_list)