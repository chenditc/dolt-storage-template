#!/bin/bash
dolt sql-server &

script_dir=$(dirname ${BASH_SOURCE[0]})

flask --app $script_dir/dolt_http_server run --host 0.0.0.0