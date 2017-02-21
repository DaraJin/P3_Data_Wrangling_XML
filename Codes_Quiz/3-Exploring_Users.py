'''
Exploring Users
'''
import xml.etree.cElementTree as ET
import pprint
import re

def get_user(element):
    return


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if 'uid' in element.attrib:
            users.add(element.attrib['uid']) 
    return users


def test():

    users = process_map('example.osm')
    pprint.pprint(users)
    assert len(users) == 6



if __name__ == "__main__":
    test()