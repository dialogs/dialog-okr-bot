from dialog_bot_sdk.interactive_media import *
from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk.internal.peers import private_peer
from src.gtmhub_metric_handler import GtmHubMetricHandler
from src.gtmhub_scheduler import GtmHubScheduler
from src.gtmhub_checkin import GtmHubCheckin
from src.input_exception import InputException
from src.translator import _
import re
import grpc
import json

#   BOT UTILS


def parse_config():
    with open('./config/config.json') as json_file:
        return json.load(json_file)


def parse_command_params(command, text):
    username_mark = '\[\[(.+?)\]\]'
    listname_mark = '\(\((.+?)\)\)'
    regexp = '^\/'+command+'( '+username_mark+'( '+listname_mark+')?| '+listname_mark+'( '+username_mark+')?)?$'

    if not re.match(regexp, text):
        raise InputException(_('Invalid command'))

    username_match = re.search(username_mark, text)
    listname_match = re.search(listname_mark, text)

    params = {}

    if username_match:
        params['username'] = username_match.group(1)

    if listname_match:
        params['list_name'] = listname_match.group(1)

    return params


def is_activate_text_command(text):
    return re.match('^/'+_('activate')+'$', text)


def is_desactivate_text_command(text):
    return re.match('^/'+_('desactivate')+'$', text)


def is_okr_text_command(text):
    return re.match('^/'+_('okr'), text)


def is_cancel_text_command(text):
    return re.match('^/'+_('stop')+'$', text)


def is_overview_text_command(text):
    return re.match('^/'+_('overview'), text)


def print_okr_list(peer, okr_list):
    if not okr_list:
        bot.messaging.send_message(peer, _("There are no available OKR's with the specified parameters"))
    else:
        for id, okr in okr_list.items():
            button = InteractiveMediaButton(okr['id'], _('Refresh'))
            action = InteractiveMedia('create', button)
            group = InteractiveMediaGroup([action])
            objective_text = '['+okr['project_name']+']('+okr['project_url']+') - '+str(int(round(okr['project_attainment']*100)))+'%'
            metric_text = '['+okr['name']+']('+okr['project_url']+'metric/'+okr['id']+'/) - '+str(okr['actual'])+' - * '+str(int(round(okr['attainment']*100)))+'% *'
            bot.messaging.send_message(peer, objective_text+'\n'+metric_text, [group])


def print_okr_info(peer, okr_info):
    message = okr_info['title']+'\n'
    message += _('Now - * {} *').format(okr_info['current_value'])+'\n'
    message += _('Must be - * {} *').format(okr_info['target_value'])+'\n'
    message += _('Specify a new value.')
    bot.messaging.send_message(peer, message)


def print_need_changes_info(peer):
    bot.messaging.send_message(peer, _('What has changed? Why?'))


def print_need_scheduler_hour(peer):
    bot.messaging.send_message(peer, _('Ok, now please reply with time in 16:40 format by Moscow timezone for me to know when to start'))


def print_need_scheduler_username(peer):
    bot.messaging.send_message(peer, _('Tell me what user you will be overviewing'))


def print_need_confidence_level(peer, confidence_levels):
    options = {}
    for value in confidence_levels:
        options[str(value)] = str(value)
    select = InteractiveMediaSelect(options, _('Choose level'))
    action = InteractiveMedia('set', select)
    group = InteractiveMediaGroup([action])
    bot.messaging.send_message(peer, _('Specify the level of confidence in the result'), [group])


def print_need_reminder_day(peer, days_list):
    select = InteractiveMediaSelect(days_list, _('Choose day'))
    action = InteractiveMedia('cron', select)
    group = InteractiveMediaGroup([action])
    bot.messaging.send_message(peer, _('Please select day to update OKR with you'), [group])


def print_update_preview(peer, preview_info):
    send_button = InteractiveMediaButton(preview_info['id'], _('Submit'))
    send_action = InteractiveMedia('send', send_button)
    cancel_button = InteractiveMediaButton(preview_info['id'], _('Cancel'))
    cancel_action = InteractiveMedia('cancel', cancel_button)
    group = InteractiveMediaGroup([send_action, cancel_action])
    bot.messaging.send_message(peer, '['+preview_info['title']+']('+preview_info['link']+') - * '+str(preview_info['new_percentage'])+'% *', [group])


def print_overview_navigation(peer):
    send_button = InteractiveMediaButton('next', _('Next key'))
    send_action = InteractiveMedia('overview', send_button)
    cancel_button = InteractiveMediaButton('list', _('List un-updated keys'))
    cancel_action = InteractiveMedia('overview', cancel_button)
    group = InteractiveMediaGroup([send_action, cancel_action])
    bot.messaging.send_message(peer, _('What is next'), [group])


def print_update_completed(peer):
    bot.messaging.send_message(peer, _('The result is updated'))


def print_overview_completed(peer):
    bot.messaging.send_message(peer, _('The overview is completed'))


def print_update_canceled(peer):
    bot.messaging.send_message(peer, _('The update has been cancelled'))


def print_overview_canceled(peer):
    bot.messaging.send_message(peer, _('The overview has been cancelled'))


def print_scheduler_canceled(peer):
    bot.messaging.send_message(peer, _('The reminder has been cancelled'))


def print_message(peer, message):
    bot.messaging.send_message(peer, message)


def print_error(peer, error):
    bot.messaging.send_message(peer, error)

#   BOT CALLBACKS


def scheduled_overview(peer_id, username):

    print('Running scheduled overview '+str(peer_id))

    peer = private_peer(peer_id)

    if handler.has_overview(peer_id) or handler.has_checkin(peer_id) or scheduler.need_params(peer_id):
        print_message(peer, _("It's time to update your OKRs. but seems you have some pendant works, after finish it you can run /overview command"))
    else:
        try:
            handler.create_overview(peer.id, None, username)
            print_message(peer, _("It's time to update your OKRs. Ok, let's go"))
            print_okr_list(peer, handler.overviews[peer.id])
        except InputException as ex:
            print_message(peer, _("It's time to update your OKRs. But seems you have no OKR's to overview"))
        except Exception as ex:
            print("Exception on scheduled overview")
            print(ex)


def on_message(*params):
    peer = params[0].peer
    message = params[0].message
    sender_uid = params[0].sender_uid

    if peer.id == sender_uid:
        try:
            if not hasattr(message, 'textMessage'):
                raise InputException(_('Invalid input value, only text messages are allowed'))

            text = message.textMessage.text

            if is_cancel_text_command(text):
                if handler.has_checkin(peer.id):
                    handler.cancel_checkin(peer.id)
                    print_update_canceled(peer)
                elif handler.has_overview(peer.id):
                    handler.cancel_overview(peer.id)
                    print_overview_canceled(peer)
                elif scheduler.need_params(peer.id):
                    scheduler.cancel_cron(peer.id)
                    print_scheduler_canceled(peer)
                else:
                    print_error(peer, _('Nothing to cancel'))
            elif is_overview_text_command(text):
                if scheduler.need_params(peer.id):
                    raise InputException(_('Please, finish your reminder configuration, or cancel it, before continue'))

                command_params = parse_command_params(_('overview'), text)

                username = command_params.get('username', None)
                list_name = command_params.get('list_name', None)

                handler.create_overview(peer.id, list_name, username)
                print_okr_list(peer, handler.overviews[peer.id])
            elif is_okr_text_command(text):
                if scheduler.need_params(peer.id):
                    raise InputException(_('Please, finish your reminder configuration, or cancel it, before continue'))
                if handler.has_checkin(peer.id):
                    raise InputException(_('You have a checkin currently'))
                if handler.has_overview(peer.id):
                    raise InputException(_("Please, finish you overview, or cancel it, before continue"))

                command_params = parse_command_params(_('okr'), text)

                username = command_params.get('username', None)
                list_name = command_params.get('list_name', None)

                okr_list = handler.get_okr_list(list_name, username)

                print_okr_list(peer, okr_list)
            elif is_activate_text_command(text):
                if handler.has_checkin(peer.id) or handler.has_overview(peer.id):
                    raise InputException(_('Please, finish your updates before begin configuring the reminder'))
                if scheduler.has_cron(peer.id):
                    raise InputException(_('You have a reminder currently, remove it to setup a new one'))
                scheduler.create_cron(peer.id)
                print_need_reminder_day(peer, GtmHubScheduler.days_list)
            elif is_desactivate_text_command(text):
                if not scheduler.has_cron(peer.id):
                    raise InputException(_('You have not a scheduler currently'))
                scheduler.cancel_cron(peer.id)
                print_scheduler_canceled(peer)
            else:
                if handler.has_checkin(peer.id):
                    handler.update_checkin(peer.id, text)
                    checkin_current_state = handler.get_checkin_state(peer.id)
                    if checkin_current_state == GtmHubCheckin.STATES.INITIALIZED:
                        print_need_changes_info(peer)
                    elif checkin_current_state == GtmHubCheckin.STATES.COMMENTED:
                        confidence_levels = handler.get_confidence_levels(peer.id)
                        print_need_confidence_level(peer, confidence_levels)
                    else:
                        raise Exception(_('Unexpected checkin state'))
                elif scheduler.need_params(peer.id):
                    scheduler.set_value(peer.id, text)
                    if not scheduler.need_params(peer.id):
                        scheduler.enable_cron(peer.id)
                        day = scheduler.days_list[scheduler.crons[peer.id].day]
                        hour = scheduler.crons[peer.id].hour
                        print_message(peer, _("Ok, then each {} at {} I will start updating okr's with you.").format(day, hour))
                    else:
                        if scheduler.crons[peer.id].hour is None:
                            print_need_scheduler_hour(peer)
                        else:
                            print_need_scheduler_username(peer)
                else:
                    raise InputException(_('Invalid command'))

        except InputException as exception:
            print(exception)
            print_error(peer, str(exception))
        except Exception as exception:
            print(exception)
            print_error(peer, _('Some internal error happens'))


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
        elif action_id == 'cron':
            scheduler.set_value(peer.id, value)
            print_need_scheduler_hour(peer)
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
            if handler.has_overview(peer.id):
                if handler.get_overview_lenght(peer.id) > 0:
                    print_overview_navigation(peer)
                else:
                    handler.cancel_overview(peer.id)
                    print_overview_completed(peer)
        elif action_id == 'overview':
            if not handler.has_overview(peer.id):
                raise InputException(_('Invalid action'))
            if handler.has_checkin(peer.id):
                raise InputException(_('You have a checkin currently, please finish it before'))
            if value == 'next':
                if handler.get_overview_lenght(peer.id) == 0:
                    raise InputException(_('Empty overview'))
                next_okr_id = handler.get_next_overview_checkin_id(peer.id)
                handler.create_checkin(peer.id, next_okr_id)
                okr_info = handler.get_okr_info(peer.id)
                print_okr_info(peer, okr_info)
            elif value == 'list':
                print_okr_list(peer, handler.overviews[peer.id])
            else:
                raise InputException(_('Invalid action'))
        else:
            raise InputException(_('Invalid action'))
    except InputException as exception:
        print(exception)
        print_error(peer, str(exception))
    except Exception as exception:
        print(exception)
        print_error(peer, _('Some internal error happens'))


if __name__ == '__main__':
    try:
        config = parse_config()

        gtmhub_config = config['gtmhubConfig']
        dialog_config = config['dialogConfig']

        handler = GtmHubMetricHandler(gtmhub_config['url'], gtmhub_config['token'], gtmhub_config['account'])

        scheduler = GtmHubScheduler(handler.get_usernames_list(), scheduled_overview)

        bot = DialogBot.get_secure_bot(
            dialog_config['host']+':'+dialog_config['port'],
            grpc.ssl_channel_credentials(),
            dialog_config['token']
        )

        bot.messaging.on_message(on_message, on_interact)
    except KeyboardInterrupt as ex:
        print(_('Stopping scheduler thread ...'))
        if scheduler.loop.is_running() is True:
            scheduler.loop.stop()
    except Exception as ex:
        print(_('Error initializing the bot - {}').format(str(ex)))
        raise ex
