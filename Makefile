build:
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	docker build -t visual-embedding-api-${stage} .
	docker tag visual-embedding-api-${stage}:latest 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search-${stage}

deploy-build:
	docker build -t visual-embedding-api-${stage} .
	docker tag visual-embedding-api-${stage}:latest 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search-${stage}

deploy:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search-$(stage)
	docker push 983570756921.dkr.ecr.us-east-1.amazonaws.com/dog-finder-search-$(stage)
	sls deploy --stage $(stage)

local:
	docker run \
	-p 9000:8080 \
	-v "$$HOME/.aws":/root/.aws \
  -e AWS_REGION=us-east-1 \
	-e AWS_PROFILE=yoavnavon \
	visual-embedding-api-${stage}:latest $(handler)

ping:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
