from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import extruct
from w3lib.html import get_base_url
import re

get_status_code = '''var req = new XMLHttpRequest();
                    req.open('GET', document.location, false);
                    req.send(null);
                    return req.status'''

mobile_user_agent = 'user-agent=Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
desktop_user_agent = 'user-agent=Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'


def cleaner(text):
    temp = text.replace("\n", "")
    temp = temp.replace("\t", "")
    return ' '.join(temp.split())


def crawl_image_size(url):
    try:
        return requests.head(url).headers["Content-length"]
    except Exception as ex:
        print("Crawl image size function error : {}, {}".format(url, ex))
        return 0


def crawl_vary_http(url, user_agent):
    try:
        return requests.head(url, headers={'user-agent': user_agent}).headers["Vary"]
    except Exception as ex:
        print("Crawl vary http function error : {}".format(ex))
        return ""


def crawl_headers(soup):
    try:
        all = []
        headers = soup.find_all('h1')
        for header in headers:
            all.append(header.text)
        return all, len(all)
    except Exception as ex:
        print("Crawl headers function error : {}".format(ex))
        return [], 0


def crawl_links(soup):
    try:
        all_links = {}
        links = soup.find_all('a')
        count = 1
        for link in links:
            if link.get('href') is not None and cleaner(link.text) is not None:
                all_links[count] = {}
                all_links[count]['url'] = link.get('href')
                all_links[count]['relContent'] = link.get('rel')
                all_links[count]['anchor'] = cleaner(link.text)
                count += 1
        return all_links, len(all_links)
    except Exception as ex:
        print("Crawl links function error : {}".format(ex))
        return [], 0


def crawl_images(soup):
    try:
        all_images = {}
        images = soup.find_all('img')
        for id, img in enumerate(images):
            all_images[id] = {}
            all_images[id]['url'] = img.get('src')
            all_images[id]['alt'] = img.get('alt')
            all_images[id]['width'] = img.get('width')
            all_images[id]['height'] = img.get('height')
            all_images[id]['totalSize'] = crawl_image_size(img.get('src'))
        return all_images, len(all_images)
    except Exception as ex:
        print("Crawl images function error : {}".format(ex))
        return [], 0


def crawl_meta_description(soup):
    try:
        meta_tag = soup.find('meta', attrs={'name': 'description'})['content']
        return meta_tag
    except Exception as ex:
        print("Crawl meta desc function error : {}".format(ex))
        return ""


def crawl_structured_data(req, url):
    try:
        structured_data = {}
        base_url = get_base_url(req, url)
        data = extruct.extract(req, base_url=base_url)
        structured_data["json-ld"] = data['json-ld']
        structured_data["rdfa"] = data['rdfa']
        structured_data["microdata"] = data['microdata']
        structured_data["microformat"] = data['microformat']
        opengraph = data['opengraph']
        return structured_data, opengraph
    except Exception as ex:
        print("Crawl structured data function error : {}".format(ex))
        return {}, {}


def crawl_structured_breadcrumbs(soup):
    try:
        breadcrumbs = {}
        results = soup.find_all("ol", {"itemtype": "http://schema.org/BreadcrumbList"})
        for result in results:
            for id, item in enumerate(result.find_all("li", {"itemtype": "http://schema.org/ListItem"})):
                breadcrumbs[id] = {}
                breadcrumbs[id]['url'] = item.find('a').get('href')
                breadcrumbs[id]['detail'] = cleaner(item.find('a').text)
        return breadcrumbs
    except Exception as ex:
        print("Crawl structured breadcrumbs function error : {}".format(ex))
        return {}


def crawl_rel_canonical(soup):
    try:
        canonicals = []
        links = soup.find_all('link', {'rel': 'canonical'})
        for item in links:
            canonicals.append(item['href'])

        a = soup.find_all('a', {'rel': 'canonical'})
        for item in a:
            canonicals.append(item['href'])

        return canonicals
    except Exception as ex:
        print("Crawl canonicals function error : {}".format(ex))
        return []


def crawl_rel_alternate(soup):
    try:
        alternates = []
        links = soup.find_all('link', {'rel': 'alternate'})
        for item in links:
            alternates.append(item['href'])

        a = soup.find_all('a', {'rel': 'alternate'})
        for item in a:
            alternates.append(item['href'])

        return alternates
    except Exception as ex:
        print("Crawl alternates function error : {}".format(ex))
        return []


def crawl_rel_hreflang(soup):
    try:
        hrefs, hreflangs = [], []

        hreflang = soup.find_all("link", hreflang=True)
        for hl in hreflang:
            hreflangs.append(hl['hreflang'])
            hrefs.append(hl['href'])

        links = soup.find_all("a", hreflang=True)
        for a in links:
            hreflangs.append(a['hreflang'])
            hrefs.append(a['href'])

        return hrefs, hreflangs
    except Exception as ex:
        print("Crawl hreflang function error : {}".format(ex))
        return [], []


def crawl_rel_amp(soup):
    try:
        links = []
        amp = soup.find_all("link", {'rel': 'amphtml'})
        for a in amp:
            links.append(a['href'])

        amp2 = soup.find_all("a", {'rel': 'amphtml'})
        for a in amp2:
            links.append(a['href'])

        return links
    except Exception as ex:
        print("Crawl relamp function error : {}".format(ex))
        return []


def crawl_meta_robots(soup):
    try:
        robots = []
        meta = soup.find_all("meta", {'name': 'robots'})
        for a in meta:
            robots.append(a['content'])
        return robots
    except Exception as ex:
        print("Crawl meta robots function error : {}".format(ex))
        return []


def crawl_meta_twitter(soup):
    try:
        tws = {}
        tw = soup.find_all(attrs={'name': re.compile(r'^twitter')})
        for id, t in enumerate(tw):
            tws[id] = {}
            tws[id]['name'] = t.get('name')
            tws[id]['content'] = t.get('content')
        return tws
    except Exception as ex:
        print("Crawl meta twitter function error : {}".format(ex))
        return {}


def check_amp(desktop_soup):
    try:
        amps = crawl_rel_amp(desktop_soup)
        if len(amps) < 1:
            clinks = crawl_rel_canonical(desktop_soup)
            if len(clinks) < 1:
                return False, "No, this page does not include any canonical URL", "", ""
            for links in clinks:
                if 'amp' in links:
                    return False, "No, this page include canonical URL but does not include in amphtml", "", ""
            return False, "No, This page does not include amp.", "", ""
        canonicals = crawl_rel_canonical(desktop_soup)
        for a in amps:
            r = requests.get(a, headers={"user-agent": mobile_user_agent})
            if r.status_code is not 200:
                return False, "No, there is amp url but return {} status code".format(r.status_code), "", ""
            soup = BeautifulSoup(r.content, 'lxml')
            links = crawl_rel_canonical(soup)
            for link in links:
                if link in canonicals:
                    return False, "Yes, it includes a correct canonical URL", link, a
            return False, "No, there is amp url but this page does not include any canonical URL", "", a
    except Exception as ex:
        print(ex)
        return False, "Server Error!", "", ""


def option_generator(is_mobile):
    if is_mobile:
        options = Options()
        options.binary_location = '/opt/headless-chromium'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(mobile_user_agent)
        return options
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(desktop_user_agent)
    return options


def create_requests(url, is_mobile):
    try:
        if is_mobile:
            req = requests.get(url, headers={'user-agent': mobile_user_agent})

        req = requests.get(url, headers={'user-agent': desktop_user_agent})

        if req.status_code is not 200:
            return req, ''

        req_page_source = req.content.decode('utf-8')
        return req, req_page_source
    except Exception as ex:
        print(ex)
        return "", ""


def create_driver(is_mobile):
    if is_mobile:
        return webdriver.Chrome('/opt/chromedriver',
                                         chrome_options=option_generator(True))
    return webdriver.Chrome('/opt/chromedriver',
                                          chrome_options=option_generator(False))


def take_screenshot(driver):
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    return driver.get_screenshot_as_base64()


def close_driver(driver):
    driver.close()
    driver.quit()
    return


def start_js_instance(url):
    desktop_driver = create_driver(False)
    mobile_driver = create_driver(True)

    desktop_driver.get(url)
    mobile_driver.get(url)

    desktop_soup = BeautifulSoup(desktop_driver.page_source, 'lxml')
    mobile_soup = BeautifulSoup(mobile_driver.page_source, 'lxml')


    body = {}

    # Links
    body["linkCompare"] = {}
    body['linkCount'] = {}
    body["linkCompare"]["desktopInternalLinks"], body["linkCount"][
        'desktop'] = crawl_links(desktop_soup)
    body["linkCompare"]["mobileInternalLinks"], body["linkCount"][
        'mobile'] = crawl_links(mobile_soup)

    # Images
    body["imageCompare"] = {}
    body["imageCount"] = {}
    body["imageCompare"]["desktopImageDetails"], body["imageCount"][
        'desktop'] = crawl_images(desktop_soup)
    body["imageCompare"]["mobileImageDetails"], body["imageCount"][
        'mobile'] = crawl_images(mobile_soup)

    # Structured Data Compare
    body["structuredDataCompare"] = {}
    body["structuredDataCompare"]["desktopParsedStructuredData"], desktop_open_graph = crawl_structured_data(
        desktop_driver.page_source, url)
    body["structuredDataCompare"]["mobileParsedStructuredData"], mobile_open_graph = crawl_structured_data(
        mobile_driver.page_source, url)

    # Breadcrumb
    body["breadcrumbCompare"] = {}
    body["breadcrumbCompare"]["desktopBreadcrumb"] = crawl_structured_breadcrumbs(desktop_soup)
    body["breadcrumbCompare"]["mobileBreadcrumb"] = crawl_structured_breadcrumbs(mobile_soup)

    # Meta data compare section
    body["metaDataCompare"] = {}
    body["metaDataCompare"]["title"] = {}
    body["metaDataCompare"]["description"] = {}
    body["metaDataCompare"]["h1"] = {}
    body["metaDataCompare"]["statusCode"] = {}
    body["metaDataCompare"]["relCanonical"] = {}
    body["metaDataCompare"]["relHreflang"] = {}
    body["metaDataCompare"]["relAMP"] = {}
    body["metaDataCompare"]["metaRobots"] = {}
    body["metaDataCompare"]["relAlternate"] = {}
    body["metaDataCompare"]["openGraph"] = {}
    body["metaDataCompare"]["relVaryUserAgent"] = {}
    body["metaDataCompare"]["twitterCards"] = {}

    body["metaDataCompare"]["statusCode"]["desktop"] = {}
    body["metaDataCompare"]["statusCode"]["desktop"][
        "code"] = desktop_driver.execute_script(get_status_code)

    body["metaDataCompare"]["statusCode"]["mobile"] = {}
    body["metaDataCompare"]["statusCode"]["mobile"][
        "code"] = mobile_driver.execute_script(get_status_code)
    body["metaDataCompare"]["title"]["desktop"] = {}
    body["metaDataCompare"]["title"]["desktop"]["title"] = desktop_driver.title
    body["metaDataCompare"]["title"]["desktop"]["count"] = len(
        desktop_driver.title)

    body["metaDataCompare"]["title"]["mobile"] = {}
    body["metaDataCompare"]["title"]["mobile"]["title"] = mobile_driver.title
    body["metaDataCompare"]["title"]["mobile"]["count"] = len(
        mobile_driver.title)

    body["metaDataCompare"]["description"]["desktop"] = {}
    desktop_meta_description = crawl_meta_description(desktop_soup)
    body["metaDataCompare"]["description"]["desktop"][
        "description"] = desktop_meta_description
    body["metaDataCompare"]["description"]["desktop"]["count"] = len(
        desktop_meta_description)

    body["metaDataCompare"]["description"]["mobile"] = {}
    mobile_meta_description = crawl_meta_description(mobile_soup)
    body["metaDataCompare"]["description"]["mobile"][
        "description"] = mobile_meta_description
    body["metaDataCompare"]["description"]["mobile"]["count"] = len(
        mobile_meta_description)

    body["metaDataCompare"]["h1"]["desktop"] = {}
    body["metaDataCompare"]["h1"]["desktop"]["headers"], \
    body["metaDataCompare"]["h1"]["desktop"]["count"] = crawl_headers(
        desktop_soup)

    body["metaDataCompare"]["h1"]["mobile"] = {}
    body["metaDataCompare"]["h1"]["mobile"]["headers"], \
    body["metaDataCompare"]["h1"]["mobile"]["count"] = crawl_headers(mobile_soup)

    body["metaDataCompare"]["relCanonical"]["desktop"] = crawl_rel_canonical(desktop_soup)
    body["metaDataCompare"]["relCanonical"]["mobile"] = crawl_rel_canonical(mobile_soup)

    body["metaDataCompare"]["relHreflang"]["desktop"] = {}
    body["metaDataCompare"]["relHreflang"]["desktop"]["href"], body["metaDataCompare"]["relHreflang"]["desktop"][
        "langs"] = crawl_rel_hreflang(desktop_soup)
    body["metaDataCompare"]["relHreflang"]["mobile"] = {}
    body["metaDataCompare"]["relHreflang"]["mobile"]["href"], body["metaDataCompare"]["relHreflang"]["mobile"][
        "langs"] = crawl_rel_hreflang(desktop_soup)

    body["metaDataCompare"]["relAlternate"]["desktop"] = crawl_rel_alternate(desktop_soup)
    body["metaDataCompare"]["relAlternate"]["mobile"] = crawl_rel_alternate(mobile_soup)

    body["metaDataCompare"]["relAMP"]["desktop"] = crawl_rel_amp(desktop_soup)
    body["metaDataCompare"]["relAMP"]["mobile"] = crawl_rel_amp(mobile_soup)

    body["metaDataCompare"]["metaRobots"]["desktop"] = crawl_meta_robots(desktop_soup)
    body["metaDataCompare"]["metaRobots"]["mobile"] = crawl_meta_robots(mobile_soup)

    body["metaDataCompare"]["openGraph"]["desktop"] = desktop_open_graph
    body["metaDataCompare"]["openGraph"]["mobile"] = mobile_open_graph

    body["metaDataCompare"]["relVaryUserAgent"]["desktop"] = crawl_vary_http(url, desktop_user_agent)
    body["metaDataCompare"]["relVaryUserAgent"]["mobile"] = crawl_vary_http(url, desktop_user_agent)

    body["metaDataCompare"]["twitterCards"]["desktop"] = crawl_meta_twitter(desktop_soup)
    body["metaDataCompare"]["twitterCards"]["mobile"] = crawl_meta_twitter(mobile_soup)

    # check amp
    body["additionalAMPcheck"] = {}
    body["additionalAMPcheck"]['status'], body["additionalAMPcheck"]['message'], body["additionalAMPcheck"][
        'canonicalURL'], body["additionalAMPcheck"]['ampURL'] = check_amp(desktop_soup)

    body["screenshots"] = {}
    body["screenshots"]["desktopBase64"] = take_screenshot(desktop_driver)
    body["screenshots"]["mobileBase64"] = take_screenshot(mobile_driver)

    close_driver(desktop_driver)
    close_driver(mobile_driver)

    return body


def start_nojs_instance(url):
    desktop_req, desktop_page_source = create_requests(url, False)
    mobile_req, mobile_page_source = create_requests(url, True)
    if desktop_page_source == '' and mobile_page_source == '':
        return 'Fail'
    desktop_soup = BeautifulSoup(desktop_page_source, 'lxml')
    mobile_soup = BeautifulSoup(mobile_page_source, 'lxml')

    body = {}

    # Links
    body["linkCompare"] = {}
    body['linkCount'] = {}
    body["linkCompare"]["desktopInternalLinks"], body["linkCount"][
        'desktop'] = crawl_links(desktop_soup)
    body["linkCompare"]["mobileInternalLinks"], body["linkCount"][
        'mobile'] = crawl_links(mobile_soup)

    # Images
    body["imageCompare"] = {}
    body["imageCount"] = {}
    body["imageCompare"]["desktopImageDetails"], body["imageCount"][
        'desktop'] = crawl_images(desktop_soup)
    body["imageCompare"]["mobileImageDetails"], body["imageCount"][
        'mobile'] = crawl_images(mobile_soup)

    # Structured Data Compare
    body["structuredDataCompare"] = {}
    body["structuredDataCompare"]["desktopParsedStructuredData"], desktop_open_graph = crawl_structured_data(
        desktop_page_source, url)
    body["structuredDataCompare"]["mobileParsedStructuredData"], mobile_open_graph = crawl_structured_data(
        mobile_page_source, url)

    # Breadcrumb
    body["breadcrumbCompare"] = {}
    body["breadcrumbCompare"]["desktopBreadcrumb"] = crawl_structured_breadcrumbs(desktop_soup)
    body["breadcrumbCompare"]["mobileBreadcrumb"] = crawl_structured_breadcrumbs(mobile_soup)

    # Meta data compare section
    body["metaDataCompare"] = {}
    body["metaDataCompare"]["title"] = {}
    body["metaDataCompare"]["description"] = {}
    body["metaDataCompare"]["h1"] = {}
    body["metaDataCompare"]["statusCode"] = {}
    body["metaDataCompare"]["relCanonical"] = {}
    body["metaDataCompare"]["relHreflang"] = {}
    body["metaDataCompare"]["relAMP"] = {}
    body["metaDataCompare"]["metaRobots"] = {}
    body["metaDataCompare"]["relAlternate"] = {}
    body["metaDataCompare"]["openGraph"] = {}
    body["metaDataCompare"]["relVaryUserAgent"] = {}
    body["metaDataCompare"]["twitterCards"] = {}

    body["metaDataCompare"]["statusCode"]["desktop"] = {}
    body["metaDataCompare"]["statusCode"]["desktop"][
        "code"] = desktop_req.status_code

    body["metaDataCompare"]["statusCode"]["mobile"] = {}
    body["metaDataCompare"]["statusCode"]["mobile"][
        "code"] = mobile_req.status_code

    body["metaDataCompare"]["title"]["desktop"] = {}
    body["metaDataCompare"]["title"]["desktop"]["title"] = desktop_soup.title.string
    body["metaDataCompare"]["title"]["desktop"]["count"] = len(
        desktop_soup.title.string)

    body["metaDataCompare"]["title"]["mobile"] = {}
    body["metaDataCompare"]["title"]["mobile"]["title"] = mobile_soup.title.string
    body["metaDataCompare"]["title"]["mobile"]["count"] = len(
        mobile_soup.title.string)

    body["metaDataCompare"]["description"]["desktop"] = {}
    desktop_meta_description = crawl_meta_description(desktop_soup)
    body["metaDataCompare"]["description"]["desktop"][
        "description"] = desktop_meta_description
    body["metaDataCompare"]["description"]["desktop"]["count"] = len(
        desktop_meta_description)

    body["metaDataCompare"]["description"]["mobile"] = {}
    mobile_meta_description = crawl_meta_description(mobile_soup)
    body["metaDataCompare"]["description"]["mobile"][
        "description"] = mobile_meta_description
    body["metaDataCompare"]["description"]["mobile"]["count"] = len(
        mobile_meta_description)

    body["metaDataCompare"]["h1"]["desktop"] = {}
    body["metaDataCompare"]["h1"]["desktop"]["headers"], \
    body["metaDataCompare"]["h1"]["desktop"]["count"] = crawl_headers(
        desktop_soup)

    body["metaDataCompare"]["h1"]["mobile"] = {}
    body["metaDataCompare"]["h1"]["mobile"]["headers"], \
    body["metaDataCompare"]["h1"]["mobile"]["count"] = crawl_headers(mobile_soup)

    body["metaDataCompare"]["relCanonical"]["desktop"] = crawl_rel_canonical(desktop_soup)
    body["metaDataCompare"]["relCanonical"]["mobile"] = crawl_rel_canonical(mobile_soup)

    body["metaDataCompare"]["relHreflang"]["desktop"] = {}
    body["metaDataCompare"]["relHreflang"]["desktop"]["href"], body["metaDataCompare"]["relHreflang"]["desktop"][
        "langs"] = crawl_rel_hreflang(desktop_soup)
    body["metaDataCompare"]["relHreflang"]["mobile"] = {}
    body["metaDataCompare"]["relHreflang"]["mobile"]["href"], body["metaDataCompare"]["relHreflang"]["mobile"][
        "langs"] = crawl_rel_hreflang(desktop_soup)

    body["metaDataCompare"]["relAlternate"]["desktop"] = crawl_rel_alternate(desktop_soup)
    body["metaDataCompare"]["relAlternate"]["mobile"] = crawl_rel_alternate(mobile_soup)

    body["metaDataCompare"]["relAMP"]["desktop"] = crawl_rel_amp(desktop_soup)
    body["metaDataCompare"]["relAMP"]["mobile"] = crawl_rel_amp(mobile_soup)

    body["metaDataCompare"]["metaRobots"]["desktop"] = crawl_meta_robots(desktop_soup)
    body["metaDataCompare"]["metaRobots"]["mobile"] = crawl_meta_robots(mobile_soup)

    body["metaDataCompare"]["openGraph"]["desktop"] = desktop_open_graph
    body["metaDataCompare"]["openGraph"]["mobile"] = mobile_open_graph

    body["metaDataCompare"]["relVaryUserAgent"]["desktop"] = crawl_vary_http(url, desktop_user_agent)
    body["metaDataCompare"]["relVaryUserAgent"]["mobile"] = crawl_vary_http(url, desktop_user_agent)

    body["metaDataCompare"]["twitterCards"]["desktop"] = crawl_meta_twitter(desktop_soup)
    body["metaDataCompare"]["twitterCards"]["mobile"] = crawl_meta_twitter(mobile_soup)

    # check amp
    body["additionalAMPcheck"] = {}
    body["additionalAMPcheck"]['status'], body["additionalAMPcheck"]['message'], body["additionalAMPcheck"][
        'canonicalURL'], body["additionalAMPcheck"]['ampURL'] = check_amp(desktop_soup)

    body["screenshots"] = {}

    desktop_driver = create_driver(False)
    mobile_driver = create_driver(True)

    body["screenshots"]["desktopBase64"] = take_screenshot(desktop_driver)
    body["screenshots"]["mobileBase64"] = take_screenshot(mobile_driver)

    close_driver(desktop_driver)
    close_driver(mobile_driver)

    return body


def hello(event, context):
    if 'url' not in event or 'option' not in event:
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

    option = event["option"]
    if option is None:
        option = "js"

    if option == "js":
        body = start_js_instance(url)
    else:
        body = start_nojs_instance(url)

    response = {
        "statusCode": 200,
        "body": body
    }

    return response
