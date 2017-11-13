# Setting up the app on Hasura

- Create a Hasura project (Let's say <project-name>)
- Login to the project console at console.<project-name>.hasura-app.io
- Import the project.json, or create your own tables based on the schema.json
    and add relationships
- Add data using the scraper python script( Make sure you run a `pip install -r
    requirements.txt` before you run the scraper)
- Install [hasuractl](https://docs.hasura.io/0.14/ref/cli/hasuractl.html)
- Login to hasuractl using `hasuractl login`
- Set up your hasura project using `hasuractl set-context <project-name>`
- Use the following command to set up a quickstart git push service

```bash
    $ hasuractl quickstart nodejs-express <app-name> --create
```

- Now cd into the <app-name> folder, delete the contents, copy this
    repositories contents into it and do a `git add . --all`,  `git commit -m "<message>"` and
    then deploy with 
```bash
    $ git push hasura master
```
