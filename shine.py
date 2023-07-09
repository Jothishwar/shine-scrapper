import requests,json,time,re
from random import randint
from bs4 import BeautifulSoup
from datetime import datetime,date,timedelta
import smtplib 
from email.message import EmailMessage
import psycopg2
from psycopg2.extras import execute_values

USERNAME = "talentaijobsuser"
PASSWORD = "jkrowlingtalentai12?"
DB_NAME = "talentai_jobs_db"
URL = "talentai-jobs-db.c95l3n9ofmp6.ap-south-1.rds.amazonaws.com"
PORT = 5432

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

def send_email(subject,body):
    # Set up SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'jothishwarvvr@gmail.com'  # Your email address
    sender_password = 'nowfywvjxxwwfyux'  # Your email password
    recipient_email = 'jothishwarvvr@gmail.com'  # Recipient's email address

    # Create the email message
    message = EmailMessage()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.set_content(body)
    
    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        print('Email sent successfully!')
    except smtplib.SMTPException as e:
        print('Error sending email:', str(e))

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
def format_sal(sal):
    if sal==None:
        return None
    fsal=[]
    if re.findall(r"\d+k", sal):
        matches = re.findall(r"\d+(?:\.\d+)?", sal)
        if len(matches)==1:
            return str((int(matches[0])*12)/100)+' LPA'

    matches = re.findall(r"\d+(?:\.\d+)?", sal.replace(',',''))
    if len(matches)>0:
        if len(matches)==1:
            try:
                if int(matches[0])/1000>=1 and str(matches[0]).count('0')>=3:
                    return str((int(matches[0])*12)/100000)+' LPA'
                else:
                    if str(matches[0]).count('0')>=4 and int(matches[0])/100000>=1:
                        return str(int(matches[0])/100000)+' LPA'
                    return str(int(matches[0]))+' LPA'
            except:
                if float(matches[0])/1000>=1 and str(matches[0]).count('0')>=3:
                    return str((float(matches[0])/1000)*12)+' LPA'
                else:
                    if str(matches[0]).count('0')>=4 and float(matches[0])/100000>=1:
                        return str(float(matches[0])/100000)+' LPA'
                    return str(float(matches[0]))+' LPA'
        if len(matches) >= 2:
            try:
                if int(matches[0])/100000>=1 and str(matches[0]).count('0')>=4:
                        return str((int(matches[0]))/100000)+' - '+str((int(matches[1]))/100000)+' LPA'
                if int(matches[0])/1000>=1 and str(matches[0]).count('0')>=3:
                        return str((int(matches[0])*12)/100000)+' - '+str((int(matches[1])*12)/100000)+' LPA'
                if(matches[0]!=matches[1]):
                    fsal.append(matches[0])
                    fsal.append(matches[1])
            except:
                if float(matches[0])/100000>=1 and str(matches[0]).count('0')>=4:
                        return str((float(matches[0]))/100000)+' - '+str((float(matches[1]))/100000)+' LPA'
                if float(matches[0])/1000>=1 and str(matches[0]).count('0')>=3:
                        return str((float(matches[0])*12)/100000)+' - '+str((float(matches[1])*12)/100000)+' LPA'
                if(matches[0]!=matches[1]):
                    fsal.append(matches[0])
                    fsal.append(matches[1])
    else:
        return None
    return str(fsal[0])+" - "+str(fsal[1])+' LPA'

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
    #----------------------Connecting to Postgresql Database-----------------------------------------------
    conn = psycopg2.connect(database=DB_NAME, password=PASSWORD, user=USERNAME, host=URL, port=PORT)
    cur = conn.cursor()
    #-----------------Fetching existing job links to remove duplicates-------------------------------------
    try:
        cur.execute("select url from jobs where url like '%timesjobs%' and category='"+str(c)+"'")
        rec=cur.fetchall()
        existing_links=list([j[0] for j in rec])
    except:
        existing_links=[]

    for page in range(1,category_json['num_pages']+1):
        print('page - ',page)
        #---------------Looping through the pages to scrape all the jobs in that category--------------------------
        time.sleep(randint(2,5))
        cat_api_url=f"https://www.shine.com/api/v2/search/simple/?q={cat}&page={page}&sort=1"
        resp = requests.request("GET", cat_api_url, headers=headers, data=payload)
        decoded_data=resp.text.encode().decode('utf-8-sig')
        job_json=json.loads(decoded_data)
        try:
            n=len(job_json['results'])
            fetched+=n
            #-----------------looping through all the jobs in each page---------------------------------
            for job in range(n):
                print('j-',job)
                da=job_json['results'][job]['jPDate'][:10]
                link="https://www.shine.com/jobs/"+job_json['results'][job]['jSlug']
                if datetime.strptime(da,'%Y-%m-%d').date() < date.today()-timedelta(days=60):
                    continue
                if link in existing_links:
                    continue
                titl=job_json['results'][job]['jJT']
                cmp=job_json['results'][job]['jCName']
                desc=format_desc(job_json['results'][job]['jJD'])
                loc="/".join(job_json['results'][job]['jLoc'])
                sk=job_json['results'][job]['jKwd']
                exp=job_json['results'][job]['jExp']
                minmax=format_exp(exp)
                qua=get_qualification(desc)

                #--------------salary and employment type details are extracted using bs4 module--------------------
                job_resp=requests.get(link)
                job_soup=BeautifulSoup(job_resp.content,'html.parser')
                sal=get_sal(job_soup,desc)
                fsal=format_sal(str(sal))
                try:
                    job_html=job_soup.select_one('script[type="application/ld+json"]')
                    job_json1=json.loads(job_html.text.strip())
                except Exception as e:
                    print('Failed to fetch json for emp type')
                    print(link,' - ',e)
                ty=job_json1['employmentType']
                # print((titl,cat,loc,da,link,desc,sk,ty,cmp,minmax[0],minmax[1],qua,None,sal))
                job_list.append((titl,cat,loc,da,link,desc,sk,ty,cmp,minmax[0],minmax[1],qua,None,sal))
        except Exception as e:
            print(e)
            print('\nfailed to fetch page')
            print('category - ',cat,'\t page number - ',page,'\n')
            continue
    print('jobs fetched using api - ',fetched)
    if len(job_list)>0:
        execute_values(cur,
            '''INSERT INTO jobs(title,category,location,date_posted,url,description,skills,job_type,company_name,minimum_experience,maximum_experience,qualifications,company_logo_url,salary)
            VALUES %s''',
            job_list)
        conn.commit()
        conn.close()
        print(cat,' Database updated - ',len(job_list))
        send_email('Shine Status',f'Shine category {cat} completed ssuccessfully \n Database updated - '+str(len(job_list)))
print('Overall jobs fetched - ',total)
send_email('Timesjobs Status','Timesjobs scraping completed successfully')
