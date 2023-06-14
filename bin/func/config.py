from typing import Dict
import os
import yaml

def merge(left: Dict, right: Dict) -> Dict:
    for key in right:
        if key in left:
            if isinstance(left[key], dict) and isinstance(right[key], dict):
                merge(left[key], right[key])
            elif left[key] != right[key]:
                left[key] = right[key]
        else:
            left[key] = right[key]
    return left


def read_config() -> Dict:


    lconf = 'config.yaml.dist'
    if not os.path.exists(lconf):
        lconf = os.path.join('..','config.yaml.dist')
        if not os.path.exists(lconf):
            lconf = os.path.join('..','..','config.yaml.dist')
            if not os.path.exists(lconf):
                print("warning unable to find config!")
                return 

    with open(lconf) as handle:
        ret = yaml.safe_load(handle.read())
        path = lconf.replace('.dist','')

        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path) as handle:
                ret = merge(ret, yaml.safe_load(handle.read()))
        return ret


config = read_config()  # pylint: disable=invalid-name
