
import re
import requests
from lxml.html import parse
from requests.exceptions import ConnectionError

DO_FAIL=False  # fail on error

def is_root_link(link):
    pattern = re.compile("^/$")
    return pattern.match(link)

def is_mailto_link(link):
    pattern = re.compile("^mailto:.*")
    return pattern.match(link)

def is_internal_link(link):
    pattern = re.compile("^/.*")
    return pattern.match(link)

def is_in_page_link(link):
    pattern = re.compile("^#.*")
    return pattern.match(link)

def get_links(doc):
    return [x for x in [y.get("href") for y in doc.cssselect("a")] if not (
            is_root_link(x)
            or is_mailto_link(x))]

def verify_link(link):
    if link[0] == "#":
        # local link on page
        return
    print("verifying "+link)
    try:
        result = requests.get(link, timeout=20, verify=False)
        if result.status_code == 200:
            print(link+" ==> OK")
        elif result.status_code == 307:
            print(link+" ==> REDIRECT")
        else:
            print("ERROR: link `"+link+"` failed with status "
                  , result.status_code)
            if DO_FAIL:
                raise Exception("Failed verify")
    except ConnectionError as ex:
        print("ERROR: ", link, ex)
        if DO_FAIL:
            raise ex

def check_page(host, start_url):
    print("")
    print("Checking links host "+host+" in page `"+start_url+"`")
    doc = parse(start_url).getroot()
    links = get_links(doc)

    internal_links = filter(is_internal_link, links)
    external_links = [x for x in links if not (is_internal_link(x) or is_in_page_link(x))]

    for link in internal_links:
        verify_link(host+link)

    for link in external_links:
        verify_link(link)

def check_links(args_obj, parser):
    print("")
    print("Checking links")
    host = args_obj.host

    # Check the home page
    check_page(host, host)

    # Check traits page
    check_page(
        host,
        host+"/show_trait?trait_id=1435395_s_at&dataset=HC_M2_0606_P")
