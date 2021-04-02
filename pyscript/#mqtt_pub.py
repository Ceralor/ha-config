@event_trigger("*")
def mqtt_pub(**kwargs):
	import json
	topic = "HA_EVENT"
	payload = json.dumps(kwargs)
	mqtt.publish(topic=topic,payload=payload)
