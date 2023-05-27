#!/bin/bash
dolt sql-server &
flask --app dolt_http_server run --host 0.0.0.0