build:
	docker build -t visual-embedding-api-dev .
	docker tag visual-embedding-api-dev:latest 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search

push:
	docker push 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search | export DIGGEST="$(ggrep -oP '(?<=digest: )[^ ]+')" 

local:
	docker run -p 9000:8080 visual-embedding-api-dev:latest $(handler)

ping:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
