build:
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	docker build -t visual-embedding-api-dev .
	docker tag visual-embedding-api-dev:latest 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search

deploy:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search
	docker push 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search
	sls deploy

local:
	docker run -p 9000:8080 visual-embedding-api-dev:latest $(handler)

ping:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
