import paho.mqtt.client as mqtt

BROKER = "machinewiseapp.in"
PORT = 1883
TOPIC = "machinewise/led/strip1/push"
 

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected Successfully!")

        result = client.publish(TOPIC, "60G", qos=1, retain=True)

        if result.rc == 0:
            print("LED command published: 60G")
        else:
            print("Publishing failed")

    else:
        print(f"Connection failed. Return code: {rc}")


client = mqtt.Client()
client.on_connect = on_connect

try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("\nMQTT connection stopped.")

except Exception as error:
    print("MQTT Error:", error)

finally:
    client.disconnect()