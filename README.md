## Intro

This is a template to use dolt as a lightweight storage sidecar. 

We can build a docker from this template, run the docker as a sidecar for our workload. Once we are done with processing, we can push the data to dolt remote. So that we get:
1. Persist. We will store our data on dolt remote.
2. Concurrent operation. Each docker can work on their own and merge during dolt push and dolt pull.
3. Price efficient. No online service needed for this solution, each container sidecar is shortliving. 
4. Easy to inspect. We can inspect the content by cloning the data or run sql online on dolt hub.
5. SQL support. Dolt support SQL.
6. Easy to inject. We can inject data easily using dol sql and dolt push.
7. No cloud vender lock in. We can change the dolt remote to our private endpoint: https://www.dolthub.com/blog/2021-09-22-sql-remotes/, we can also run our own doltlab: https://docs.dolthub.com/guides/doltlab

**NOTE: The dolt project need to have at least one table to be able to build.**

## Use this template

It's recommended to fork and **rename** this repo to some name meaningful for your use, so that github action can properly build docker image.

## Build

Build a docker for your repo, and maybe set a timezone you want:

```
docker build --build-arg DATABASE_NAME=<My dolt database name> \
    --build-arg DOLTHUB_USER=<My dolt username> \
    --build-arg TIMEZONE=<Timezone, default to UTC> \
    -t dolt-storage .
```

Example:

```
docker build --build-arg DATABASE_NAME=trading_record \
    --build-arg DOLTHUB_USER=chenditc \
    --build-arg TIMEZONE=Asia/Shanghai \
    -t dolt-storage .
```

Or you can leverage the github action by setting `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` credential in the forked project. Also change the "build-args" in the workflow to pass your arguments.
Then you can trigger a build by creating a tag starting with "v", eg "v1.0.0"

## Use as mysql server

Run your docker and use dolt cli, pass credential in using environment variable:

```
docker run -e CREDS_KEY=xxxx \
   -e CREDS_VALUE='{"d":"xxxxx","x":"xxx","kty":"OKP","crv":"Ed25519"}' \
   --rm -it  dolt-storage dolt sql
```

You can generate dolt credential key and value from dolt cli:

```
$ dolt creds new
Credentials created successfully.
pub key: df2vvkm6t90o7k7u8cmg9jovq8nta032fu4neq2sr594initqrl0
$ cat /.dolt/.dolt/creds/n0q6a6qdff51ifsigj7ugber3tmh8dj2bjt8d86kp7d42.jwk       
{"d":"a8X_0sbqQYPQ_kMtBM8f0i_VAGJ_iXdoXNlSSV5d1uo=","x":"cyAGlzUmWpaLgHtC6uV8OxrdqCTZVeTkYcolLmhe2_Vrxf_SxupBg9D-Qy0Ezx_SL9UAYn-Jd2hc2VJJXl3W6g==","kty":"OKP","crv":"Ed25519"}
```

## Use as http server

The default auth token is same as the DBNAME.

Start docker and export port 5000
```
docker run -e CREDS_KEY=xxxx \
   -p 5000:5000
   -e CREDS_VALUE='{"d":"xxxxx","x":"xxx","kty":"OKP","crv":"Ed25519"}' \
   --rm -it  dolt-storage dolt sql
```

Use http request to operate database. See file [dolt_http_server.py](dolt_http_server.py)
