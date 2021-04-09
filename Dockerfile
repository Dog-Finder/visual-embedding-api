FROM public.ecr.aws/lambda/python:3.8

RUN yum -y install tar gzip zlib && yum clean all

# Copy the earlier created requirements.txt file to the container
COPY requirements.txt ./

# Install the python requirements from requirements.txt
RUN python3.8 -m pip install -r requirements.txt

COPY src/ ./

# Download ResNet50 and store it in a directory
# RUN mkdir model
# RUN curl -L https://tfhub.dev/google/imagenet/inception_resnet_v2/feature_vector/4?tf-hub-format=compressed -o ./model/resnet.tar.gz
# RUN tar -xf model/resnet.tar.gz -C model/ && rm -r model/resnet.tar.gz


# You can overwrite command in `serverless.yml` template
CMD ["app.hello"]
