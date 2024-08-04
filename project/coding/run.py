import subprocess
import os

try:
    script_path = r'coding\task.py'
    data_path= r'coding\data.py'
    # 執行 task.py 腳本
    result = subprocess.run(['python', script_path],
                            capture_output=True, text=True, shell=True)
    
    # 檢查執行結果
    if result.returncode == 0:
        print("task.py executed successfully.")
        print(result.stdout)
    else:
        print("task.py execution failed.")
        print(result.stderr)
        
except subprocess.CalledProcessError as e:
    print(f"task.py execution failed: {e}")
finally:
    # 刪除 task.py 檔案
    try:
        os.remove(script_path)
        os.remove(data_path)
        print("task.py file deleted successfully.")
    except OSError as e:
        print(f"Error deleting task.py file: {e}")
