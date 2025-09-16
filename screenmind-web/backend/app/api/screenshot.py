"""
系统截屏API
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import tempfile
import os
import base64
import platform
import time
from ..core.logger import api_logger

router = APIRouter()

def take_screenshot_mac():
    """在Mac系统上截屏"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # 使用screencapture命令截屏整个屏幕
        # -x: 不播放截屏声音
        # -t png: 指定输出格式为PNG
        result = subprocess.run([
            'screencapture', '-x', '-t', 'png', temp_path
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            api_logger.error(f"Mac截屏失败: {result.stderr}")
            raise Exception(f"截屏命令执行失败: {result.stderr}")
        
        # 读取截屏文件
        with open(temp_path, 'rb') as f:
            image_data = f.read()
        
        # 清理临时文件
        os.unlink(temp_path)
        
        return image_data
        
    except subprocess.TimeoutExpired:
        api_logger.error("Mac截屏超时")
        raise Exception("截屏操作超时")
    except Exception as e:
        api_logger.error(f"Mac截屏异常: {str(e)}")
        raise Exception(f"截屏失败: {str(e)}")

def take_screenshot_windows():
    """在Windows系统上截屏"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # 使用PowerShell截屏
        powershell_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
        $bitmap.Save('{temp_path}', [System.Drawing.Imaging.ImageFormat]::Png)
        $graphics.Dispose()
        $bitmap.Dispose()
        """
        
        result = subprocess.run([
            'powershell', '-Command', powershell_script
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            api_logger.error(f"Windows截屏失败: {result.stderr}")
            raise Exception(f"截屏命令执行失败: {result.stderr}")
        
        # 读取截屏文件
        with open(temp_path, 'rb') as f:
            image_data = f.read()
        
        # 清理临时文件
        os.unlink(temp_path)
        
        return image_data
        
    except subprocess.TimeoutExpired:
        api_logger.error("Windows截屏超时")
        raise Exception("截屏操作超时")
    except Exception as e:
        api_logger.error(f"Windows截屏异常: {str(e)}")
        raise Exception(f"截屏失败: {str(e)}")

def take_screenshot_linux():
    """在Linux系统上截屏"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # 尝试使用gnome-screenshot
        try:
            result = subprocess.run([
                'gnome-screenshot', '-f', temp_path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                with open(temp_path, 'rb') as f:
                    image_data = f.read()
                os.unlink(temp_path)
                return image_data
        except FileNotFoundError:
            pass
        
        # 尝试使用scrot
        try:
            result = subprocess.run([
                'scrot', temp_path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                with open(temp_path, 'rb') as f:
                    image_data = f.read()
                os.unlink(temp_path)
                return image_data
        except FileNotFoundError:
            pass
        
        # 尝试使用import (ImageMagick)
        try:
            result = subprocess.run([
                'import', '-window', 'root', temp_path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                with open(temp_path, 'rb') as f:
                    image_data = f.read()
                os.unlink(temp_path)
                return image_data
        except FileNotFoundError:
            pass
        
        raise Exception("未找到可用的截屏工具，请安装 gnome-screenshot、scrot 或 ImageMagick")
        
    except subprocess.TimeoutExpired:
        api_logger.error("Linux截屏超时")
        raise Exception("截屏操作超时")
    except Exception as e:
        api_logger.error(f"Linux截屏异常: {str(e)}")
        raise Exception(f"截屏失败: {str(e)}")

@router.post("/screenshot")
async def take_screenshot():
    """
    系统级截屏API
    
    Returns:
        包含base64编码图片数据的JSON响应
    """
    start_time = time.time()
    api_logger.info("开始系统截屏...")
    
    try:
        # 检测操作系统
        system = platform.system().lower()
        api_logger.info(f"检测到操作系统: {system}")
        
        # 根据操作系统选择截屏方法
        if system == 'darwin':  # macOS
            image_data = take_screenshot_mac()
        elif system == 'windows':
            image_data = take_screenshot_windows()
        elif system == 'linux':
            image_data = take_screenshot_linux()
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的操作系统: {system}"
            )
        
        # 将图片数据转换为base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        api_logger.info(f"截屏完成，耗时: {duration}秒，图片大小: {len(image_data)} bytes")
        
        return JSONResponse(content={
            "success": True,
            "message": "截屏成功",
            "data": {
                "image": image_base64,
                "format": "png",
                "size": len(image_data),
                "timestamp": int(time.time()),
                "duration": duration
            }
        })
        
    except Exception as e:
        api_logger.error(f"截屏失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"截屏失败: {str(e)}"
        )

@router.get("/screenshot/test")
async def test_screenshot_capability():
    """
    测试当前系统的截屏能力
    
    Returns:
        系统截屏能力信息
    """
    system = platform.system().lower()
    capabilities = {
        "system": system,
        "supported": False,
        "tools": [],
        "message": ""
    }
    
    try:
        if system == 'darwin':  # macOS
            # 检查screencapture命令
            result = subprocess.run(['which', 'screencapture'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                capabilities["supported"] = True
                capabilities["tools"].append("screencapture")
                capabilities["message"] = "macOS原生截屏支持"
            else:
                capabilities["message"] = "未找到screencapture命令"
                
        elif system == 'windows':
            capabilities["supported"] = True
            capabilities["tools"].append("powershell")
            capabilities["message"] = "Windows PowerShell截屏支持"
            
        elif system == 'linux':
            # 检查各种Linux截屏工具
            tools_to_check = ['gnome-screenshot', 'scrot', 'import']
            for tool in tools_to_check:
                result = subprocess.run(['which', tool], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    capabilities["tools"].append(tool)
            
            if capabilities["tools"]:
                capabilities["supported"] = True
                capabilities["message"] = f"找到截屏工具: {', '.join(capabilities['tools'])}"
            else:
                capabilities["message"] = "未找到可用的截屏工具"
        else:
            capabilities["message"] = f"不支持的操作系统: {system}"
            
    except Exception as e:
        capabilities["message"] = f"检测截屏能力时出错: {str(e)}"
    
    return JSONResponse(content=capabilities)