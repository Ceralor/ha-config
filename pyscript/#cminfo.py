import requests

# unit_of_measurement: '%'
# icon: 'mdi:speedometer'
# availability_topic: iotlink/workgroup/yapbox/lwt
# state_topic: iotlink/workgroup/yapbox/windows-monitor/stats/cpu/usage
# name: YAPBOX CPU Usage
# unique_id: yapbox_cpu_usage
# payload_available: 'ON'
# payload_not_available: 'OFF'
# device:
#   identifiers:
#     - YAPBOX_CPU
#   name: YAPBOX CPU
#   model: WORKGROUP
#   manufacturer: IOTLink 2.2.2.0
# platform: mqtt
login_url = 'http://192.168.100.1/goform/login'
wan_info_url = 'http://192.168.100.1/data/getCmDocsisWan.asp'
ustream_info_url = 'http://192.168.100.1/data/usinfo.asp'
dstream_info_url = 'http://192.168.100.1/data/dsinfo.asp'
system_model_url = 'http://192.168.100.1/data/system_model.asp'
system_info_url = 'http://192.168.100.1/data/getSysInfo.asp'

s = requests.Session()
r = s.post(login_url,data={'user':'','pws':''})
wan_info = s.get(wan_info_url).json()[0]
ustream_info = s.get(ustream_info_url).json()
dstream_info = s.get(dstream_info_url).json()
system_model = s.get(system_model_url).json()[0]
system_info = s.get(system_info_url).json()[0]
device_payload = { \
    'identifiers':['cable_modem'], \
    'name':'Cable Modem', \
    'model':system_info['modelName'], \
    'manufacturer':system_info['vendorname']}
ha_mqtt_root = 'homeassistant/sensor/cablemodem/'
state.set('sensor.cable_modem_wan_info',value=wan_info['CmIpAddress'],new_attributes=wan_info)
for port in ustream_info:
	sensor_name = f"sensor.cable_modem_upstream_port{port['portId']}_signal_strength"
	state.set(sensor_name,value=port['signalStrength'],new_attributes=port)
	state.setattr(f"{sensor_name}.unit_of_measurement",'dBm')
	state.setattr(f"{sensor_name}.device_class",'signal_strength')
for port in dstream_info:
	sensor_name = f"sensor.cable_modem_downstream_port{port['portId']}_snr"
	state.set(sensor_name,value=port['snr'],new_attributes=port)
	state.setattr(f"{sensor_name}.unit_of_measurement",'dB')
	state.setattr(f"{sensor_name}.device_class",'signal_strength')
