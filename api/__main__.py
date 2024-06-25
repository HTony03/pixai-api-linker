import requests
from io import BytesIO
from PIL import Image
import json
import time

# TODO:error handlers

api_key = ''
url = 'https://api.pixai.art/graphql'


def gen_pic(parameter):
    """
    generate pics
    WARN: please define your api key before generating(see @define_apikey)
    :param parameter: see @format_tag
    :return: post_data
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }
    data = requests.post(url, json={
        'query': """
mutation createGenerationTask($parameters: JSONObject!) {
  createGenerationTask(parameters: $parameters) {
    id
  }
}
""",
        'variables': {
            'parameters': parameter
        }
    },
                         headers=headers)
    print(data.text)
    return json.loads(data.text)


def get_pic_mediaid(taskId):
    """
    get mediaid of the tasks
    :param taskId: the post_data of gen_pic or post_data['data']['createGenerationTask']['id']
    :return: got mediaid
    """
    if 'data' in taskId:
        taskId = taskId['data']['createGenerationTask']['id']

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }
    getpic_data = {
        'query': """
query getTaskById($id: ID!) { 
task(id: $id) {
    outputs
}
}
""",
        'variables': {
            'id': str(taskId)
        }
    }
    data = requests.post(url, headers=headers, json=getpic_data)
    print(data.text)
    mediaid = []
    output = json.loads(data.text)['data']['task']['outputs']
    if 'batch' in output:
        for i in output['batch']:
            mediaid.append(i['mediaId'])
    else:
        mediaid.append(output['mediaId'])
    return mediaid


def get_pic(mediaId):
    """
    get pics from mediaId
    :param mediaId: the mediaId from @get_pic_mediaid
    :return: pics(auto_save)
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }
    if type(mediaId) == type([]):
        for id in mediaId:
            query = {
                'query': """
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
            data = requests.post(url, headers=headers, json=query)
            urlpic = json.loads(data.text)['data']['media']['urls'][0]['url']
            imgresponse = requests.get(urlpic)
            img_data = imgresponse.content
            # Create a BytesIO object and put the image data into it
            img_io = BytesIO(img_data)
            # Open the image
            img = Image.open(img_io)
            # Show the image
            # img.show()
            img.save('%s.jpg' % (str(mediaId.index(id)) + ("%02d_%02d_%02d"
                                                           % (time.localtime().tm_hour,
                                                              time.localtime().tm_min,
                                                              time.localtime().tm_sec))))


def define_apikey(apikey):
    """
    define your api_key
    :param apikey: your api key
    :return: None
    """
    # TODO:save apikey in storage
    global api_key
    api_key = apikey
    # TODO:try connect

    print('successfully changed the api key')


def format_tag(prompt="1girl",
               model='AnythingV5',
               negativeprompt='(worst quality, low quality, large head, extra digits:1.4), easynegative,',
               samplingSteps=12,
               samplingMethod="Euler a",
               cfgScale=5,
               width=512,
               height=768,
               batchSize=4,
               lora=None):
    if lora is None:
        lora = {}
    model_list = {('AnythingV5', "1648918115270508582"): "1648918115270508582"}
    samplingmethod_list = ['Euler a', 'Euler', 'DDIM', 'LMS','Restart']
    if samplingMethod not in samplingmethod_list:
        samplingMethod = 'Euler a'
        print('WARNING: wrong sampling method\nUsing default Euler a')
    for models in model_list.keys():
        if model in models:
            model = model_list.values()[model_list.keys().index(models)]



    gendata = {
        "prompts": prompt,
        "enableTile": False,
        "negativePrompts": negativeprompt,
        "samplingSteps": samplingSteps,
        "samplingMethod": samplingMethod,
        "cfgScale": cfgScale,
        "modelId": "1648918115270508582",
        "width": width,
        "height": height,
        "batchSize": batchSize,
        "lora": lora
    }
    return gendata
