FROM numenta/nupic

MAINTAINER Basel Magableh

RUN apt-get update
RUN apt-get install nano 
RUN apt-get install docker.io -y 


RUN pip install --upgrade pip
RUN pip install --upgrade numpy

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
 

COPY /model-trainer /model-trainer
ENV TERM xterm
ENV NTA_CONF_PROP_nupic_cluster_database_passwd nupic
ENV NTA_CONF_PROP_nupic_cluster_database_host db
COPY nupic-default.xml /usr/local/src/nupic/src/nupic/support/nupic-default.xml

WORKDIR /model-trainer
CMD python main.py


