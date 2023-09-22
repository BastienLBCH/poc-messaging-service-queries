# Poc Messaging Service CQRS queries part
This code is a proof of concept. 
Meaning it's not made to run on a production environment (e.g. it uses a sqlite database) 
and it is also the first time I use these design patterns.

It's part of an instant messaging service designed with the CQRS designed pattern combined with event sourcing.

This repo contains the queries part, meaning that it get the event from Kafka, update the database and is focused on 
delivering data to the users

> [!NOTE]
> For easier testing, as ***demo*** purpose, this project also contains a small frontend app. 
> Please take note that I am not a frontend developer, never pretented to be one and that on a real project I would have developped a real application


## Installation
### Preparing
**Prerequisite :** Having docker installed

You need to create a .env file in the folder pocMessagingServiceCommands
Options are :
```
KAFKA_BOOTSTRAP_SERVER
KAFKA_GROUP_ID
KAFKA_TOPIC

KEYCLOAK_PUBLIC_KEY
KEYCLOAK_ALG
```
Explaining one by one :
- **KAFKA_BOOTSTRAP_SERVER**: Address of the Kafka server used to 
- **KAFKA_GROUP_ID**: Group ID 
- **KAFKA_TOPIC**: Topic to send the messages on
- **KEYCLOAK_PUBLIC_KEY**: Public key used by Keycloak to sign the JWT delivered
- **KEYCLOAK_ALG**: Algorithm used by Keycloak to sign the JWT

To use the demo frontend, add these requirements
```
# Optionals arguments for using integrated frontend
KEYCLOAK_CLIENT_ID
KEYCLOAK_USERS_URL
COMMAND_SERVER

# Used for integrated frontend & unit testing
KEYCLOAK_TOKEN_URL
```
- **KEYCLOAK_CLIENT_ID** : ID of the keycloak client used to authentify users
- **KEYCLOAK_USERS_URL** : [Keycloak endpoint to list realm's users](https://www.keycloak.org/docs-api/22.0.1/rest-api/#_users) ({base_url}/admin/realms/{realm}/users)
- **COMMAND_SERVER** : Base url (http://host:port) of the command service. Should not end with a /
- **KEYCLOAK_TOKEN_URL**: DO NOT PUT IT TWICE. Keycloak url to get the access token. 
This argument is needed for both unit testing and using the demo frontend app ({base_url}/realms/{realm}/protocol/openid-connect/token)

For unit test, you have to add extra variables :
```
# Used for integrated frontend & unit testing
KEYCLOAK_TOKEN_URL


# Optionals Arguments for unit testing
KEYCLOAK_USERNAME_TEST
KEYCLOAK_USERNAME_TEST_2
KEYCLOAK_PASSWORD_TEST
```
- **KEYCLOAK_TOKEN_URL**: DO NOT PUT IT TWICE. Keycloak url to get the access token. This argument is needed for both unit testing and using the demo frontend app
- **KEYCLOAK_USERNAME_TEST**: Username of a user existing for testing purpose
- **KEYCLOAK_USERNAME_TEST_2**: Username of a second user existing for testing purpose
- **KEYCLOAK_PASSWORD_TEST**: Test users has to share the same password which will be stored in this variable



**Example of a complete .env file :**
```
KEYCLOAK_PUBLIC_KEY=MIIB...AQAB
KEYCLOAK_ALG=RS256


# Optionals arguments for using integrated frontend
KEYCLOAK_CLIENT_ID=login-client
KEYCLOAK_USERS_URL=http://localhost:8080/admin/realms/poc/users/
COMMAND_SERVER=http://localhost:8000


# Used for integrated frontend & unit testing
KEYCLOAK_TOKEN_URL=http://localhost:8080/realms/poc/protocol/openid-connect/token


# Optionals Arguments for unit testing
KEYCLOAK_USERNAME_TEST=John
KEYCLOAK_USERNAME_TEST_2=Doe
KEYCLOAK_PASSWORD_TEST=qwerty
```


### Building and deploying

> [!IMPORTANT]
> This repo is only one "service" of the whole project, if you want to really test it you need :
> - [The command part](https://github.com/BastienLBCH/poc-messaging-service-commands) 
> - Kafka
> - Keycloak
> 
> To be configured and runnning

You can easily deploy this service using docker using these commands in the project root directory:
```bash
docker build . -t poc-messaging-service-query
```
then
```bash 
docker run -p 8000:8000 --name poc-messaging-service-query poc-messaging-service-query 
```


## Usage
This API provides endpoints to create conversations, post messages and add a participant to a conversation.


### List all user's conversation
- **Endpoint**: /conversations
- **Method**: GET

Headers :

| Attribute       |                  Value |
|:----------------|-----------------------:|
| Authorization   |  Bearer {access token} |



### Get all messages from a conversation
- **Endpoint**: /conversations/{conversation_id}
- **Method**: GET

Headers :

| Attribute       |                  Value |
|:----------------|-----------------------:|
| Authorization   |  Bearer {access token} |




### Get all members from a conversation
- **Endpoint**: /conversations/{conversation id}/members
- **Method**: GET

Headers :

| Attribute       |                  Value |
|:----------------|-----------------------:|
| Authorization   |  Bearer {access token} |


### Connect the websocket
The service uses websockets to send events in real time to the frontend, so it can update without reloading everything.

- **endpoint**: ws://{base url}/ws/{token}

The token in the url is the Json Web Token provided on login






