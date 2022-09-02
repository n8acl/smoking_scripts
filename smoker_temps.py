#################################################
# Import Libraries
import config as cfg
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import os
import mysql.connector
from subprocess import check_output
from re import findall
from time import sleep
from datetime import datetime
from mysql.connector import Error

#################################################
# Misc Variables
my_broker = cfg.my_mqtt_broker
tenergy_topic = "theengsgateway/780473C30D6C"
smoker_base_topic = "sensors/temp/smoker/"
tenergy_temp_topic = smoker_base_topic + "tenergy/probe/"
power_topic = smoker_base_topic + "tenergy/power"
power = 1
default_states = {"tempf":0,"tempf2":0,"tempf3":0,"tempf4":0,"tempf5":0,"tempf6":0}
errormsg = "Smoker Temp Reader stopped for some reason."
conn = mysql.connector.connect(**cfg.sensor_data_db_config)
#discord_wh_url = config.discord_webhook_url

#################################################
## Define Functions

## User Defined Functions

def select_sql(conn, sql):
    # Executes SQL for Selects - Returns a "value"
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall(), cur.rowcount

def exec_sql(conn,sql):
    # Executes SQL for Updates, inserts and deletes - Doesn't return anything
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def publish_message(topic, message):
    publish.single(topic,message,hostname=my_broker)

def parse_temps(data):
    now = datetime.now()
    dt_string = datetime.timestamp(now)
    temp_data = json.loads(data)

    sql = "insert into smoker_temps (dtstamp,probe1,probe2,probe3,probe4,probe5,probe6) "
    sql = sql + "values(" + str(int(dt_string)) + ","

    for i in range(1,7):
        if i == 1:
            if "tempf" in temp_data:
                publish_message(tenergy_temp_topic + "1",temp_data["tempf"])
                sql = sql + str(temp_data["tempf"])
            else:
                publish_message(tenergy_temp_topic + "1",0)
                sql = sql + str(0)
        else:
            if "tempf"+str(i) in temp_data:
                publish_message(tenergy_temp_topic + str(i),temp_data["tempf"+str(i)])
                sql = sql + str(temp_data["tempf"+str(i)])
            else:
                publish_message(tenergy_temp_topic + str(i),0)
                sql = sql + str(0) 
        if i == 6:
            sql = sql + ");"
            break
        else:
            sql = sql + ","

    exec_sql(conn, sql)         

## Define MQTT Callback Functions

def on_connect(client, userdata, flags, rc):
    # Subscribe to cheerlights and cheerlightsRGB topics on mqtt.cheerlights.com
    client.subscribe([(tenergy_topic,0),(power_topic,0)])

def on_message(client, userdata, message):
    global power
    if (message.topic == power_topic):
        if (str(message.payload.decode("utf-8")).strip() == "on"):
            power = 1
        elif (str(message.payload.decode("utf-8")).strip() == "off"):
            power = 0
        elif (str(message.payload.decode("utf-8")).strip() == "reboot"):
            script_state(0)
            os.system('sudo reboot now')
    
    else:
        if power == 1:
            parse_temps(str(message.payload.decode("utf-8","ignore")))
        else:
            power = 0
            parse_temps(str(json.dumps(default_states)))


#################################################
## Main Program

try:
    # create connecton clients
    client = mqtt.Client("cloudbbq")

    # Bind functions to callbacks for receiving Cheerlights messages
    client.on_message=on_message
    client.on_connect=on_connect

    # Connect to broker mqtt.cheerlights.com
    client.connect(my_broker, keepalive=60)#connect

    # Start loop to process received messages
    client.loop_forever() 

except KeyboardInterrupt:
    client.disconnect()
    #send_telegram_msg(errormsg)
    #send_discord_msg(errormsg,discord_wh_url)

except Exception as e:
    client.disconnect()
    print(e)
    #send_telegram_msg(errormsg)
    #send_discord_msg(errormsg,discord_wh_url)