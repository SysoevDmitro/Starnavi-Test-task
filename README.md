# Starnavi-Test-task
This is test task for Starnavi company
## Features
- **JWT Authentication**
- **Post CRUD**
- **Comments CRUD**
- **Daily breakdown**
- **AI replyes**
- **Profanity check**
```bash
git clone https://github.com/SysoevDmitro/Starnavi-Test-task.git
cd Starnavi-Test-task
```
## Run with Docker
Docker must be already installed

Copy .env-sample to .env and fill with all required data.

```shell 
docker-compose build
docker-compose up
```
### Documentation for endpoints
`/api/docs#/`
### Firstly
go to `/api/auth/login/` and get access token then paste it to Authorize header

## Run Tests
run in docker terminal
```shell 
python manage.py test
```
