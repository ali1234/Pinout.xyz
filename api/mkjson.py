#!/usr/bin/env python

import json
import re
import sys
import unicodedata
import glob
import markdown

sys.path.insert(0, "../")
BASE_DIR = "../"

import markjaml
import pinout


lang = "en"

if len(sys.argv) > 1:
    lang  = sys.argv[1]

pinout.load(lang)

overlays = glob.glob("{}src/{}/overlay/*.md".format(BASE_DIR, lang))

pages = {}


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '_', value)


def load_overlay(overlay):
    try:
        data = markjaml.load(overlay) 
        slug = slugify(data['data']['name'])

        filename = 'v1/detail/{}.json'.format(slug)
        web_url = "https://pinout.xyz/pinout/{}".format(slug),

        data['api_output_file'] = filename
        data['data']['pinout_url'] = web_url

        loaded = data
    except IOError:
        return None

    return loaded

overlays = map(load_overlay, overlays)

for overlay in overlays:
    for t in ['power', 'ground']:
        try:
            overlay['data'][t] = list(str(k) for k in overlay['data'][t].keys())
        except (KeyError, AttributeError):
            pass
    data = {
        str(k): v for k, v in overlay["data"].items()
    }
    if "pin" in data:
        data["pin"] = {
            str(k): v for k, v in data["pin"].items()
        }
    filename = overlay['api_output_file']
    data = json.dumps(data, sort_keys=True)
    
    #print("Writing: {}".format(filename))
    #print(data)
    f = open(filename, 'w')
    f.write(data)
    f.close()
