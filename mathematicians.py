from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    #This creates a HTTP GET which lterally 'gets' content from the url
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                #If the content is HTML or XML it returns the text content
                return resp.content
            else:
                #If the content is not HTML or XML it returns nothing
                return None


    except RequestException as e:
        log_error('There was an error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    #If the response looks like HTML it returns True otherwise, it returns False
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    #This function prints the errors
    print(e)
    

def get_names():
    #This downloads the list of mathematicians url and
    #returns a list of string. In this case it's one per mathematician.
    url = 'http://www.fabpedigree.com/james/mathmen.htm'
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        names = set()
        for li in html.select('li'):
            for name in li.text.split('\n'):
                if len(name) > 0:
                       names.add(name.strip())
        return list(names)
    #Causes an exception if it failed to get data from the url
    raise Exception('There was an error retrieving contents at {}'.format(url))

def get_hits_on_name(name):
    #This accepts a `name` of a mathematician and
    #returns the number of hits within the last 60 days as an integer
    #url_root is a template string that builds a URL
    url_root = 'https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{}'
    response = simple_get(url_root.format(name))

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')

        hit_link = [a for a in html.select('a')
                    if a['href'].find('latest-60') > -1]

        if len(hit_link) > 0:
            #Removes the commas
            link_text = hit_link[0].text.replace(',', '')
            try:
                #Converts the hits to an int
                return int(link_text)
            except:
                log_error("Could not parse{} as an `int`".format(link_text))
    log_error('No pageviews were found for {}'.format(name))
    return None

if __name__ == '__main__':
    print('Getting the list of names...')
    names = get_names()
    print('...done.\n')

    results = []

    print('Getting stats for each name...')

    for name in names:
        try:
            hits = get_hits_on_name(name)
            if hits is None:
                hits = -1
            results.append((hits, name))
        except:
            results.append((-1, name))
            log_error('error encountered while processing '
                      '{}, skipping'.format(name))

    print('...done.\n')

    results.sort()
    results.reverse()

    if len(results) > 5:
        top_marks = results[:5]
    else:
        top_marks = results

    print('\nThe most popular mathematicians are:\n')
    for (mark, mathematician) in top_marks:
        print('{} with {} pageviews'.format(mathematician, mark))

    no_results = len([res for res in results if res[0] == -1])
    print('\nBut we did not find results for '
    '{} mathematicians on the list'.format(no_results))
        
