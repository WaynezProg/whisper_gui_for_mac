#!/usr/bin/env python3
"""
Configuration check tool / 配置檢查工具

Run this script to check if configuration is properly set / 執行此腳本來檢查配置是否正確設定
"""

from config import config

def main():
    """
    Main function for configuration check / 配置檢查的主函數
    
    Returns:
        int: 0 if configuration is valid, 1 if errors found / 配置正確返回 0，發現錯誤返回 1
    """
    print("=" * 60)
    print("配置檢查工具")
    print("=" * 60)
    print()
    
    # Print current configuration / 印出當前配置
    config.print_config()
    print()
    
    # Validate configuration / 驗證配置
    errors = config.validate()
    
    if errors:
        print("❌ 發現以下問題：")
        print()
        for error in errors:
            print(error)
            print()
        print("💡 解決方案：")
        print("1. 檢查環境變數是否正確設定")
        print("2. 檢查 .env 檔案是否存在且格式正確")
        print("3. 檢查 config.py 中的預設值")
        print("4. 詳見 docs/CONFIGURATION.md")
        return 1
    else:
        print("✅ 配置檢查通過！")
        return 0

if __name__ == "__main__":
    exit(main())

