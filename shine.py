import requests,json,time
from random import randint

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
for cat in category_names:
    fetched=0
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
        job_json=json.loads(resp.text)
        n=len(job_json['results'])
        fetched+=n
    print('jobs fetched using api - ',fetched)
print('Overall jobs fetched - ',total)
print('Success !!!')