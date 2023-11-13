import unittest
from unittest.mock import patch, mock_open
import alert
class TestCheckNewPapers(unittest.TestCase):
    def setUp(self):
        # テストの前処理
        self.query = "Machine Learning"
        self.fields = ['title', 'publicationDate']
        self.limit = 10
        
    @patch('alert.open', new_callable=mock_open, read_data='2023-01-01')

    def test_get_last_checked_date(self, mock_file):
        # get_last_checked_date 関数のテスト
        result = alert.get_last_checked_date()
        self.assertEqual(result.strftime('%Y-%m-%d'), '2023-01-01')
        # ファイルが存在する場合と存在しない場合の両方をテスト


    @patch('alert.open', new_callable=mock_open)
    def test_update_last_checked_date(self, mock_file):
        # update_last_checked_date 関数のテスト
        alert.update_last_checked_date()
        mock_file.assert_called_with('last_checked.txt', 'w')
        handle = mock_file()
        handle.write.assert_called_once()

    @patch('alert.requests.get')
    def test_check_new_papers(self, mock_get):
        # check_new_papers 関数のテスト
        # APIからの応答をモックして、関数が正しく動作するかをテスト
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '{"data": [{"title": "Test Paper", "publicationDate": "2023-01-01"}]}'

        with patch('alert.get_last_checked_date') as mock_last_date:
            mock_last_date.return_value = alert.datetime.strptime('2023-01-01', '%Y-%m-%d')
            with patch('alert.update_last_checked_date') as mock_update_date:
                alert.check_new_papers(self.query, self.fields, self.limit)
                mock_update_date.assert_called_once()

                # APIが呼び出されたことを確認
                mock_get.assert_called_once()

                # 新しい論文が見つかったことを確認
                # ここではprint文や通知機能の出力をテストする方法を示す
        pass

if __name__ == '__main__':
    unittest.main()
