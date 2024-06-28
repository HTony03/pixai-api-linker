# Pixai_api_linker
A small program to connect to `pixai api` 

### future features
- [X] A pypi package with the basic features
- [ ] other possible features

### current features
- [x] link to api & generate/get pictures

### example code
```python
from pixai_openapi import *
import time

if __name__ == '__main__':
    pass


genpic_data = gen_pic({
    "prompts":
"""GTS, GigaGTS, Cramped, PlanetaryGTS, Looming,solo,(((a giant girl))),
(((a giant girl treads on a mini city))),1girl, (loli,wariza:1.5), cute girl,
(((extremely kawaii girl))),long_silver|pink_hair,(kawaii|magical_girl clothes, 
fairy_tale texture pink|silver clothes:1.3),colorful rainbow texture magic pink dress,
cat ears, ((fill the screen)),full body,day:1.2,proving Earth is flat,horizon, city:2.8,
(loli,medium breasts),giantess""",
    "enableTile": False,
    "negativePrompts": """(worst quality, low quality, large head, extra digits:1.4), easynegative,
castle background,castle,indoors,black background, space background""",
    "samplingSteps": 12,
    "samplingMethod": "Euler a",
    "cfgScale": 5,
    "modelId": "1648918115270508582",
    "width": 512,
    "height": 768,
    "batchSize": 4,
    "lora": {
        "1664117900185699763": 0.7,
        "1632808153143363282": 0.7
    }
})
time.sleep(25)
get_pic(get_pic_mediaid(genpic_data))

```

## Versions

`v0.0.2.dev5` add some features & fix bugs & save api key safely in the sortage