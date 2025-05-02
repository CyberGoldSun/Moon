import os
import glob
from typing import Final
from confluent_kafka import DeserializingConsumer
from confluent_kafka.serialization import IntegerDeserializer
from scapy.all import PcapWriter
from scapy.layers.l2 import Ether

# Kafka configuration
APPLICATION_ID: Final[str] = "new"
BOOTSTRAP_SERVERS: Final[str] = "192.168.2.165:9092"
TOPIC_LIST = ['network']

consumer_config = {
    'client.id': APPLICATION_ID,
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': 'invoice-consumer-group1',
    'key.deserializer': IntegerDeserializer()
}

consumer = DeserializingConsumer(consumer_config)
consumer.subscribe(TOPIC_LIST)

# rotation configuration
MAX_PCAP_SIZE = 10 * 1024 * 1024  # 10 MB per file

# Utility to find the next pcap index
def get_last_pcap_index():
    files = glob.glob("capture_*.pcap")
    indices = [int(f.split("_")[1].split(".")[0]) for f in files if "_" in f and f.split("_")[1].split(".")[0].isdigit()]
    return max(indices) + 1 if indices else 0

pcap_index = get_last_pcap_index()

def get_new_writer(index: int):
    filename = f"capture_{index}.pcap"
    writer = PcapWriter(filename, append=True, sync=True)
    return filename, writer

current_filename, writer = get_new_writer(pcap_index)

# Main packet capture loop
while True:
    message = consumer.poll(100)
    if message is None:
        continue

    frame_bytes = message.value()
    packet = Ether(frame_bytes)
    print(packet)

    writer.write(packet)

    # Force flush to disk
    writer._write_header(None)  # no-op to access file handle
    writer.f.flush()            # flush Python file buffer
    os.fsync(writer.f.fileno())  # flush OS-level buffer

    # Check if file needs to be rotated
    if os.path.getsize(current_filename) >= MAX_PCAP_SIZE:
        writer.close()
        pcap_index += 1
        current_filename, writer = get_new_writer(pcap_index)
