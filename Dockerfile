FROM python:3.9

#initialize working directory 
WORKDIR /app

#copy the current directory inside the container
COPY . /app/

#install requirements.txt
RUN  pip install -r requirements.txt


# copy the application code tot the working directoyr 
COPY  . . 



#expose the application code to the working directory 
EXPOSE 8000