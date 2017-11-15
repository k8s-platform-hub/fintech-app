# Fintech Application with Hasura

This is a simple fin-tech application made using nodeJS and deployed on Hasura. Follow the following steps to get the app running.

1.  Get the project from the hub using

```
    hasura quickstart rishi/fintech-app
```

2. Modify your cluster name in the ``microservices/fintech/src/views/index.html``

```
  hasura.setProject('controllable78'); //Set your own cluster name in place of controllable78
```

3. Run these commands from the project directory to push this service to your cluster::

```
  $ git add .
  $ git commit -m "First commit"
  $ git push hasura master
```
4. Your app will be running at https://fintech.cluster-name.hasura-app.io
