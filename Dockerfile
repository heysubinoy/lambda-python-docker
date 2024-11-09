# Use an official Python base image
FROM public.ecr.aws/lambda/python:3.9

# Install necessary dependencies
RUN yum -y install curl unzip
# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip

RUN yum -y update && \
    yum -y install wget bash && \
    yum clean all

# Install Miniconda
RUN mkdir -p ${LAMBDA_TASK_ROOT}/miniconda3 && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ${LAMBDA_TASK_ROOT}/miniconda3/miniconda.sh && \
    bash ${LAMBDA_TASK_ROOT}/miniconda3/miniconda.sh -b -u -p ${LAMBDA_TASK_ROOT}/miniconda3 && \
    rm ${LAMBDA_TASK_ROOT}/miniconda3/miniconda.sh


ENV PATH=${LAMBDA_TASK_ROOT}/miniconda3/bin:$PATH

RUN conda update sqlite
RUN conda install -c conda-forge libgdal=3.6


RUN conda --version
RUN conda list gdal 
RUN find ${LAMBDA_TASK_ROOT}/miniconda3/ -name gdal_translate



RUN gdal_translate --version
RUN conda install -c conda-forge proj

ENV CPL_VSIL_USE_TEMP_FILE_FOR_RANDOM_WRITE=YES
COPY . ${LAMBDA_TASK_ROOT}
RUN rm -rf awscliv2.zip
# RUN rm /root/miniconda3/miniconda.sh
RUN pip install boto3
RUN conda clean -a -y
RUN chmod 755 ${LAMBDA_TASK_ROOT}/miniconda3/bin/gdal_translate
ENV PROJ_LIB=${LAMBDA_TASK_ROOT}/miniconda3/share/proj
# Expose the port (if you have a server running inside, or not needed here)
EXPOSE 8080

# Set the entry point to run the Python app
CMD ["app.handler"]