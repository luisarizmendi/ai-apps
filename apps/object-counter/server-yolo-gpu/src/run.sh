#!/bin/bash

uvicorn object_detection_server:app --port ${PORT:=8000} --host ${HOST:=0.0.0.0}
