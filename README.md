# graphrag-dify
本视频时AI带路党Pro为分享视频准备[可能是第一个分享GraphRAG结合Dify使用的教程-GraphRAG实战教程2
](https://www.bilibili.com/video/BV1ud1iY3Em1)
将graphrag暴露为http服务给dify使用

**注意:本仓库代码需要和graphrag源码放一起**

### release log
2024.12.11更新
支持官方v0.9.0版本
### 签出官方源码

```bash
# clone代码
git clone https://github.com/microsoft/graphrag.git 
# 进入目录
cd graphrag
# 切换为v0.9.0版本
git checkout v0.9.0
```

### 准备工作

pyproject.toml中添加依赖包，并执行poetry install
```
fastapi = "^0.115.0"
uvicorn = "^0.31.0"
asyncio = "^3.4.3"
utils = "^1.0.2"
```
### 文件存放位置
- main.py 存放于grpahrag项目源码跟目录
- search.py和search_prompt.py按照仓库中的目录位置覆盖graphrag的源文件
- 将已经生成的索引存放于根目录下indexs目录中

### 测试

- response type中增加了search_prompt参数，大家可以参考官方命令，测试是否能够正常运行

### 启动graphrag service
> poetry shell
> 
> uvicorn main:app --reload --host 0.0.0.0 --port 8000
### dify dsl导入
将dify的两个dsl导入，并重新把工作流发布为工具，并在agent中重新引用，具体可以参考视频
