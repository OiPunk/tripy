# 得到项目所在绝对路径
from pathlib import Path

basic_dir = Path(__file__).resolve().parent.parent

# 项目默认运行数据库
db = str(basic_dir / "travel_new.sqlite")

# 工具初始化与重置会用到的本地数据库路径
local_file = str(basic_dir / "travel_new.sqlite")

# 创建一个备份文件，允许我们在测试的时候可以重新开始
backup_file = str(basic_dir / "travel2.sqlite")
