
import sys
import os
# 添加 utils 路徑到 sys.path，讓整個 services 模塊都可以導入 utils 中的模塊
utils_path = os.path.join(os.path.dirname(__file__), '../../../../utils')
sys.path.insert(0, utils_path)

from .bpmin_it import BpminItServices
from .bpmin_it_detail import BpminItDetailServices
