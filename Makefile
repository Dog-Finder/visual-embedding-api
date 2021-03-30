build:
	docker build -t visual-embedding-api .

local:
	docker run -p 9000:8080 visual-embedding-api:latest $(handler)

ping:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
