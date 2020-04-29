import requests
import trafilatura
import urllib.request
from inscriptis import get_text


mobile_user_agent = 'user-agent=Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
desktop_user_agent = 'user-agent=Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'


def fetch_url(url, user_agent):
    headers = {
        'Connection': 'close',
        'User-Agent': user_agent,
    }
    # send
    try:
        response = requests.get(url, timeout=30, verify=False, allow_redirects=True, headers=headers)
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL):
        print('malformed URL: %s', url)
    except requests.exceptions.TooManyRedirects:
        print('redirects: %s', url)
    except requests.exceptions.SSLError as err:
        print('SSL: %s %s', url, err)
    else:
        if response.status_code != 200:
            print('not a 200 response: %s', response.status_code)
        else:
            return decode_response(response)
    return None


def decode_response(response):
    guessed_encoding = 'UTF-8'
    if guessed_encoding is not None:
        try:
            htmltext = response.content.decode(guessed_encoding)
        except UnicodeDecodeError:
            htmltext = response.text
    else:
        htmltext = response.text
    return htmltext


def create_requests(url, user_agent):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', user_agent)
        content = urllib.request.urlopen(req).read().decode('utf-8')

        return content
    except Exception as ex:
        print(ex)
        return ""


def crawl_extracted_content(url, user_agent):
    try:
        html = fetch_url(url, user_agent)
        extract_text = trafilatura.extract(html)
        return extract_text
    except Exception as ex:
        print(html)
        print(ex)
        return ""


def full_html_content(url, user_agent):
    try:
        html = create_requests(url, user_agent)
        text = get_text(html)
        return text
    except Exception as ex:
        print(ex)
        return ""


def hello(event, context):
    if 'url' not in event:
        return {
            "statusCode": 404,
            "data": "",
            "error": "Parameter missing!"
        }
    url = event["url"]
    if url is None:
        return {
            "statusCode": 404,
            "data": "",
            "error": "Url parameter missing!"
        }

    body = {}
    body["contentCompare"] = {}
    body["contentCompare"]["desktop"] = {}
    body["contentCompare"]["mobile"] = {}

    desktop_extracted_content = crawl_extracted_content(url, desktop_user_agent)
    body["contentCompare"]["desktop"]["extractedContent"] = desktop_extracted_content
    if desktop_extracted_content is not None:
        body["contentCompare"]["desktop"]["extractedContentWordCount"] = len(str(desktop_extracted_content))
    else:
        body["contentCompare"]["desktop"]["extractedContentWordCount"] = 0

    mobile_extracted_content = crawl_extracted_content(url, mobile_user_agent)
    body["contentCompare"]["mobile"]["extractedContent"] = mobile_extracted_content
    if mobile_extracted_content is not None:
        body["contentCompare"]["mobile"]["extractedContentWordCount"] = len(str(mobile_extracted_content))
    else:
        body["contentCompare"]["mobile"]["extractedContentWordCount"] = 0

    desktop_full_html = full_html_content(url, desktop_user_agent)
    body["contentCompare"]["desktop"]["fullHTMLcontent"] = desktop_full_html
    if desktop_full_html is not None:
        body["contentCompare"]["desktop"]["fullHTMLContentWordCount"] = len(str(desktop_full_html))
    else:
        body["contentCompare"]["desktop"]["fullHTMLContentWordCount"] = 0

    mobile_full_html = full_html_content(url, mobile_user_agent)
    body["contentCompare"]["mobile"]["fullHTMLcontent"] = mobile_full_html
    if mobile_user_agent is not None:
        body["contentCompare"]["mobile"]["fullHTMLContentWordCount"] = len(str(mobile_full_html))
    else:
        body["contentCompare"]["mobile"]["fullHTMLContentWordCount"] = 0

    response = {
        "statusCode": 200,
        "body": body
    }

    return response

