FROM public.ecr.aws/lambda/python:3.8

# Copy the earlier created requirements.txt file to the container
COPY requirements.txt ./

# Install the python requirements from requirements.txt
RUN python3.8 -m pip install -r requirements.txt

COPY app.py ./

# You can overwrite command in `serverless.yml` template
CMD ["app.hello"]
