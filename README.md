# Small Python script to get the list of closed alerts in Opsgenie

![opsgenie_clean](/assets/opsgenie_cleaner_logo.png)

When you have a huge number and you can't delete from console web, because Opsgenie only allow you to select 25 (Default number) I have more than 35000 closed alerts and I don't want to delete it... OMG! But why you ... ? don't ask please historical reasons. :trollface:

# Technologies we’ll use:

* Docker version 4.8.2 (Windows)
* Python 3.8.10 (WSL2)

# Pre-requisites:

1º Generate API-KEY from OPSGENIE with sufficient permissions.

![api-key-opsgenie](/assets/generate_api_key_opsgenie.PNG)

# Deploy:

Download the repository, you will have the Dockerfile, in the same path execute the following commands:

```bash
docker build --no-cache --pull -t opsgenie_cleaner .   # Building the new image.

docker run -it -v "$(pwd)":/home/nroot/  --name opsgenie_cleaner  opsgenie_cleaner # Run the container with a volume.

python3 opsgenie_cleaner.py --key TOKEN --region EU/GLOBAL  # If you have any doubt "python3 opsgenie_cleaner.py --help"
```



# Check the results

If everything is working well, when the script finish you will see a new file called --> **all_ids_backup_temp.txt** like this with all Alert IDs. 

![Result](/assets/testing.PNG)


# Delete all alerts

1º With opsgenie-lamp binary already installed in the Docker. Execute a loop with your file all_ids_backup_temp.txt generated before:

https://docs.opsgenie.com/docs/lamp-command-line-interface-for-opsgenie

```bash
cat all_ids_backup_temp.txt | while read line; do opsgenie-lamp deleteAlert --id $line  --apiKey 'XXX' ; done
```

![Result](/assets/opsgenie-lamp.png)

# Considerations

**1º Why is the reason that you use opsgenie-lamp instead to try to delete it with Python script?**

- Yes you are right. I tried but when Python script goes to delete the alerts sometimes I received an error from Cloudflare with the message "429 for too many requests sent".I didn't want to spend more time and I used Opsgenie-lamp. Is a tool written in go language and developers control this types of errors/retry because basically they are the creators of the API.

https://community.atlassian.com/t5/Opsgenie-questions/Error-429-Too-Many-Requests-to-Opsgenie-Integration-API/qaq-p/1966186

**2º Why I can only delete 20.000 closed alerts if I have more than 35.000?**

- There is a limitation in Opsgenie API, only return Max 20.000 records. Is a HARD limit described here --> https://community.atlassian.com/t5/Opsgenie-questions/Opsgenie-Alert-API-422-Sum-of-offset-and-limit-should-be-lower/qaq-p/1576684

# Licence

Apache

# Information

More info --> 

* https://docs.opsgenie.com/docs/alert-api#list-alerts

* https://www.w3schools.com/tags/ref_urlencode.asp

* https://docs.opsgenie.com/docs/api-rate-limiting

* https://stackoverflow.com/questions/4841436/what-exactly-does-do

* https://stackoverflow.com/questions/899103/writing-a-list-to-a-file-with-python-with-newlines

* https://phoenixnap.com/kb/docker-volumes#ftoc-heading-8

# Contributors

* David Álvarez Quiroga
* [Ángel Barrera](https://github.com/angelbarrera92) --> Thanks for your help! :-)


![meme](/assets/this_is_fine.gif)
