# COVITTER ANALYSIS

Covitter Analysis is a COVID-19 analysis application on Twitter posts. It uses a stream of posts about COVID-19 collected at 10 minute intervals. On the application, analysis on sentiment, entity linking and co-occurancies are presented. 

You can access the application from https://covitter.herokuapp.com.


You may find the detailed documentation here.


The application is readily available [here](https://covitter.herokuapp.com) and the source code can be cloned from this repository. To use the system there are certain accounts one has to get. They are;
-	Twitter developer account
-	TagMe account
-	News API account
-	A database url that contains the data explained the “System Design” section of the [project documentation](https://github.com/melisMirza/SWE573_project/blob/main/Covitter_ProjectReport.pdf) in the repository.


An .env file has to be created by filling the values in the .env-sample file in the repository. It is placed at the root of the repository with (or in place of) the sample file. After obtaining all environment variables, there are two ways to run and customize the code. 

### Using pipenv

**1.**	Install Python 3

**2.**	Install pipenv by: `pip install pipenv`

**3.**	Go to applications root directory: `cd SWE573_project`

**4.**	Run `pipenv install` . This will install every dependency declared in the *requirements.txt* file.

**5.**	After the virtual environment is created, go to it by; `pipenv shell` 

**6.**	Run the application by; `python manage.py runserver 0.0.0.0:8000` (for Windows) or `gunicorn CovitterAnalysis.wsgi:application --bind 0.0.0.0:8000` (for Mac)

**7.**	Go to the *localhost:8000* to view the application. 


### Using Docker

As the application is dockerized, an image can be built and ran, by the following steps.

**1.**	Build image; `docker build -t covitter -f Dockerfile.local .` (this is for local use, for deployment use Dockerfile instead)

**2.**	Run; `docker run -it -p 8000:8000 --env-file=.env covitter` (--env-file is optional, add that if the application fails to read environment variables)

**3.**	Go to the *localhost:8000* to view the application. 
