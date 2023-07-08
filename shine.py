import requests,json,time,re
from random import randint
from bs4 import BeautifulSoup
from datetime import datetime,date,timedelta
import smtplib 
from email.message import EmailMessage
import psycopg2
from psycopg2.extras import execute_values

payload = {}
headers = {
  'authority': 'www.shine.com',
  'accept': 'application/json',
  'accept-language': 'en-US,en;q=0.5',
  'cookie': '_ds_=True; sessionid=pvozirv0gl70b6i5uqz70zis8febkmiz; csrftoken=ALR7P9uYhIWkzhoD95REUCIKQdPjBltkGdGPyUPeL0VNzrljVrIL9DH7ZuGGN2gj; sessionid=pvozirv0gl70b6i5uqz70zis8febkmiz',
  'referer': 'https://www.shine.com/browsejobs/industry?letter=A',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'sec-gpc': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

category_names=[]
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    category_api_url = f"https://www.shine.com/api/v2/browse-jobs/industry/word/?q={letter}"
    response = requests.request("GET", category_api_url, headers=headers, data=payload)
    resp_json=json.loads(response.text)
    for cat in range(len(resp_json['data'])):
        category_names.append(resp_json['data'][cat][0])
    # print(resp_json['data'][0][0])
print('total categories - ',len(category_names))
total=0

def get_qualification(desc):
    qualification = re.search(r'\b(Education|QUALIFICATION)\s*[:\- ]*\s*(\w[^,\n]*)', desc)
    if qualification:
        return qualification.group(2)
    else:
        q=re.search(r'\b(qualification|degree|diploma|B\.Tech|BE|B\.E)\s*[:\- ]*\s*(\w[^,\n]*)', desc, flags=re.IGNORECASE)
        if q:
            return q.group(2)
        return None
def format_desc(desc):
    desc=desc.replace('<b>','').replace('</b>','').replace('<p>','').replace('</p>','').replace('<br />','').replace('<strong>','').replace('</strong>','').replace('\r','').replace('<li>','').replace('</li>','').replace('<br>','').replace('<span>','').replace('</span>','').replace('<ul>','').replace('</ul>','').replace('&nbsp;',' ').replace('<p class="x_xmsonormal">','').replace('<h2 class="jdlb-t1">','').replace('</h2>','')
    desc=re.sub(r'\n\s?(?=:)','',desc)
    desc=desc.strip()
    return desc
def format_exp(exp):
    matches=re.findall(r"\d+",exp)
    minimax=[]
    if len(matches)>0:
        if len(matches)==1:
            minimax.append(int(matches[0]))
            minimax.append(None)
        if len(matches) >= 2:
            if(int(matches[0])!=int(matches[1])):
                minimax.append(int(matches[0]))
                minimax.append(int(matches[1]))
            else:
                minimax.append(int(matches[0]))
                minimax.append(None)
    else:
        minimax.append(None)
        minimax.append(None)
    return minimax
def get_sal(job_soup,desc):
    try:
        sal=job_soup.select_one('#__next > div.main > div > div > div.leftWrapper.jd_page.mt-15 > div.JobDetailWidget_jobDetail_blue__JDzC6 > div.row > div > div.JobDetailWidget_jobCard_lists__3HvvF > span').text
        return sal
    except Exception as e:
        salary = re.search(r'SALARY\s*:\s*(.*)', desc,flags=re.IGNORECASE)
        if salary:
            return salary.group(1).strip()
        else:
            return None

for cat in category_names:
    fetched=0
    job_list=[]
    time.sleep(randint(10,15))
    api_url = f"https://www.shine.com/api/v2/search/simple/?q={cat}&page=1&sort=1"
    cresp = requests.request("GET", api_url, headers=headers, data=payload)
    category_json=json.loads(cresp.text)
    c=category_json['count']
    print('available jobs - ',c)
    total+=c
    for page in range(1,category_json['num_pages']+1):
        time.sleep(randint(2,5))
        cat_api_url=f"https://www.shine.com/api/v2/search/simple/?q={cat}&page={page}&sort=1"
        resp = requests.request("GET", cat_api_url, headers=headers, data=payload)
        decoded_data=resp.text.encode().decode('utf-8-sig')
        job_json=json.loads(decoded_data)
        try:
            n=len(job_json['results'])
            fetched+=n
            for job in range(n):
                titl=job_json['results'][job]['jJT']
                cmp=job_json['results'][job]['jCName']
                desc=format_desc(job_json['results'][job]['jJD'])
                loc="/".join(job_json['results'][job]['jLoc'])
                da=job_json['results'][job]['jPDate'][:10]
                sk=job_json['results'][job]['jKwd']
                exp=job_json['results'][job]['jExp']
                minmax=format_exp(exp)
                link="https://www.shine.com/jobs/"+job_json['results'][job]['jSlug']
                qua=get_qualification(desc)

                #salary and employment type details are extracted using bs4 module
                job_resp=requests.get(link)
                job_soup=BeautifulSoup(job_resp.content,'html.parser')
                sal=get_sal(job_soup,desc)
                try:
                    job_html=job_soup.select_one('script[type="application/ld+json"]')
                    job_json1=json.loads(job_html.text.strip())
                except Exception as e:
                    print('Failed to fetch json for emp type')
                    print(link,' - ',e)
                ty=job_json1['employmentType']
                print((titl,cat,loc,da,link,desc,sk,ty,cmp,minmax[0],minmax[1],qua,None,sal))
        except Exception as e:
            print(e)
            print('\nfailed to fetch page')
            print('category - ',cat,'\t page number - ',page,'\n')
            continue
    print('jobs fetched using api - ',fetched)
print('Overall jobs fetched - ',total)
print('Success !!!')