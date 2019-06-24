## Introduction

GtmHubBot is a Python script to manage your current OKR's from GtmHub through a Dialog chat. You will need an account on both platforms in order to use this tool.

## Requisites

This script requires Python 3 or greater, with the following packages, and his dependencies

- dialog-sdk-bot
- requests
- grpcio
- async_cron

## Configuration

Create a chat bot in your Dialog instance and store his access **token**.

Generate and **API token** from you GtmHub account and get your **account id**, if you haven't insuficient permissions, contact your account admin.

Create or modify the **config.json** file ( placed in the script folder ) to follow the format bellow :

```
{
  "dialogConfig": {
    "host": "dialog.host.com",
    "port": "1234",
    "token": "abcdefghijk1234"
  },
  "gtmhubConfig": {
    "url": "https://app.us.gtmhub.com/api/v1",
    "token": "abcdefghijk1234",
    "account": "abcdefghijk1234"
  }
}
```

All keys on the config are required string values. ( Between quotation marks )

`dialogConfig.host` host url where your Dialog instance is accessible, without include protocol prefix ( https is assumed )</br>
`dialogConfig.port` secure port which the Dialog instanca is listening </br>
`dialogConfig.token` token to access the Dialog bot instance

`gtmhubConfig.url` the url for the GtmHub API, should be "https://app.gtmhub.com/api/v1" or "https://app.us.gtmhub.com/api/v1" depending your account location </br>
`gtmhubConfig.account`the GtmHub account id 
`gtmhubConfig.token` the generated token for the account

## Usage

Run gtmhub_bot.py from some machine, if all goes fine you will see the "Bot is ready message" ( with no exceptions ).

Then you can open your prefered Dialog client to talk to the assigned bot ( asociated to the provided token ).

There are 3 main commands which starts a process and can't be overlaped ( you need to finish or cancel the proocess to run another process command ) since it requires new ordered input from the chat.

`/okr` command will list all your current OKR's. You can provide two optional parameters to the command, username and list name.

The user parameter should be marked between double square brakets `[[user name]]` and will return the current OKR's of the specified user, instead of yours.
The listname parameter should be marked between double parentheses `((list name))` and will filter the results, returning only the OKR's on the specified list.

So, and example using both can be `/okr [[user name]] ((list name))`

`/overview` will run internally the okr command, with no parameters, and store the list to allow you to iterate all OKR's in ordered way

`/activate` this command allow you to set a scheduler for the overview command, so you will be reminded to overview your okr's in the configured date
`/desactivate` command will remove your reminder

`/stop` command will cancel the current process, so if you introduced an incorrect value or want to exit the current overview, you can use this command. If you are processing an OKR update inside your overview, this command with cancel the update and not the full overview, but you can run again the command to exit the overview.