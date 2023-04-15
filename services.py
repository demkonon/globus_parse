import bs4


def list_to_dict(arr):
    dict = {}
    for i in range(len(arr)+1):
        try:
            if not i % 2:
                dict.update({arr[i]: arr[i+1]})
        except IndexError:
            continue


    return dict


def remove_shit(s: str) -> str:
    return s.replace('\n', '').replace(' ', '').strip()

class GetTagValue:
    def __init__(self, tag: bs4.Tag):
        self.tag = tag

    def value(self, tag_name: str) ->str:
        try:
            return self.tag.find(tag_name).text
        except:
            return ''

    def scope(self, tag_name: str, scope: dict):
        try:
            return self.tag.find(tag_name, scope).text
        except:
            return ''


class GetDictValue:
    def __init__(self, dict):
        self.dict = dict

    def value(self, key):
        try:
            return self.dict[key]
        except:
            return ''

