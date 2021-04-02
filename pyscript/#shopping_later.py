
#%%
@event_trigger('shopping_list_updated')
def monitor_service_calls(**kwargs):
    log.info(f"got EVENT_CALL_SERVICE with kwargs={kwargs}")
 