# 在这里，您可以通过 ‘args’  获取节点中的输入变量，并通过 'ret' 输出结果
# 'args' 和 'ret' 已经被正确地注入到环境中
# 下面是一个示例，首先获取节点的全部输入参数params，其次获取其中参数名为‘input’的值：
# params = args.params; 
# input = params.input;
# 下面是一个示例，输出一个包含多种数据类型的 'ret' 对象：
# ret: Output =  { "name": ‘小明’, "hobbies": [“看书”, “旅游”] };

import requests_async as requests
import json

async def main(args: Args) -> Output:
    params = args.params
    url = params.get('url', '')  # 获取博客URL
    formats = params.get('formats', ['html'])  # 获取需要的格式

    # API endpoint
    API_URL = "https://api.blog-keeper.com"
    api_url = API_URL + "/parse"
    request_data = {
        "url": url,
        "formats": formats,
        "fileContent": "true",
    }

    try:
        
        response = await requests.post(
            api_url,
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        
        # 直接尝试解析响应内容
        if isinstance(response, str):
            result = json.loads(response)
        else:
            result = json.loads(response.content)
        
        # 处理返回的列表，获取第一个结果
        if result and isinstance(result, list):
            first_result = result[0]
            return {
                "success": True,
                "files": API_URL + first_result['download_url'],
                "title": first_result['title'],
                "message": f"解析成功：{first_result['title']}",
                "file_content": first_result['file_content']
            }
        else:
            return {
                "success": False,
                "files": "",
                "message": "未获取到解析结果"
            }
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP请求失败: {e.response.status_code} - {e.response.reason}"
        return {
            "success": False,
            "files": "",
            "message": error_msg
        }
    except requests.exceptions.ConnectionError as e:
        error_msg = f"网络连接错误: {str(e)}"
        return {
            "success": False,
            "files": "",
            "message": error_msg
        }
    except json.JSONDecodeError as e:
        error_msg = f"JSON解析错误: {str(e)}"
        return {
            "success": False,
            "files": "",
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"发生未知错误: {str(e)}"
        return {
            "success": False,
            "files": "",
            "message": error_msg
        }