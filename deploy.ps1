docker build -t covitter -f Dockerfile .

heroku container:push web -a covitter

heroku container:release web -a covitter
