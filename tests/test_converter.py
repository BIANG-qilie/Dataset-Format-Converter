"""
测试转换器功能
"""

import os
import tempfile
import pytest

from labelimgobb2DOTA_converter import (
    DOTA2labelimgOBB,
    labelimgOBB2DOTA
)


class TestConverter(unittest.TestCase):
    """转换器测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_yolo_data = "0 0.5 0.3 0.7 0.4 0.8 0.6 0.2 0.7\n"
        self.sample_labelimg_data = "YOLO_OBB\n0 640.0 360.0 200.0 150.0 45.0\n"
        
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_yolo_to_labelimg_conversion(self):
        """测试YOLO到labelimg转换"""
        # 创建测试输入文件
        input_file = os.path.join(self.temp_dir, "test_input.txt")
        output_file = os.path.join(self.temp_dir, "test_output.txt")
        
        with open(input_file, 'w') as f:
            f.write(self.sample_yolo_data)
        
        # 执行转换
        DOTA2labelimgOBB(input_file, output_file, 1280, 720)
        
        # 验证输出文件存在
        self.assertTrue(os.path.exists(output_file))
        
        # 验证输出内容
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn("YOLO_OBB", content)
            self.assertIn("0 ", content)  # 类别ID
    
    def test_labelimg_to_yolo_conversion(self):
        """测试labelimg到YOLO转换"""
        # 创建测试输入文件
        input_file = os.path.join(self.temp_dir, "test_input.txt")
        output_file = os.path.join(self.temp_dir, "test_output.txt")
        
        with open(input_file, 'w') as f:
            f.write(self.sample_labelimg_data)
        
        # 执行转换
        labelimgOBB2DOTA(input_file, output_file, 1280, 720)
        
        # 验证输出文件存在
        self.assertTrue(os.path.exists(output_file))
        
        # 验证输出内容
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn("0 ", content)  # 类别ID
            # 验证有8个坐标值（4个点）
            parts = content.strip().split()
            self.assertEqual(len(parts), 9)  # 1个类别ID + 8个坐标


if __name__ == '__main__':
    unittest.main() 