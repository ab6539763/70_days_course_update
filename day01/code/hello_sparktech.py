# -*- coding: utf-8 -*-
"""
星火科技 · 培训 Day 1
文件：hello_sparktech.py
说明：环境验证脚本 —— 确认 Python 解释器、编码与 print 正常。

使用方法：
    cd day01/code
    python3 hello_sparktech.py

预期输出：
    - 星火科技欢迎语
    - 当前 Python 版本号
    - 中文 UTF-8 测试行

若本文件无法运行，请先完成讲义第二章环境搭建，不要继续后面的卡片作业。
"""

from __future__ import annotations

import platform
import sys
from datetime import datetime


def main() -> None:
    """
    程序入口。Day 6 会学习「为什么把逻辑放在 main 里」；
    Day 10 会学习 if __name__ == '__main__' 的作用。
    """
    # 使用多行字符串打印横幅，三引号保留换行格式
    banner = """
╔══════════════════════════════════════════════════╗
║           星火科技 · 大模型应用开发培训           ║
║                  Day 1 环境自检                   ║
╚══════════════════════════════════════════════════╝
"""
    print(banner)

    # sys.version 返回完整版本信息字符串，适合写入日志
    print(f"[信息] Python 解释器版本：{sys.version}")

    # platform.python_version() 只取简短版本号，如 3.12.3
    print(f"[信息] 简短版本号：{platform.python_version()}")

    # 操作系统信息：交付时客户环境可能是 Linux，要提前习惯
    print(f"[信息] 运行平台：{platform.system()} {platform.release()}")

    # 中文编码测试：若此行乱码，请按讲义 2.2 节调整终端 UTF-8
    print("[测试] 中文显示正常：大模型应用开发")

    # 默认编码声明（Python 3 字符串为 Unicode，此处仅作教学展示）
    print(f"[信息] 标准输出编码：{sys.stdout.encoding}")

    # 当前时间：与 personal_info_card.py 使用相同的时间格式化方式
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[信息] 当前系统时间：{now_str}")

    print()
    print("✓ 环境自检完成。请继续学习 personal_info_card.py。")


# Python 脚本被「直接运行」时 __name__ 为 "__main__"
# 被其他文件 import 时 __name__ 为模块名，main() 不会自动执行
if __name__ == "__main__":
    main()
