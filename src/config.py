from ruamel.yaml import YAML
from pathlib import Path
from typing import *

# 获取当前文件的绝对路径
# current_path = os.path.dirname(os.path.abspath(__file__))
# 获取仓库的根目录
ROOT_PATH = Path(__file__).resolve().parent.parent
# 创建一个全局变量来存储配置
CONFIG: Dict = None
# 创建一个YAML对象
yaml = YAML()


def load_config() -> None:
    """
    读取配置文件
    :return: None
    """
    global CONFIG
    if CONFIG is None:
        config_path = ROOT_PATH / 'config/config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            CONFIG = yaml.load(f)


def fix_boolean_values(dictionary: dict) -> None:
    """
    将config中错误格式的布尔值转换为正确的格式
    :param dictionary: 待处理的字典
    :return: None
    """
# 创建一个列表，包含所有可能的布尔值的字符串表示
    true_values = ['true', 'ture', 'treu', 't', 'yes', 'y', '1']
    false_values = ['false', 'fasle', 'fales', 'flase', 'f', 'no', 'n', '0']
    for key, value in dictionary.items():
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower in true_values:
                dictionary[key] = True
            elif value_lower in false_values:
                dictionary[key] = False
        elif isinstance(value, dict):
            fix_boolean_values(value)
    # 将修改后的CONFIG字典写回到config.yaml文件中
    config_path = ROOT_PATH / 'config/config.yaml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(CONFIG, f)


def get_config_param(config_param_name: str) -> Any:
    """
    获取配置参数
    :param config_param_name: 配置参数的名称
    :return:配置参数的值
    """
    load_config()

    def find_in_nested_dict(dictionary, key):
        if key in dictionary:
            return dictionary[key]
        for k, v in dictionary.items():
            if isinstance(v, dict):
                item = find_in_nested_dict(v, key)
                if item is not None:
                    return item
        return None

    value = find_in_nested_dict(CONFIG, config_param_name)
    if value is None:
        raise KeyError(f'配置参数 "{config_param_name}" 在配置文件中不存在')

    return value


def write_config_param(config_param_name: str, value: Any) -> None:
    """
    修改配置参数
    :param config_param_name: 配置参数的名称
    :param value: 配置参数的值
    """
    load_config()

    def set_in_nested_dict(dictionary, key, value):
        if key in dictionary:
            dictionary[key] = value
            return
        for k, v in dictionary.items():
            if isinstance(v, dict):
                set_in_nested_dict(v, key, value)

    set_in_nested_dict(CONFIG, config_param_name, value)

    # 将修改后的CONFIG字典写回到config.yaml文件中
    config_path = ROOT_PATH / 'config/config.yaml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(CONFIG, f)


def set_log_level(level=None) -> None:
    """
    根据devmode的值设置日志级别
    :param level: 日志级别（仅调试）
    :return: None
    """
    devmode = get_config_param('DevMode')
    level_state = {
        'DEBUG': ['DE', 'DEBUG', 'BUG', 'D'],
        'INFO': ['INFO', 'INF', 'I'],
        'WARNING': ['WARNING', 'WARN', 'W'],
        'ERROR': ['ERROR', 'ERR', 'E'],
        'CRITICAL': ['CRITICAL', 'CRI', 'C']
    }
    if level is not None:
        level_upper = level.upper()
        for log_level, aliases in level_state.items():
            if level_upper in aliases:
                CONFIG['DevOptions']['LogLevel'] = log_level
                break
    else:
        if devmode:
            CONFIG['DevOptions']['LogLevel'] = 'DEBUG'
        else:
            CONFIG['DevOptions']['LogLevel'] = 'INFO'

    # 将修改后的CONFIG字典写回到config.yaml文件中
    write_config_param('LogLevel', CONFIG['DevOptions']['LogLevel'])


load_config()
fix_boolean_values(CONFIG)
set_log_level()


if __name__ == '__main__':
    # 测试代码
    load_config()
    print(CONFIG)
    write_config_param('DevMode', 'Ture')
    load_config()
    print(CONFIG)
    write_config_param('DevMode', 'fasle')
    load_config()
    print(CONFIG)
