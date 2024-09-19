import logging
import azure.functions as func
from fastapi import FastAPI
from fastapi.routing import APIRoute
from main import app as fastapi_app

# FastAPI のアプリケーションを Azure Functions に統合
app = FastAPI()

# FastAPI のルートを Azure Functions に追加
for route in fastapi_app.routes:
    if isinstance(route, APIRoute):
        app.add_api_route(route.path, route.endpoint, methods=route.methods)

# Azure Functions 用の HTTP トリガー
async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.AsgiMiddleware(app)(req, context)
