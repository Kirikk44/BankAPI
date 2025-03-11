import uvicorn
from fastapi import FastAPI, Request

from database import *
from routers.v1 import abs as abs_v1
from routers.v1 import auth as auth_v1
from routers.v1 import dbo as dbo_v1
from routers.v1 import sm as sm_v1
##
app = FastAPI()

app.include_router(dbo_v1.router)
app.include_router(auth_v1.router)
app.include_router(abs_v1.router)
app.include_router(sm_v1.router)


@app.get('/list_endpoints/')
def list_endpoints(request: Request):
    url_list = [
        {'path': route.path, 'name': route.name}
        for route in request.app.routes
    ]
    return url_list


if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8082)
