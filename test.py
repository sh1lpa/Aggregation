import unittest
import pandas as pd
from unittest.mock import patch
from io import StringIO
from Aggregations import url_request, get_transactions, pivot_table, get_formula_data, compute_aggregates

class TestAggregations(unittest.TestCase):
    
    @patch('requests.get')
    def test_url_request(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.text = 'IDENTIFIER,TIME_PERIOD,OBS_VALUE\n1,2022-01-01,100\n1,2022-02-01,200\n'
        
        response = url_request('D.CHF.EUR.SP00.A')
        
        self.assertEqual(response.text, 'IDENTIFIER,TIME_PERIOD,OBS_VALUE\n1,2022-01-01,100\n1,2022-02-01,200\n')
        mock_get.assert_called_with(
            'https://sdw-wsrest.ecb.europa.eu/service/data/BP6/D.CHF.EUR.SP00.A',
            params={'detail': 'dataonly'},
            headers={'Accept': 'text/csv'}
        )
    
    @patch('Aggregations.url_request')
    @patch('pandas.read_csv')
    def test_get_transactions(self, mock_read_csv, mock_url_request):
        mock_url_request.return_value = 'IDENTIFIER,TIME_PERIOD,OBS_VALUE\n1,2022-01-01,100\n1,2022-02-01,200\n'
        mock_read_csv.return_value = pd.DataFrame({
            'IDENTIFIER': [1, 1],
            'TIME_PERIOD': ['2022-01-01', '2022-02-01'],
            'OBS_VALUE': [100, 200]
        })
        
        response_df = get_transactions('D.CHF.EUR.SP00.A')
        
        self.assertEqual(response_df.shape, (2, 3))
        self.assertEqual(list(response_df.columns), ['IDENTIFIER', 'TIME_PERIOD', 'OBS_VALUE'])
        self.assertEqual(list(response_df['IDENTIFIER']), [1, 1])
        self.assertEqual(list(response_df['TIME_PERIOD']), ['2022-01-01', '2022-02-01'])
        self.assertEqual(list(response_df['OBS_VALUE']), [100, 200])
    
    def test_pivot_table(self):
        dfs = []
        
        pivot_table(dfs, 'D.CHF.EUR.SP00.A', False)
        
        self.assertEqual(len(dfs), 1)
        self.assertTrue(isinstance(dfs[0], pd.DataFrame))
        self.assertEqual(dfs[0].shape, (2, 1))
        self.assertEqual(list(dfs[0].index), ['TIME_PERIOD'])
        self.assertEqual(list(dfs[0].columns), [('OBS_VALUE', 'D.CHF.EUR.SP00.A')])
    
    def test_get_formula_data(self):
        formula = 'result = D.CHF.EUR.SP00.A + D.EUR.USD.SP00.A - D.GBP.USD.SP00.A'
        with patch('Aggregations.get_transactions') as mock_get_transactions:
            mock_get_transactions.side_effect = [
                pd.DataFrame({
                    'IDENTIFIER': ['D.CHF.EUR.SP00.A'],
                    'TIME_PERIOD': ['2022-01-01'],
                    'OBS_VALUE': [100]
                }),
                pd.DataFrame({
                    'IDENTIFIER': ['D.EUR.USD.SP00.A'],
                    'TIME_PERIOD': ['2022-01-01'],
                    'OBS_VALUE': [200]
                }),
                pd.DataFrame({
                    'IDENTIFIER': ['D.GBP.USD.SP00.A'],
                    'TIME_PERIOD': ['2022-01-01'],
                    'OBS_VALUE': [50]
                }),
            ]
            
            df = get_formula_data(formula)
            
            self.assertEqual(df.shape, (1, 3))
            self.assertEqual(list(df.columns), [('OBS_VALUE', 'D.CHF.EUR.SP00.A'), ('OBS_VALUE', 'D.EUR.USD.SP00.A'), ('OBS_VALUE', 'D.GBP.USD.SP00.A')])
            self.assertEqual(list(df.index), ['2022-01-01'])
            self.assertEqual(list(df.iloc[0]), [100, 200, 50])
    
    def test_compute_aggregates(self):
        formula = 'result = D.CHF.EUR.SP00.A + D.EUR.USD.SP00.A - D.GBP.USD.SP00.A'
        with patch('Aggregations.get_formula_data') as mock_get_formula_data:
            mock_get_formula_data.return_value = pd.DataFrame({
                'OBS_VALUE': [100, 200, 50]
            }, index=['2022-01-01', '2022-01-02', '2022-01-03'])
            
            df = compute_aggregates(formula)
            
            self.assertEqual(df.shape, (3, 1))
            self.assertEqual(list(df.columns), ['result'])
            self.assertEqual(list(df.index), ['2022-01-01', '2022-01-02', '2022-01-03'])
            self.assertEqual(list(df['result']), [100, 200, 50])
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('builtins.print')
    def test_main(self, mock_print, mock_parse_args):
        mock_parse_args.return_value = {
            'formula': 'result = D.CHF.EUR.SP00.A + D.EUR.USD.SP00.A - D.GBP.USD.SP00.A'
        }
        
        main()
        
        mock_print.assert_called_with(mock_parse_args.return_value['formula'])
        # Additional assertions for the file creation and CSV content can be added if required

if __name__ == '__main__':
    unittest.main()
