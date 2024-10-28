import re
import requests
import itertools

# regex patterns
CATEGORY_ARTICLES = r'<li[^>]*>.*<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>.*</li>'
ARTICLE_INNER_LINKS = r'<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'
ARTICLE_IMAGES = r'<img[^>]*src=\"(//upload\.wikimedia\.org/[^"]+)\"[^>]*/>'
REF_LINKS = r'<a[^>]*class=\"external[^"]*\"[^>]*href=\"([^"]+)\"[^>]*>'
CAT_LINKS = r'<a[^>]*href=\"(/wiki/Kategoria:[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'


def pipe_join_print(iterable):
    joined = ' | '.join(iterable)
    print(joined)

def get_article_body_text(html: str) -> str:
    return html[html.find('<div id="mw-content-text"'):html.find('<div id="catlinks"')]


def get_article_reflinks_text(html: str) -> str:
    html = html[html.find('id="Przypisy"'):]
    html = html[:html.find('<div class="mw-heading')]

    return html

def get_article_category_text(html: str) -> str:
    return html[html.find('<div id="catlinks"'):]


def findall_with_limit(pattern: str, text: str, flags: int = 0, limit: int = 5) -> list:
    return list(map(lambda m: m.groups(), itertools.islice(re.finditer(pattern, text, flags=flags), limit)))


def get_category_page_url(category: str) -> str:
    parsed_category = category.replace(' ', '_')
    return f'https://pl.wikipedia.org/wiki/Kategoria:{parsed_category}'


def get_category_articles(category: str, limit: int = 3) -> list[tuple[str, str]]:
    category_page_url = get_category_page_url(category)
    # get raw html
    response = requests.get(category_page_url)
    html = response.text
    # parse html
    articles = findall_with_limit(CATEGORY_ARTICLES, html, limit=limit)

    return articles


def get_article(article_url: str) -> str:
    response = requests.get("https://pl.wikipedia.org" + article_url)
    html = response.text
    return html


def get_article_inner_links(article: str, limit: int = 5) -> list[tuple[str, str]]:
    html = get_article_body_text(article)
    links = findall_with_limit(ARTICLE_INNER_LINKS, html, limit=limit)
    
    return links


def get_article_images(article: str, limit: int = 3) -> list:
    html = get_article_body_text(article)
    images = findall_with_limit(ARTICLE_IMAGES, html, limit=limit)
    
    return images


def get_article_refs(article: str, limit: int = 3) -> list:
    html = get_article_reflinks_text(article)
    refs = findall_with_limit(REF_LINKS, html, limit=limit)
    
    return refs


def get_article_categories(article: str, limit: int = 3) -> list:
    html = get_article_category_text(article)
    categories = findall_with_limit(CAT_LINKS, html, limit=limit)
    
    return categories


def main():
    cat = input().strip()
    articles = get_category_articles(cat)
    for article_link, article_title in articles:
        article = get_article(article_link)
        
        links = get_article_inner_links(article)
        pipe_join_print(map(lambda x: x[1], links))
        
        images = get_article_images(article)
        pipe_join_print(map(lambda x: x[0], images))
        
        refs = get_article_refs(article)
        pipe_join_print(map(lambda x: x[0], refs))
        
        categories = get_article_categories(article)
        pipe_join_print(map(lambda x: x[1].removeprefix('Kategoria:'), categories))
    
if __name__ == '__main__':
    main()