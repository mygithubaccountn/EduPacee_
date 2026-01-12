from django.test import TestCase
import pandas as pd
from io import BytesIO
from edupace_app import excel_utils_refined as eu

class ExcelUtilsRefinedTests(TestCase):
    def test_valid_excel_file(self):
        data = {
            'Student ID': [1, 2],
            'Outcome': ['A', 'B'],
            'Score': [85, 90]
        }
        df = pd.DataFrame(data)
        buf = BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)

        file_mock = type('File', (), {'name': 'test.xlsx', 'read': lambda: buf.getvalue()})()

        self.assertTrue(eu.is_valid_excel(file_mock))
        parsed_df = eu.read_excel_file(BytesIO(file_mock.read()))
        self.assertIsNotNone(parsed_df)
