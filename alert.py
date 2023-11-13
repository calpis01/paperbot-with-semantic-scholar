import requests
import json
from datetime import datetime, timedelta
import schedule
import time
ss_url = 'http://api.semanticscholar.org/graph/v1/paper/search?'
# QUERY PARAMETERS(https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/post_graph_get_papers)
fields = (
    'paperId', 'title','url',  'venue','authors', 'abstract', 'year', 'externalIds', 'influentialCitationCount',
    'citationCount', 'publicationDate', 'isOpenAccess', 'openAccessPdf', 'fieldsOfStudy', 'publicationVenue', 'tldr', 's2FieldsOfStudy'
)
# 前回のチェック日時を保存するファイル
last_checked_file = 'last_checked.txt'
def generate_url(ss_url_, query_list_, fields_, limit_, offset_):
    all_fields = ''
    for field in fields_:
        all_fields += field + ','
    url = ss_url_ + 'query=' + query_list_ + '&fields=' + all_fields[:-1] + '&limit=' + str(limit_) + '&offset=' + str(offset_)
    return url

def get_last_checked_date():
    try:
        with open('last_checked.txt', 'r') as file:
            last_checked_date = file.read().strip()
            # 空の場合はデフォルトの日付を返す
            if not last_checked_date:
                return datetime.now()
            return datetime.strptime(last_checked_date, '%Y-%m-%d')
    except FileNotFoundError:
        # ファイルが存在しない場合もデフォルトの日付を返す
        return datetime.now()

def update_last_checked_date():
    with open(last_checked_file, 'w') as file:
        file.write(datetime.now().strftime('%Y-%m-%d'))

def check_new_papers(query, fields, limit):
    last_checked_date = get_last_checked_date()
    
    if not last_checked_date:
        last_checked_date = datetime.now() - timedelta(days=1)

    # Semantic Scholar APIを呼び出すためのURLを生成
    url = generate_url(ss_url, query, fields, limit, 0)

    # APIからデータを取得
    response = requests.get(url)
    if response.status_code == 429:
        print("Rate limit exceeded. Waiting before retrying...")
        time.sleep(60)  # 60秒待機してから再試行
        return check_new_papers(query, fields, limit)
    elif response.status_code != 200:
        print(f"Error fetching data from Semantic Scholar API: Status Code {response.status_code}")
        print(f"Response: {response.text}")
        return

    papers = json.loads(response.text)['data']
    new_papers = [paper for paper in papers if paper['publicationDate'] is not None and datetime.strptime(paper['publicationDate'], '%Y-%m-%d') > last_checked_date]

    if new_papers:
        # 新しい論文が見つかった場合の処理
        for paper in new_papers:
            print(f"New paper found: {paper['title']} published on {paper['publicationDate']}")
            # ここで、Discordやメールなどで通知を送る処理を追加

    # 最後にチェックした日付を更新
    update_last_checked_date()

# 例: 毎日特定のキーワードで新しい論文をチェック
schedule.every().day.at("20:51:50").do(check_new_papers, query="Machine Learning", fields=fields, limit=10)
check_new_papers(query="Machine Learning", fields=fields, limit=100)
while False:
    schedule.run_pending()
    time.sleep(1)
