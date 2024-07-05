import time
import epics
import paho.mqtt.client as mqtt
import queue

def main():
    ## runs on connection
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    ## client setup
    print('Attempting to connect to MQTT server ...')
    mqclient = mqtt.Client(client_id="nsrv-envs", clean_session=True, transport="tcp")
    mqclient.username_pw_set("Spock", password="vulcan")
    mqclient.on_connect = on_connect
    mqclient.connect("192.168.1.11", port=1883, keepalive=60)
    mqclient.loop_start()
    time.sleep(2)

    dataQ = queue.Queue(20)
    def epicscallback(pvname=None, value=None, char_value=None, **kw):
        if not dataQ.full():
            qmsg = [pvname, value]
            dataQ.put(qmsg)

    ## create epics channels
    print("Connecting to epics channels...")
    pvtemp = epics.PV("NSRV:ENV:temperature:avg", auto_monitor=True, callback=epicscallback)
    pvtemp = epics.PV("NSRV:ENV:pressure:avg", auto_monitor=True, callback=epicscallback)
    pvtemp = epics.PV("NSRV:ENV:rh:avg", auto_monitor=True, callback=epicscallback)
    pvtemp = epics.PV("NSRV:ENV:light:intensity:avg", auto_monitor=True, callback=epicscallback)
    time.sleep(3)

    ## main loop
    print("Main loop started...")
    # clear queue
    dataQ.queue.clear()
    while(True):
        payload = dataQ.get()
        topic = payload[0].replace(':',"/")
        v = float(payload[1])
        mqclient.publish(topic, payload=v, qos=0, retain=False)

try:
    main()
except Exception as err:
    print("[{}] Error:".format(time.asctime()))
    print(err)
    time.sleep(10)

print("OK")
