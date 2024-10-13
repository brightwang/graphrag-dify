# graphrag-dify
本视频时AI带路党Pro为分享视频准备[可能是第一个分享GraphRAG结合Dify使用的教程-GraphRAG实战教程2
](https://www.bilibili.com/video/BV1ud1iY3Em1)
将graphrag暴露为http服务给dify使用
### 准备工作
本视频测试为0.3.6左右版本，最新版有变更
pyproject.toml中添加依赖包，并执行poetry install
```
fastapi = "^0.115.0"
uvicorn = "^0.31.0"
asyncio = "^3.4.3"
utils = "^1.0.2"
```
### 文件存放位置
- main.py 存放于项目跟目录
- search.py和search_prompt.py按照仓库中的目录位置覆盖graphrag的源文件
- 将已经生成的索引存放于根目录下indexs目录中

### 测试
大家可以参考如下命令，测试是否能够正常运行
> poetry run poe query --root ./indexs/wzry --method local --response_type search_prompt "项羽有什么技能"

### 启动graphrag service
> uvicorn main:app --reload --host 0.0.0.0 --port 8000
### dify dsl导入
将dify的两个dsl导入，并重新把工作流发布为工具，并在agent中重新引用，具体可以参考视频
