import portalocker
from ruamel.yaml import YAML
from pathlib import Path
from typing import *
from log import logger


# 获取仓库的根目录
ROOT_PATH = Path(__file__).resolve().parent.parent
# 创建一个全局变量来存储配置
CONFIG: Dict = None
# 创建一个YAML对象
yaml = YAML()

fix_times = 0


def load_config() -> None:
    """
    读取配置文件
    :return: None
    """
    logger.debug('开始加载配置文件')
    global CONFIG
    if CONFIG is None:
        config_path = ROOT_PATH / 'config/config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            CONFIG = yaml.load(f)
            logger.debug('加载配置文件成功')
        fix_boolean_values(CONFIG)
        set_log_level()
    else:
        logger.debug('配置文件已经加载，无需重复加载')


def write_config_to_file() -> None:
    """
    将修改后的CONFIG字典写回到config.yaml文件中
    :return: None
    """
    logger.debug('开始写入配置文件')
    config_path = ROOT_PATH / 'config/config.yaml'
    with open(config_path, 'w', encoding='utf-8') as f:
        try:
            portalocker.lock(f, portalocker.LOCK_EX)  # 获取文件锁
            yaml.dump(CONFIG, f)
        except IOError as e:
            logger.error(f"写入配置文件时出错: {e}")
        finally:
            portalocker.unlock(f)  # 释放文件锁
            logger.debug('写入配置文件成功')


def get_config_param(config_param_name: str) -> Any:
    """
    获取配置参数
    :param config_param_name: 配置参数的名称
    :return:配置参数的值
    """
    logger.debug(f'开始获取配置参数 "{config_param_name}" 的值')
    load_config()

    def find_in_nested_dict(dictionary, key):
        lower_key = key.lower()
        lower_dict = {k.lower(): (k, v) for k, v in dictionary.items()}
        if lower_key in lower_dict:
            original_key, value = lower_dict[lower_key]
            return dictionary[original_key]
        for k, (original_key, v) in lower_dict.items():
            if isinstance(v, dict):
                item = find_in_nested_dict(v, lower_key)
                if item is not None:
                    return item
        return None

    value = find_in_nested_dict(CONFIG, config_param_name)
    if value is None:
        logger.error(f'配置参数 "{config_param_name}" 在配置文件中不存在')
        raise KeyError(f'配置参数 "{config_param_name}" 在配置文件中不存在')

    logger.debug(f'获取配置参数 "{config_param_name}" 的值为 {value}')
    return value


def write_config_param(config_param_name: str, value: Any) -> None:
    """
    修改配置参数
    :param config_param_name: 配置参数的名称
    :param value: 配置参数的值
    """
    logger.debug(f'开始修改配置参数 "{config_param_name}" 的值为 {value}')
    load_config()

    def set_in_nested_dict(dictionary, key, value):
        lower_key = key.lower()
        lower_dict = {k.lower(): (k, v) for k, v in dictionary.items()}
        if lower_key in lower_dict:
            original_key, _ = lower_dict[lower_key]
            dictionary[original_key] = value
            return
        for k, (original_key, v) in lower_dict.items():
            if isinstance(v, dict):
                set_in_nested_dict(v, key, value)

    set_in_nested_dict(CONFIG, config_param_name, value)
    logger.debug(f'修改配置参数 "{config_param_name}" 的值为 {value} 成功')
    # 将修改后的CONFIG字典写回到config.yaml文件中
    write_config_to_file()


def fix_boolean_values(dictionary: dict) -> None:
    """
    将config中错误格式的布尔值转换为正确的格式
    :param dictionary: 待处理的字典
    :return: None
    """
    logger.debug('开始修复布尔值')
    global fix_times
    fix_times += 1
    logger.debug(f'修复布尔值的次数: {fix_times}')
    # 创建一个列表，包含所有可能的布尔值的字符串表示
    true_values = ['ture', 'treu', 't', 'yes', 'y', '1']
    false_values = ['fasle', 'fales', 'flase', 'f', 'no', 'n', '0']
    # 创建一个标志，用于检查是否需要写入文件
    need_write = False
    for key, value in dictionary.items():
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower in true_values:
                dictionary[key] = True
                need_write = True
            elif value_lower in false_values:
                dictionary[key] = False
                need_write = True
        elif isinstance(value, dict):
            logger.debug(f'进入子字典: {key}')
            fix_boolean_values(value)

    # 将修改后的CONFIG字典写回到config.yaml文件中
    if need_write:
        write_config_to_file()
        logger.debug('修复布尔值成功')
    else:
        logger.debug('布尔值已经是正确的格式')


def set_log_level(level=None) -> None:
    """
    根据devmode的值设置日志级别
    :param level: 日志级别（仅调试）
    :return: None
    """
    logger.debug('开始设置日志级别')
    devmode = get_config_param('DevMode')
    level_state = {
        'DEBUG': ['DE', 'BUG', 'D'],
        'INFO': ['INF', 'I'],
        'WARNING': ['WARN', 'W'],
        'ERROR': ['ERR', 'E'],
        'CRITICAL': ['CRI', 'C']
    }
    need_write = False
    if level is not None:
        level_upper = level.upper()
        if level_upper in level_state:
            CONFIG['DevOptions']['LogLevel'] = level_upper
        else:
            for log_level, aliases in level_state.items():
                if level_upper in aliases:
                    CONFIG['DevOptions']['LogLevel'] = log_level
                    need_write = True
                    break
                else:
                    print(f"未知的日志级别: {level}")
    else:
        need_write = True
        if devmode:
            CONFIG['DevOptions']['LogLevel'] = 'DEBUG'
        else:
            CONFIG['DevOptions']['LogLevel'] = 'INFO'

    # 将修改后的CONFIG字典写回到config.yaml文件中
    if need_write:
        write_config_to_file()


load_config()


if __name__ == '__main__':
    # 测试代码
    load_config()
