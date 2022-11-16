import requests
import sys
import os
import datetime
from lxml import html
# 创建 session 对象。这个对象会保存所有的登录会话请求。
session_requests = requests.session()
# 提取在登录时所使用的 csrf 标记
main_url = "http://154.233.150.87:8089/SJFF/"
login_url = "http://154.233.150.87:8089/SJFF/j_spring_security_check"
username= '853000'
password = '123456'
firstpage = 'http://154.233.150.87:8089/SJFF/noticesList.do'
yxrq=sys.argv[1]
#print(yxrq)
def finddownpage(tree,yxrq):
    bucket_elems = tree.xpath('//tr')
    #print(bucket_elems)

    for row in bucket_elems:
        rows=row.xpath('td/text()')
        td1=row.xpath('td[1]/text()')
        tdtemp=''
        if len(td1) > 0:
           tdtemp=td1[0].strip()
        #print(tdtemp)
        if '标准化文档更新' == tdtemp or '标准化文档更新1' == tdtemp:
            #print(td1)
            td2=row.xpath('td[2]/text()')[0]
            date1=td2.strip()
            date2=datetime.datetime.strptime(date1,'%Y-%m-%d %H:%M:%S')
            date3=datetime.datetime.strftime(date2,'%Y%m%d')
            #print(date3)
            if date3 < yxrq:
                td3=row.xpath('td/input/@onclick')[0]
                td3str=str(td3)
                #print(td3str)
                #print(td3str.rfind("'"))
                detail=td3str[td3str.index("'")+1:td3str.rfind("'")]
                #print(detail)
                return detail
        else:
            pass
    return ''
def nextpage(session_requests,pageurl,pagenum):
    payload = {
      "pageIndex": pagenum
    }
    # 执行登录
    result = session_requests.post(
      pageurl,
      data = payload
    )
    tree = html.fromstring(result.content)
    return tree

        

def downloadFile(url,filename,session_requests):
    req=session_requests.get(url)
    if req.status_code != 200 :
        print('下载异常')
        return
    try :
        with open(os.getcwd()+'/file/'+filename,'wb') as f:
            #print(req.content)
            f.write(req.content)
            print('下载成功')
    except Exception as e:
        print(e)

host=main_url[0:len(main_url)-1]
host=host[0:host.rfind("/")]
result = session_requests.get(login_url)
#urlcook=result.cookies
#tree = html.fromstring(result.text)

#authenticity_token = tree.xpath("//input[@name='authenticity_token']/@value")[0]
#print(authenticity_token)
#inputs = tree.xpath("//input")
#print(inputs)
payload = {
  "username": "853000",
  "password": "123456"
}
# 执行登录
result = session_requests.post(
  login_url,
  data = payload,
  headers = dict(referer=login_url)
)
#print(result.status_code)
#print(result.cookies)
#print(result.content)

# 已经登录成功了，然后从 bitbucket dashboard 页面上爬取内容。
result = session_requests.get(
  firstpage,
  headers = dict(referer=login_url))
#print(result.content)
# 测试爬取的内容
tree = html.fromstring(result.content)
downpage=finddownpage(tree,yxrq)
if '' == downpage:
    for x in range(2,50):
        pagetree=nextpage(session_requests,firstpage,x)
        downpage=finddownpage(pagetree,yxrq)
        if '' != downpage:
            break
#print('downlaodurl'+downpage)
if '' != downpage:
    result = session_requests.get(main_url+downpage)
    tree = html.fromstring(result.content)
            #print(html)
            #downpage = tree.xpath('//tr')
            #print(downpage)
            #for row2 in downpage:
                #td12=row2.xpath('th[1]/text()')
                #td22=row2.xpath('td/text()')
                #print(td22)
                #print(td12)
                #if '附件' in str(td12):
                    #print(td12)
                    #print(td22)
                    #td22=row2.xpath('//a')
                    #print('do'+str(td22))
    downpage = tree.xpath("//a")
    for link in downpage:
        url=link.xpath("@href")[0]
        name=link.xpath("text()")[0]
        #print (str(url))
        #print(str(name))
        #print(host)
        downloadFile(host+url,name,session_requests)
        break

                

