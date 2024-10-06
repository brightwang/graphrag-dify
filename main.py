# 导入FastAPI
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import pandas as pd
from pydantic import BaseModel
from typing import Union

import tiktoken
from graphrag.index.create_pipeline_config import create_pipeline_config
import graphrag.query.api as api
from graphrag.query.indexer_adapters import read_indexer_reports, read_indexer_text_units
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext
from graphrag.query.structured_search.local_search.search import LocalSearch
import utils
from pathlib import Path
import uvicorn
from graphrag.query.llm.oai import ChatOpenAI, OpenAIEmbedding
from graphrag.query.llm.base import BaseLLM
from graphrag.config import (
    GraphRagConfig,
    load_config,
    resolve_paths,
)
from graphrag.utils.storage import _create_storage, _load_table_from_storage


class SearchQuery(BaseModel):
    active_docs: str
    query: str


async def _resolve_parquet_files(
    root_dir: str,
    config: GraphRagConfig,
    parquet_list: list[str],
    optional_list: list[str],
) -> dict[str, pd.DataFrame]:
    """Read parquet files to a dataframe dict."""
    dataframe_dict = {}
    pipeline_config = create_pipeline_config(config)
    storage_obj = _create_storage(root_dir=root_dir,
                                  config=pipeline_config.storage)
    for parquet_file in parquet_list:
        df_key = parquet_file.split(".")[0]
        df_value = await _load_table_from_storage(name=parquet_file,
                                                  storage=storage_obj)
        dataframe_dict[df_key] = df_value

    # for optional parquet files, set the dict entry to None instead of erroring out if it does not exist
    for optional_file in optional_list:
        file_exists = await storage_obj.has(optional_file)
        df_key = optional_file.split(".")[0]
        if file_exists:
            df_value = await _load_table_from_storage(name=optional_file,
                                                      storage=storage_obj)
            dataframe_dict[df_key] = df_value
        else:
            dataframe_dict[df_key] = None

    return dataframe_dict


token_encoder = tiktoken.get_encoding("cl100k_base")

# 创建FastAPI实例
app = FastAPI()


# 定义一个GET请求的路由
@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/v1/search")
async def search(search_query: SearchQuery):
    print(search_query)
    root_dir = f"./indexs/{search_query.active_docs}"
    root = Path(root_dir).resolve()
    config = load_config(root, None)
    resolve_paths(config)
    community_level = 2
    response_type = "search_prompt"
    dataframe_dict = await _resolve_parquet_files(
        root_dir=root_dir,
        config=config,
        parquet_list=[
            "create_final_nodes.parquet",
            "create_final_community_reports.parquet",
            "create_final_text_units.parquet",
            "create_final_relationships.parquet",
            "create_final_entities.parquet",
        ],
        optional_list=["create_final_covariates.parquet"],
    )
    final_nodes: pd.DataFrame = dataframe_dict["create_final_nodes"]
    final_community_reports: pd.DataFrame = dataframe_dict[
        "create_final_community_reports"]
    final_text_units: pd.DataFrame = dataframe_dict["create_final_text_units"]
    final_relationships: pd.DataFrame = dataframe_dict[
        "create_final_relationships"]
    final_entities: pd.DataFrame = dataframe_dict["create_final_entities"]
    final_covariates: pd.DataFrame | None = dataframe_dict[
        "create_final_covariates"]
    result, context_data = await api.local_search(
        config=config,
        nodes=final_nodes,
        entities=final_entities,
        community_reports=final_community_reports,
        text_units=final_text_units,
        relationships=final_relationships,
        covariates=final_covariates,
        community_level=community_level,
        response_type=response_type,
        query=search_query.query,
    )
    return {"result": result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
