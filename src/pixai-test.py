import json
import time
from io import BytesIO

import requests
from PIL import Image


def run_query(uri, query, parameters, statusCode, headers):
    request = requests.post(uri, json={
        'query': query,
        'variables': {
            'parameters': parameters
        }
    },
                            headers=headers)
    response = json.loads(request.text)
    if request.status_code == statusCode:
        if 'errors' in response:
            print('message:%s' % response['errors'][0]['message'])
            print('loc:%s' % response['errors'][0]['locations'])
            if 'path' in response['errors'][0]:
                print('path:%s' % response['errors'][0]['path'])
            print('extension code:%s' % response['errors'][0]['extensions']['code'])
            if 'data' in response:
                print('returned data:%s' % response['data'])
        print(response)
        return request.json()
    else:
        print(request)
        # print(response)
        print('message:%s' % response['errors'][0]['message'])
        print('loc:%s' % response['errors'][0]['locations'])
        if 'path' in response['errors'][0]:
            print('path:%s' % response['errors'][0]['path'])
        print('extension code:%s' % response['errors'][0]['extensions']['code'])
        if 'data' in response:
            print('returned data:%s' % response['data'])
        raise Exception(f"Unexpected status code returned: {request.status_code}")


url = 'https://api.pixai.art/graphql'

###################################### remember to fill in your api key! ######################################

myheaders = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '
}
###################################### remember to fill in your api key! ######################################

# Define the GraphQL query
myquery = """
mutation createGenerationTask($parameters: JSONObject!) {
  createGenerationTask(parameters: $parameters) {
    id
  }
}
"""

myparameters = {
    "prompts":
        """
        1girl
        """,
    # prompts
    "enableTile": False,
    # controlnet
    "negativePrompts": '(worst quality, low quality, large head, extra digits:1.4), easynegative,',
    # neg prompts
    "samplingSteps": 12,
    # sampling steps
    "samplingMethod": "Euler a",
    # sampling steps
    "cfgScale": 5,
    # cfg scale
    "modelId": "1648918115270508582",
    # generate model version id
    "width": 512,
    # image width
    "height": 768,
    # image hight
    "batchSize": 4,
    # batch size
    "lora": {
        "LoraId1": "1632808149867611809", "LoraId2": "1664117894070404490"
    }
    # still unknown
}


# Define the data for the request
data = {
    'query': myquery,
    'variables': {
        'parameters': myparameters
    }
}

getpic_query = """
query getMediaById($id: String!) {
  media(id: $id) {
    urls {
      variant
      url
    }
  }
}
"""

result = run_query(url, myquery, myparameters, 200, myheaders)
# try:
picid = result['data']['createGenerationTask']['id']
print(result)
print('sleeping for image being generated')
time.sleep(25)
print("sleeped")

getpic_parameter = """
query getTaskById($id: ID!) { 
task(id: $id) {
    outputs
}
}
"""
getpic_data = {
    'query': getpic_parameter,
    'variables': {
        'id': str(picid)
    }
}

result_pic = requests.post(url, headers=myheaders, json=getpic_data)
mediaid = []
output = json.loads(result_pic.text)['data']['task']['outputs']
if 'batch' in output:
    for i in output['batch']:
        mediaid.append(i['mediaId'])
else:
    mediaid.append(output['mediaId'])
for id in mediaid:
    data = {
        'query':
            """
    query getMediaById($id: String!) {
media(id: $id) {
urls {
  variant
  url
}
}
}""",
        'variables': {
            'id': str(id)
        }
    }
    pic = requests.post(url, headers=myheaders, json=data)
    datasss = json.loads(pic.text)
    urlpic = datasss['data']['media']['urls'][0]['url']
    imgresponse = requests.get(urlpic)
    img_data = imgresponse.content
    # Create a BytesIO object and put the image data into it
    img_io = BytesIO(img_data)
    # Open the image
    img = Image.open(img_io)
    # Show the image
    # img.show()
    img.save('%s.jpg' % (str(mediaid.index(id)) + ("%02d_%02d_%02d"
                                                   % (time.localtime().tm_hour,
                                                      time.localtime().tm_min,
                                                      time.localtime().tm_sec))))
