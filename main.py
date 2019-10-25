from __future__ import annotations

from typing import Union, Dict, NoReturn, List, Any

import pandas
import requests

_APP_ID = 1065803457  # https://apps.apple.com/ru/app/лига-ставок-ставки-на-спорт/id1065803457


def row_for_entry(entry: Dict) -> List[Any]:
    """
    :param entry:
    :return: List with data in order: ['id', 'author', 'content', 'rating', 'version']
    """
    review_id = int(entry['id']['label'])
    author = entry['author']['name']['label']
    content = entry['content']['label']
    rating = int(entry['im:rating']['label'])
    version = entry['im:version']['label']
    return [review_id, author, content, rating, version]


def get_reviews(*, app_id: int, page: int = 1) -> Union[List[Any], NoReturn]:
    """
    :param app_id: ID of application in App Store
    :param page:
    :return: List of Review objects on selected page;
    None if there are no reviews or something went wrong during request
    """
    rss_url = f'https://itunes.apple.com/RU/rss/customerreviews/id={app_id}/page={page}/sortby=mostrecent/json'
    response = requests.get(rss_url)
    if response.status_code != 200:
        return None
    extracted_reviews = []
    for d in response.json()['feed'].get('entry', []):
        try:
            extracted_reviews.append(row_for_entry(d))
        except KeyError:  # if something is wrong with entry, let's just ignore it
            pass
    return extracted_reviews or None


def dataframe_from_reviews(*, app_id: int, max_pages: int = 10) -> pandas.DataFrame:
    """
    :param app_id:
    :param max_pages:
    :return: DataFrame with columns=['id', 'author', 'content', 'rating', 'version'] from the received read
    """
    all_reviews = []
    for current_page in range(1, max_pages+1):
        reviews_for_page = get_reviews(app_id=app_id, page=current_page)
        if reviews_for_page:
            all_reviews += reviews_for_page
    return pandas.DataFrame(data=all_reviews, columns=['id', 'author', 'content', 'rating', 'version'])


if __name__ == '__main__':
    parsed_data = dataframe_from_reviews(app_id=_APP_ID, max_pages=10)
    parsed_data.to_csv(f'{_APP_ID}.csv')
