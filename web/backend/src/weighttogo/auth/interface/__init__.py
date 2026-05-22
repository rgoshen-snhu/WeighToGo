"""Interface layer for the auth bounded context.

Contains FastAPI routers, request/response Pydantic schemas, and dependency
injection wiring. This layer is the outermost ring and may import FastAPI,
Starlette, and Pydantic.
"""
