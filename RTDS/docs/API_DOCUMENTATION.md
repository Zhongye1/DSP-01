# MinerU 解析服务 API 文档

## 概述

MinerU 解析服务提供文档解析功能，支持 PDF、DOC、PPT、图片等多种格式文件的解析，并将内容转换为 Markdown 或 JSON 格式。

### 注意事项

- 单个文件大小不能超过 200MB，文件页数不超过 600 页
- 每个账号每天享有 2000 页最高优先级解析额度，超过部分优先级降低
- 因网络限制，GitHub、AWS 等国外 URL 可能会请求超时
- 该接口不支持文件直接上传
- Header 头中需要包含 Authorization 字段，格式为 `Bearer + 空格 + Token`

## 认证方式

所有 API 请求都需要在 Header 中包含认证信息：

```
Authorization: Bearer YOUR_API_TOKEN
```

## 单个文件解析

### 创建解析任务

#### 请求信息

- **URL**: `https://mineru.net/api/v4/extract/task`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求体参数

| 参数            | 类型     | 是否必选 | 示例                                                    | 描述                                                                                          |
| --------------- | -------- | -------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| url             | string   | 是       | https://static.openxlab.org.cn/opendatalab/pdf/demo.pdf | 文件 URL，支持 .pdf、.doc、.docx、.ppt、.pptx、.png、.jpg、.jpeg、.html 多种格式              |
| is_ocr          | bool     | 否       | false                                                   | 是否启动 OCR 功能，默认 false，仅对 pipeline、vlm 模型有效                                    |
| enable_formula  | bool     | 否       | true                                                    | 是否开启公式识别，默认 true，仅对 pipeline、vlm 模型有效。对于 vlm 模型，只影响行内公式的解析 |
| enable_table    | bool     | 否       | true                                                    | 是否开启表格识别，默认 true，仅对 pipeline、vlm 模型有效                                      |
| language        | string   | 否       | ch                                                      | 指定文档语言，默认 ch，其他可选值详见 PaddleOCR 语言列表，仅对 pipeline、vlm 模型有效         |
| data_id         | string   | 否       | abc\*\*                                                 | 解析对象对应的数据 ID                                                                         |
| callback        | string   | 否       | http://127.0.0.1/callback                               | 解析结果回调通知 URL                                                                          |
| seed            | string   | 否       | abc\*\*                                                 | 随机字符串，该值用于回调通知请求中的签名                                                      |
| extra_formats   | [string] | 否       | ["docx","html"]                                         | 支持 docx、html、latex 三种格式中的一个或多个，markdown、json 为默认导出格式                  |
| page_ranges     | string   | 否       | 1-600                                                   | 指定页码范围，格式为逗号分隔的字符串                                                          |
| model_version   | string   | 否       | vlm                                                     | mineru 模型版本，可选值：pipeline、vlm、MinerU-HTML                                           |
| no_cache        | bool     | 否       | false                                                   | 是否绕过缓存，默认 false                                                                      |
| cache_tolerance | int      | 否       | 900                                                     | 缓存容忍时间（秒），默认 900（15分钟）                                                        |

#### Python 示例代码

```python
import requests

token = "官网申请的api token"
url = "https://mineru.net/api/v4/extract/task"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
data = {
    "url": "https://cdn-mineru.openxlab.org.cn/demo/example.pdf",
    "model_version": "vlm"
}

res = requests.post(url, headers=header, json=data)
print(res.status_code)
print(res.json())
print(res.json()["data"])
```

#### 响应参数

| 参数         | 类型   | 示例                             | 说明                            |
| ------------ | ------ | -------------------------------- | ------------------------------- |
| code         | int    | 0                                | 接口状态码，成功：0             |
| msg          | string | ok                               | 接口处理信息，成功："ok"        |
| trace_id     | string | c876cd60b202f2396de1f9e39a1b0172 | 请求 ID                         |
| data.task_id | string | a90e6ab6-44f3-4554-b4\*\*\*      | 提取任务 id，可用于查询任务结果 |

#### 响应示例

```json
{
    "code": 0,
    "data": {
        "task_id": "a90e6ab6-44f3-4554-b4***"
    },
    "msg": "ok",
    "trace_id": "c876cd60b202f2396de1f9e39a1b0172"
}
```

### 获取任务结果

#### 请求信息

- **URL**: `https://mineru.net/api/v4/extract/task/{task_id}`
- **方法**: `GET`

#### Python 示例代码

```python
import requests

token = "官网申请的api token"
url = f"https://mineru.net/api/v4/extract/task/{task_id}"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

res = requests.get(url, headers=header)
print(res.status_code)
print(res.json())
print(res.json()["data"])
```

#### 响应参数

| 参数                                  | 类型   | 示例                                                                            | 说明                                                                                                  |
| ------------------------------------- | ------ | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| code                                  | int    | 0                                                                               | 接口状态码，成功：0                                                                                   |
| msg                                   | string | ok                                                                              | 接口处理信息，成功："ok"                                                                              |
| trace_id                              | string | c876cd60b202f2396de1f9e39a1b0172                                                | 请求 ID                                                                                               |
| data.task_id                          | string | abc\*\*                                                                         | 任务 ID                                                                                               |
| data.data_id                          | string | abc\*\*                                                                         | 解析对象对应的数据 ID                                                                                 |
| data.state                            | string | done                                                                            | 任务处理状态，完成:done，pending: 排队中，running: 正在解析，failed：解析失败，converting：格式转换中 |
| data.full_zip_url                     | string | https://cdn-mineru.openxlab.org.cn/pdf/018e53ad-d4f1-475d-b380-36bf24db9914.zip | 文件解析结果压缩包                                                                                    |
| data.err_msg                          | string | 文件格式不支持，请上传符合要求的文件类型                                        | 解析失败原因，当 state=failed 时有效                                                                  |
| data.extract_progress.extracted_pages | int    | 1                                                                               | 文档已解析页数，当state=running时有效                                                                 |
| data.extract_progress.start_time      | string | 2025-01-20 11:43:20                                                             | 文档解析开始时间，当state=running时有效                                                               |
| data.extract_progress.total_pages     | int    | 2                                                                               | 文档总页数，当state=running时有效                                                                     |

## 批量文件解析

### 文件批量上传解析

#### 请求信息

- **URL**: `https://mineru.net/api/v4/file-urls/batch`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求体参数

| 参数             | 类型     | 是否必选 | 示例                      | 描述                                                                           |
| ---------------- | -------- | -------- | ------------------------- | ------------------------------------------------------------------------------ |
| enable_formula   | bool     | 否       | true                      | 是否开启公式识别，默认 true，仅对 pipeline、vlm 模型有效                       |
| enable_table     | bool     | 否       | true                      | 是否开启表格识别，默认 true，仅对 pipeline、vlm 模型有效                       |
| language         | string   | 否       | ch                        | 指定文档语言，默认 ch，仅对 pipeline、vlm 模型有效                             |
| file.name        | string   | 是       | demo.pdf                  | 文件名，支持 .pdf、.doc、.docx、.ppt、.pptx、.png、.jpg、.jpeg、.html 多种格式 |
| file.is_ocr      | bool     | 否       | true                      | 是否启动 OCR 功能，默认 false，仅对 pipeline、vlm 模型有效                     |
| file.data_id     | string   | 否       | abc\*\*                   | 解析对象对应的数据 ID                                                          |
| file.page_ranges | string   | 否       | 1-600                     | 指定页码范围                                                                   |
| callback         | string   | 否       | http://127.0.0.1/callback | 解析结果回调通知 URL                                                           |
| seed             | string   | 否       | abc\*\*                   | 随机字符串，用于回调通知请求中的签名                                           |
| extra_formats    | [string] | 否       | ["docx","html"]           | 支持 docx、html、latex 三种格式中的一个或多个                                  |
| model_version    | string   | 否       | vlm                       | mineru 模型版本                                                                |

#### Python 示例代码

```python
import requests

token = "官网申请的api token"
url = "https://mineru.net/api/v4/file-urls/batch"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
data = {
    "files": [
        {"name":"demo.pdf", "data_id": "abcd"}
    ],
    "model_version":"vlm"
}
file_path = ["demo.pdf"]
try:
    response = requests.post(url, headers=header, json=data)
    if response.status_code == 200:
        result = response.json()
        print('response success. result:{}'.format(result))
        if result["code"] == 0:
            batch_id = result["data"]["batch_id"]
            urls = result["data"]["file_urls"]
            print('batch_id:{},urls:{}'.format(batch_id, urls))
            for i in range(0, len(urls)):
                with open(file_path[i], 'rb') as f:
                    res_upload = requests.put(urls[i], data=f)
                    if res_upload.status_code == 200:
                        print(f"{urls[i]} upload success")
                    else:
                        print(f"{urls[i]} upload failed")
        else:
            print('apply upload url failed,reason:{}'.format(result.msg))
    else:
        print('response not success. status:{} ,result:{}'.format(response.status_code, response))
except Exception as err:
    print(err)
```

#### 响应参数

| 参数          | 类型     | 示例                                                            | 说明                                    |
| ------------- | -------- | --------------------------------------------------------------- | --------------------------------------- |
| code          | int      | 0                                                               | 接口状态码，成功：0                     |
| msg           | string   | ok                                                              | 接口处理信息，成功："ok"                |
| trace_id      | string   | c876cd60b202f2396de1f9e39a1b0172                                | 请求 ID                                 |
| data.batch_id | string   | 2bb2f0ec-a336-4a0a-b61a-\*\*\*\*                                | 批量提取任务 id，可用于批量查询解析结果 |
| data.files    | [string] | ["https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/****"] | 文件上传链接                            |

### URL 批量上传解析

#### 请求信息

- **URL**: `https://mineru.net/api/v4/extract/task/batch`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求体参数

| 参数             | 类型     | 是否必选 | 示例                      | 描述                                                                             |
| ---------------- | -------- | -------- | ------------------------- | -------------------------------------------------------------------------------- |
| enable_formula   | bool     | 否       | true                      | 是否开启公式识别，默认 true，仅对 pipeline、vlm 模型有效                         |
| enable_table     | bool     | 否       | true                      | 是否开启表格识别，默认 true，仅对 pipeline、vlm 模型有效                         |
| language         | string   | 否       | ch                        | 指定文档语言，默认 ch，仅对 pipeline、vlm 模型有效                               |
| file.url         | string   | 是       | demo.pdf                  | 文件链接，支持 .pdf、.doc、.docx、.ppt、.pptx、.png、.jpg、.jpeg、.html 多种格式 |
| file.is_ocr      | bool     | 否       | true                      | 是否启动 OCR 功能，默认 false，仅对 pipeline、vlm 模型有效                       |
| file.data_id     | string   | 否       | abc\*\*                   | 解析对象对应的数据 ID                                                            |
| file.page_ranges | string   | 否       | 1-600                     | 指定页码范围                                                                     |
| callback         | string   | 否       | http://127.0.0.1/callback | 解析结果回调通知 URL                                                             |
| seed             | string   | 否       | abc\*\*                   | 随机字符串，用于回调通知请求中的签名                                             |
| extra_formats    | [string] | 否       | ["docx","html"]           | 支持 docx、html、latex 三种格式中的一个或多个                                    |
| model_version    | string   | 否       | vlm                       | mineru 模型版本                                                                  |
| no_cache         | bool     | 否       | false                     | 是否绕过缓存，默认 false                                                         |
| cache_tolerance  | int      | 否       | 900                       | 缓存容忍时间（秒），默认 900（15分钟）                                           |

#### Python 示例代码

```python
import requests

token = "官网申请的api token"
url = "https://mineru.net/api/v4/extract/task/batch"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
data = {
    "files": [
        {"url":"https://cdn-mineru.openxlab.org.cn/demo/example.pdf", "data_id": "abcd"}
    ],
    "model_version": "vlm"
}
try:
    response = requests.post(url, headers=header, json=data)
    if response.status_code == 200:
        result = response.json()
        print('response success. result:{}'.format(result))
        if result["code"] == 0:
            batch_id = result["data"]["batch_id"]
            print('batch_id:{}'.format(batch_id))
        else:
            print('submit task failed,reason:{}'.format(result.msg))
    else:
        print('response not success. status:{} ,result:{}'.format(response.status_code, response))
except Exception as err:
    print(err)
```

### 批量获取任务结果

#### 请求信息

- **URL**: `https://mineru.net/api/v4/extract-results/batch/{batch_id}`
- **方法**: `GET`

#### Python 示例代码

```python
import requests

token = "官网申请的api token"
url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

res = requests.get(url, headers=header)
print(res.status_code)
print(res.json())
print(res.json()["data"])
```

#### 响应参数

| 参数                                                 | 类型   | 示例                                                                            | 说明                                                                                                                                                |
| ---------------------------------------------------- | ------ | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| code                                                 | int    | 0                                                                               | 接口状态码，成功：0                                                                                                                                 |
| msg                                                  | string | ok                                                                              | 接口处理信息，成功："ok"                                                                                                                            |
| trace_id                                             | string | c876cd60b202f2396de1f9e39a1b0172                                                | 请求 ID                                                                                                                                             |
| data.batch_id                                        | string | 2bb2f0ec-a336-4a0a-b61a-241afaf9cc87                                            | batch_id                                                                                                                                            |
| data.extract_result.file_name                        | string | demo.pdf                                                                        | 文件名                                                                                                                                              |
| data.extract_result.state                            | string | done                                                                            | 任务处理状态，完成:done，waiting-file: 等待文件上传排队提交解析任务中，pending: 排队中，running: 正在解析，failed：解析失败，converting：格式转换中 |
| data.extract_result.full_zip_url                     | string | https://cdn-mineru.openxlab.org.cn/pdf/018e53ad-d4f1-475d-b380-36bf24db9914.zip | 文件解析结果压缩包                                                                                                                                  |
| data.extract_result.err_msg                          | string | 文件格式不支持，请上传符合要求的文件类型                                        | 解析失败原因，当 state=failed 时有效                                                                                                                |
| data.extract_result.data_id                          | string | abc\*\*                                                                         | 解析对象对应的数据 ID                                                                                                                               |
| data.extract_result.extract_progress.extracted_pages | int    | 1                                                                               | 文档已解析页数，当state=running时有效                                                                                                               |
| data.extract_result.extract_progress.start_time      | string | 2025-01-20 11:43:20                                                             | 文档解析开始时间，当state=running时有效                                                                                                             |
| data.extract_result.extract_progress.total_pages     | int    | 2                                                                               | 文档总页数，当state=running时有效                                                                                                                   |

## 模型版本说明

- **pipeline**: 传统处理管道
- **vlm**: 视觉语言模型
- **MinerU-HTML**: 专门用于 HTML 文件解析

## 常见错误码

| 错误码 | 说明                          | 解决建议                                                                                                   |
| ------ | ----------------------------- | ---------------------------------------------------------------------------------------------------------- |
| A0202  | Token 错误                    | 检查 Token 是否正确，请检查是否有 Bearer 前缀 或者更换新 Token                                             |
| A0211  | Token 过期                    | 更换新 Token                                                                                               |
| -500   | 传参错误                      | 请确保参数类型及 Content-Type 正确                                                                         |
| -10001 | 服务异常                      | 请稍后再试                                                                                                 |
| -10002 | 请求参数错误                  | 检查请求参数格式                                                                                           |
| -60001 | 生成上传 URL 失败，请稍后再试 | 请稍后再试                                                                                                 |
| -60002 | 获取匹配的文件格式失败        | 检测文件类型失败，请求的文件名及链接中带有正确的后缀名，且文件为 pdf,doc,docx,ppt,pptx,png,jp(e)g 中的一种 |
| -60003 | 文件读取失败                  | 请检查文件是否损坏并重新上传                                                                               |
| -60004 | 空文件                        | 请上传有效文件                                                                                             |
| -60005 | 文件大小超出限制              | 检查文件大小，最大支持 200MB                                                                               |
| -60006 | 文件页数超过限制              | 请拆分文件后重试                                                                                           |
| -60007 | 模型服务暂时不可用            | 请稍后重试或联系技术支持                                                                                   |
| -60008 | 文件读取超时                  | 检查 URL 可访问                                                                                            |
| -60009 | 任务提交队列已满              | 请稍后再试                                                                                                 |
| -60010 | 解析失败                      | 请稍后再试                                                                                                 |
| -60011 | 获取有效文件失败              | 请确保文件已上传                                                                                           |
| -60012 | 找不到任务                    | 请确保 task_id 有效且未删除                                                                                |
| -60013 | 没有权限访问该任务            | 只能访问自己提交的任务                                                                                     |
| -60014 | 删除运行中的任务              | 运行中的任务暂不支持删除                                                                                   |
| -60015 | 文件转换失败                  | 可以手动转为 pdf 再上传                                                                                    |
| -60016 | 文件转换失败                  | 文件转换为指定格式失败，可以尝试其他格式导出或重试                                                         |
| -60017 | 重试次数达到上限              | 等后续模型升级后重试                                                                                       |
| -60018 | 每日解析任务数量已达上限      | 明日再来                                                                                                   |
| -60019 | html 文件解析额度不足         | 明日再来                                                                                                   |
| -60020 | 文件拆分失败                  | 请稍后重试                                                                                                 |
| -60021 | 读取文件页数失败              | 请稍后重试                                                                                                 |
| -60022 | 网页读取失败                  | 可能因网络问题或者限频导致读取失败，请稍后重试                                                             |

## 附录

### 页码范围格式说明

- `"2,4-6"`：表示选取第2页、第4页至第6页（包含4和6，结果为 [2,4,5,6]）
- `"2--2"`：表示从第2页一直选取到倒数第二页（其中"-2"表示倒数第二页）

### 回调机制说明

如果使用 callback 参数，回调接口必须支持：

- POST 方法
- UTF-8 编码
- Content-Type: application/json 传输数据
- 参数 checksum 和 content

其中：

- checksum：字符串格式，由用户 uid + seed + content 拼成字符串，通过 SHA256 算法生成
- content：JSON 字符串格式

接收成功返回 HTTP 状态码 200，否则会重复推送 5 次。
