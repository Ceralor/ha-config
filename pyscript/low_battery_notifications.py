# %%
state.persist("pyscript.notified_batts")

@time_trigger("cron(0 * * * *)")
def report_batteries():
    import json
    low_batts = []
    for entity_id in state.names():
        entity_attrs = state.getattr(entity_id)
        if ("battery_level" in entity_attrs.keys()) and \
            ("device_class" in entity_attrs.keys()) and \
            (entity_attrs["device_class"] not in ("humidity","pressure")) and \
            (entity_attrs["battery_level"] <= 15):
            low_batts.append(entity_id)
    notified_batts = []
    if "pyscript.notified_batts" in state.names(domain="pyscript"):
        notified_batts_prev = json.loads(pyscript.notified_batts)
        for entity_id in notified_batts_prev:
            if entity_id in low_batts:
                notified_batts.append(entity_id)
    non_notified_batts = []
    for entity_id in low_batts:
        if entity_id not in notified_batts:
            non_notified_batts.append(entity_id)
    for entity_id in non_notified_batts:
        entity_attrs = state.getattr(entity_id)
        notified_batts.append(entity_id)
        message = f'The {entity_attrs["friendly_name"]} battery level is low at {entity_attrs["battery_level"]}% and needs to be replaced or recharged soon.'
        telegram_bot.send_message(message=message,parse_mode="html")
    pyscript.notified_batts = json.dumps(notified_batts)
