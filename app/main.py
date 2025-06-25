from routes import scheduler_route
from version import __version__
from fastapi import FastAPI


app = FastAPI(
    title="Distributed Task Scheduler",
    version=__version__,
    contact={
        "name": "Diogo Bastos",
        "url": "https://github.com/BastosDiogo",
        "email": "bmnetto.diogo@gmail.com",
    }
)

app.include_router(scheduler_route.router)