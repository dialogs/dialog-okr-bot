from dialog_bot_sdk.interactive_media import *
from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk.internal.peers import private_peer
from gtmhub_metric_handler import GtmHubMetricHandler
from gtmhub_checkin import GtmHubCheckin
from input_exception import InputException
import re
import grpc
import json

#   BOT UTILS


def parse_config():
    with open('config.json') as json_file:
        return json.load(json_file)


def parse_okr_command(text):
    username_mark = '\[\[(.+?)\]\]'
    listname_mark = '\(\((.+?)\)\)'
    regexp = '^\/okr( '+username_mark+'( '+listname_mark+')?| '+listname_mark+'( '+username_mark+')?)?$'

    if not re.match(regexp, text):
        raise InputException('Invalid command')

    username_match = re.search(username_mark, text)
    listname_match = re.search(listname_mark, text)

    params = {}

    if username_match:
        params['username'] = username_match.group(1)

    if listname_match:
        params['list_name'] = listname_match.group(1)

    return params


def is_cancel_text_command(text):
    return re.match('^/stop$', text)


def print_okr_list(peer, okr_list):
    for okr in okr_list:
        for metric in okr['metrics']:
            button = InteractiveMediaButton(metric['id'], 'Refresh')
            action = InteractiveMedia('create', button)
            group = InteractiveMediaGroup([action])
            objective_text = '['+okr['name']+']('+okr['url']+') - '+str(int(round(okr['attainment']*100)))+'%'
            metric_text = '['+metric['name']+']('+okr['url']+'metric/'+metric['id']+'/) - '+str(metric['actual'])+' - * '+str(int(round(metric['attainment']*100)))+'% *'
            bot.messaging.send_message(peer, objective_text+'\n'+metric_text, [group])


def print_okr_info(peer, okr_info):
    message = okr_info['title']+'\n'
    message += 'Now - * '+str(okr_info['current_value'])+' *\n'
    message += 'Must be - * '+str(okr_info['target_value'])+' *\n'
    message += 'Specify a new value.'
    bot.messaging.send_message(peer, message)


def print_need_changes_info(peer):
    bot.messaging.send_message(peer, 'What has changed? Why?')


def print_need_confidence_level(peer, confidence_levels):
    options = {}
    for value in confidence_levels:
        options[str(value)] = str(value)
    select = InteractiveMediaSelect(options, 'Choose level')
    action = InteractiveMedia('set', select)
    group = InteractiveMediaGroup([action])
    bot.messaging.send_message(peer, 'Specify the level of confidence in the result', [group])


def print_update_preview(peer, preview_info):
    send_button = InteractiveMediaButton(preview_info['id'], 'Submit')
    send_action = InteractiveMedia('send', send_button)
    cancel_button = InteractiveMediaButton(preview_info['id'], 'Cancel')
    cancel_action = InteractiveMedia('cancel', cancel_button)
    group = InteractiveMediaGroup([send_action, cancel_action])
    bot.messaging.send_message(peer, '['+preview_info['title']+']('+preview_info['link']+') - * '+str(preview_info['new_percentage'])+'% *', [group])


def print_update_completed(peer):
    bot.messaging.send_message(peer, 'The result is updated')


def print_update_canceled(peer):
    bot.messaging.send_message(peer, 'The update has been cancelled')


def print_error(peer, error):
    bot.messaging.send_message(peer, error)

#   BOT CALLBACKS


def on_message(*params):
    peer = params[0].peer
    message = params[0].message

    try:
        if not hasattr(message, 'textMessage'):
            raise InputException('Invalid input value, only text messages are allowed')

        text = message.textMessage.text

        if handler.has_checkin(peer.id):
            if is_cancel_text_command(text):
                handler.cancel_checkin(peer.id)
                print_update_canceled(peer)
            else:
                handler.update_checkin(peer.id, text)
                checkin_current_state = handler.get_checkin_state(peer.id)
                if checkin_current_state == GtmHubCheckin.STATES.INITIALIZED:
                    print_need_changes_info(peer)
                elif checkin_current_state == GtmHubCheckin.STATES.COMMENTED:
                    confidence_levels = handler.get_confidence_levels(peer.id)
                    print_need_confidence_level(peer, confidence_levels)
                else:
                    raise Exception('Unexpected checkin state')
        else:
            command_params = parse_okr_command(text)

            username = command_params.get('username', None)
            list_name = command_params.get('list_name', None)

            okr_list = handler.get_okr_list(list_name, username)

            print_okr_list(peer, okr_list)

    except InputException as exception:
        print(exception)
        print_error(peer, str(exception))
    except Exception as exception:
        print(exception)
        print_error(peer, 'Some internal error happens')


def on_interact(*params):
    action_id = params[0].id
    value = params[0].value
    uid = params[0].uid

    peer = private_peer(uid)

    try:
        if action_id == 'create':
            handler.create_checkin(peer.id, value)
            okr_info = handler.get_okr_info(peer.id)
            print_okr_info(peer, okr_info)
        elif action_id == 'set':
            handler.update_checkin(peer.id, value)
            preview_info = handler.get_preview_info(peer.id)
            print_update_preview(peer, preview_info)
        elif action_id == 'cancel':
            handler.cancel_checkin(peer.id)
            print_update_canceled(peer)
        elif action_id == 'send':
            handler.send_checkin(peer.id)
            print_update_completed(peer)
        else:
            raise InputException('Invalid action')
    except InputException as exception:
        print(exception)
        print_error(peer, str(exception))
    except Exception as exception:
        print(exception)
        print_error(peer, 'Some internal error happens')


if __name__ == '__main__':
    config = parse_config()

    gtmhub_config = config['gtmhubConfig']
    dialog_config = config['dialogConfig']

    handler = GtmHubMetricHandler(gtmhub_config['url'], gtmhub_config['token'], gtmhub_config['account'])

    bot = DialogBot.get_secure_bot(
        dialog_config['host']+':'+dialog_config['port'],
        grpc.ssl_channel_credentials(),
        dialog_config['token']
    )

    bot.messaging.on_message(on_message, on_interact)
