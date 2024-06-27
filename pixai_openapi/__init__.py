import requests
from io import BytesIO
from PIL import Image
import json
import time
from requests.exceptions import *

_api_key = ''
_url = 'https://api.pixai.art/graphql'
# TODO: download custome & choose the quality of pics to download


def handler(request_text):
    """
        Handles the response from the API request. If there are errors in the response, it prints the error details
        and raises a ConnectionError.

        :param request_text: The response text from the API request.
        :raises ConnectionError: If there are errors in the response.
        """
    if 'errors' in json.loads(request_text):
        print('message:%s' % request_text['errors'][0]['message'])
        print('loc:%s' % request_text['errors'][0]['locations'])
        if 'path' in request_text['errors'][0]:
            print('path:%s' % request_text['errors'][0]['path'])
        print('extension code:%s' % request_text['errors'][0]['extensions']['code'])
        if 'data' in request_text:
            print('returned data:%s' % request_text['data'])
        raise ConnectionError('Error accursed when handling the request')


def gen_pic(parameter):
    """
    Generates pictures using the Pixai API.
    Sends a POST request to the API with the provided parameters
    and handles the response.
    WARN: please define your api key before generating(see @define_apikey)

    :param parameter: The parameters for the picture generation, see @format_tag
    :return: The response from the API as a JSON object.
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + _api_key
        }
        data = requests.post(_url, json={
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
        handler(data.text)
        if 'data' in data.text:
            print(json.loads(data.text)['data']['createGenerationTask']['id'])
        return json.loads(data.text)
    except ConnectionResetError as E:
        print("Connection was forcibly closed by the remote host:")
        print(E)
    except ConnectionError as E:
        print("Connection Error:")
        print(E)


def get_pic_mediaid(taskId):
    """
    Gets the media IDs of the tasks.
    Sends a POST request to the API with the task ID and handles the response.
    15 to 25 seconds are recommended to wait for the pics to be generated

    :param taskId: the response of @gen_pic or response['data']['createGenerationTask']['id']
    :return: A list of media IDs
    """
    try:
        if 'data' in taskId:
            taskId = taskId['data']['createGenerationTask']['id']

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + _api_key
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
        data = requests.post(_url, headers=headers, json=getpic_data)
        print(data.text)
        handler(data.text)
        mediaid_list = []
        if not (json.loads(data.text)['data']['task']):
            print('invalid task!')
            print("maybe your pictures are not generated yet")
            return 0
        output = json.loads(data.text)['data']['task']['outputs']
        print('parameters:%s' % json.dumps(output['detailParameters'], indent=4))
        print('duration:%s s' % output['duration'])
        if 'batch' in output:
            for i in output['batch']:
                mediaid_list.append(i['mediaId'])
        else:
            mediaid_list.append(output['mediaId'])
        return mediaid_list
    except ConnectionResetError as E:
        print("Connection was forcibly closed by the remote host:")
        print(E)
    except ConnectionError as E:
        print("Connection Error:")
        print(E)


def get_pic(mediaId):
    """
    Gets the pictures from the media IDs.
    Sends a POST request to the API with the media ID and handles the response.

    :param mediaId: The media ID from @get_pic_mediaid
    :return: The pictures(auto_save)
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + _api_key
    }
    if type(mediaId) == type([]):
        for id in mediaId:
            try:
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
                data = requests.post(_url, headers=headers, json=query)
                print(data.text)
                handler(data.text)
                urlpic = json.loads(data.text)['data']['media']['urls'][0]['url']
                time.sleep(1)
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
            except ConnectionResetError as E:
                print("Connection was forcibly closed by the remote host:")
                print(E)
            except ConnectionError as E:
                print("Connection Error:")
                print(E)
    elif type(mediaId) == type('') or type(mediaId) == type(0):
        if mediaId == 0 or mediaId == '0':
            return 0

        try:
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
                    'id': str(mediaId)
                }
            }
            data = requests.post(_url, headers=headers, json=query)
            print(data.text)
            handler(data.text)
            urlpic = json.loads(data.text)['data']['media']['urls'][0]['url']
            time.sleep(1)
            imgresponse = requests.get(urlpic)
            img_data = imgresponse.content
            # Create a BytesIO object and put the image data into it
            img_io = BytesIO(img_data)
            # Open the image
            img = Image.open(img_io)
            # Show the image
            # img.show()
            img.save('%s.jpg' % ("single" + ("%02d_%02d_%02d"
                                             % (time.localtime().tm_hour,
                                                time.localtime().tm_min,
                                                time.localtime().tm_sec))))
        except ConnectionResetError as E:
            print("Connection was forcibly closed by the remote host:")
            print(E)
        except ConnectionError as E:
            print("Connection Error:")
            print(E)


def define_apikey(apikey):
    """
    Defines the API key for the Pixai API

    :param apikey: The API key.
    """
    # TODO:save apikey in storage
    global _api_key
    _api_key = apikey
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + _api_key
        }

        query = {
            'query': """
    mutation createGenerationTask($parameters: JSONObject!) {
      createGenerationTask(parameters: $parameters) {
        id
      }
    }""",
            'variables': {
                'parameters': {
                    "prompts":
                        """solo,1girl,
        (loli,wariza:1.5), cute girl,(((extremely kawaii girl))),((fill the screen)),
        full body,day:1.9,(loli,small breasts), tall female,<lora:more_details:1>
        1girl, solo, long hair, looking at viewer, blush, smile, bangs, blue eyes, blonde hair,
        hair ornament, gloves, long sleeves, dress, sitting, very long hair, full body, braid, heart,
         multicolored hair, medium breasts, frills, wings, barefoot, fingerless gloves, nail polish,
         white dress, two side up,streaked hair, book, symbol-shaped pupils, thigh strap, halo, feathers,""",
                    "negativePrompts": '(worst quality, low quality, large head, extra digits:1.4), easynegative,',
                    "samplingSteps": 12,
                    "samplingMethod": "Euler a",
                    "cfgScale": 5,
                    "modelId": "1648918115270508582",
                    "width": 256,
                    "height": 384,
                    "batchSize": 4,
                }
            }
        }
        data = requests.post(_url, headers=headers, json=query)
        data_json = json.loads(data.text)
        if 'message' in data_json:
            print('Invalid token:')
            print("out:%s,code:%s" % (data_json['message'], data_json['code']))
        else:
            print('successfully changed the api key')
            print('test generated pic:taskid=%s,est credit:200' 
                  % json.loads(data.text)['data']['createGenerationTask']['id'])
    except ConnectionResetError as E:
        print("Connection was forcibly closed by the remote host:")
        print(E)
    except ConnectionError as E:
        print("Connection Error:")
        print(E)


def format_tag(prompt="1girl",
               model='AnythingV5',
               negativeprompt='(worst quality, low quality, large head, extra digits:1.4), easynegative,',
               samplingSteps=12,
               samplingMethod="Euler a",
               cfgScale=5,
               width=512,
               height=768,
               batchSize=1,
               lora=None):
    """
        Formats the tag for the Pixai API.

        :param prompt: The prompt for the picture generation.
        :type prompt:str
        :param model: The model to be used for the picture generation.
        :type model:str,the ver num of the model or the name (only covers some models,maybe not in database)
        :param negativeprompt: The negative prompt for the picture generation.
        :type negativeprompt:str
        :param samplingSteps: The number of sampling steps.
        :type samplingSteps:int
        :param samplingMethod: The sampling method to be used.
        :type samplingMethod:str,list following:
        ['Euler a', 'Euler', 'DDIM', 'LMS', 'Restart', 'Heun', 'DPM2 Karras',
       'DPM2 a Karras', 'DPM++ 2M Karras', 'DPM++ 2S a Karras', 'DPM++ SDEMKarras',
       'DPM++ 2M SDEKarras']
        :param cfgScale: The configuration scale.
        :type cfgScale:int
        :param width: The width of the picture.
        :type width:int
        :param height: The height of the picture.
        :type height:int
        :param batchSize: The batch size.
        :type batchSize:int
        :param lora: The lora parameters.
        :return: The formatted tag as a dictionary.
        """
    if lora is None:
        lora = {}
    model_list = {('AnythingV5', "1648918115270508582"): "1648918115270508582",
                  ('Moonbeam', '1648918127446573124'): '1648918127446573124',
                  ('Whimsical', '1648918121624879157'): '1648918121624879157',
                  ('Neverland', '1648918123654922298'): '1648918123654922298',
                  ('Shinymood', '1668725869389316083'): '1668725869389316083',
                  ('Hassaku', '1648918119460618288'): '1648918119460618288',
                  ('Pixai Diffusion (CG)', '1684657781067182082'): '1684657781067182082',
                  ('Animagine XL V3', '1702058694023647156'): '1702058694023647156',
                  ('Sunflower', '1709400693561386681'): '1709400693561386681'
                  }
    samplingmethod_list = ['Euler a', 'Euler', 'DDIM', 'LMS', 'Restart', 'Heun', 'DPM2 Karras',
                           'DPM2 a Karras', 'DPM++ 2M Karras', 'DPM++ 2S a Karras', 'DPM++ SDEMKarras',
                           'DPM++ 2M SDEKarras']
    if samplingMethod not in samplingmethod_list:
        samplingMethod = 'Euler a'
        print('WARNING: wrong sampling method\nUsing default Euler a')
    model_out = None
    for models in list(model_list.keys()):
        if model in models:
            model_out = list(model_list.values())[list(model_list.keys()).index(models)]
    try:
        model_out = str(int(model))
    except ValueError:
        pass
    if not model_out:
        print("WARNING: invalid model\nUsing default AnythingV5")
        model_out = "1648918115270508582"

    gendata = {
        "prompts": prompt,
        "enableTile": False,
        "negativePrompts": negativeprompt,
        "samplingSteps": samplingSteps,
        "samplingMethod": samplingMethod,
        "cfgScale": cfgScale,
        "modelId": model_out,
        "width": width,
        "height": height,
        "batchSize": batchSize,
        "lora": lora
    }
    return gendata
