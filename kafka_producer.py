
from scapy.all import *
from typing import Final
from kafka3 import KafkaProducer

from scapy.layers.l2 import Ether



my_producer = KafkaProducer(bootstrap_servers=['192.168.2.165:9092'])



def packets(p):
    print(p)
    try:

        # Send the captured packet to Kafka
        my_producer.send('network',value=bytes(p))

        print("Packet sent to Kafka")

    except Exception as e:
        print(f"Error sending packet to Kafka: {e}")


if __name__ == '__main__':
    sniff(iface="wan", prn=packets)
