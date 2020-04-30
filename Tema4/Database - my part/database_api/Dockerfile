# Dockerfile
FROM python:3.7-stretch
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install apt-transport-https
############ ODBC 13 ##################
#RUN su
#RUN echo "deb [arch=amd64] https://apt-mo.trafficmanager.net/repos/mssql-ubuntu-xenial-release/ xenial main" > /etc/apt/sources.list.d/mssqlpreview.list
#RUN apt-key adv --keyserver apt-mo.trafficmanager.net --recv-keys 417A0893
#RUN apt-get update
#RUN ACCEPT_EULA=Y apt-get install -y libodbc1 unixodbc msodbcsql mssql-tools unixodbc-dev
#msodbcsql
#RUN apt-get install unixodbc-dev-utf16

#RUN su
#RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
##RUN echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/16.04/prod bionic main" | tee /etc/apt/sources.list.d/mssql-release.list
#RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
#RUN exit
#RUN apt-get update
#RUN ACCEPT_EULA=Y apt-get install -y libodbc1 unixodbc msodbcsql mssql-tools unixodbc-dev
##msodbcsql mssql-tools
#RUN apt-get install unixodbc-dev-utf16

############ ODBC 17 ##################
RUN su
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN exit
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
############
RUN apt-get install -y unixodbc-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["api-db.py"]