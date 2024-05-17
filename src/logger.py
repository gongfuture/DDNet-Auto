import logging
import os
from datetime import datetime
from src.config import get_config_param, ROOT_PATH, set_log_level

# 创建一个logger
logger = logging.getLogger(__name__)

# 设置日志级别
log_level = get_config_param('LogLevel')
logger.setLevel(log_level.upper())

# 创建log目录（如果不存在）
log_dir = ROOT_PATH / 'log'
os.makedirs(log_dir, exist_ok=True)

# 创建一个handler，用于写入日志文件
# 日志文件的名称是当前的日期
log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
log_filepath = os.path.join(log_dir, log_filename)
file_handler = logging.FileHandler(log_filepath)

# 创建一个handler，用于输出到控制台
console_handler = logging.StreamHandler()

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(file_handler)
logger.addHandler(console_handler)

if __name__ == '__main__':
    # 测试代码
    set_log_level('D')
    # 记录不同级别日志
    logger.debug('This is a debug message')
    logger.info('This is a info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')