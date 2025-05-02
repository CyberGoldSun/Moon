
# Kafka Packet Monitor on OpenWrt

Moon is a simple and experimental project that shows how a lightweight Kafka-based network monitoring setup can be built using OpenWrt and a Raspberry Pi. The idea is to sniff raw network packets on a router running OpenWrt and send them via Kafka to a separate consumer that stores them as `.pcap` files for later analysis.

## Overview

- The **Kafka producer** runs on an OpenWrt router (Netgear Nighthawk X6 R8000 with OpenWrt 22.03.5). It uses Python and [Scapy](https://scapy.net) to sniff packets on a specified interface (e.g., `wan`) and sends them to a Kafka topic.
- The **Kafka broker and consumer** run on a Raspberry Pi 4B with Ubuntu. The consumer reads packets from the Kafka topic and writes them into rotating `.pcap` files.

> Please note: This is just an idea and an example setup. You can expand or adapt it for your own use cases.

## Device and Firmware

This project was tested on a **Netgear Nighthawk X6 R8000** router running **OpenWrt 22.03.5**.

To install OpenWrt on this device, please refer to the official OpenWrt guide:  
[https://openwrt.org/toh/netgear/r8000](https://openwrt.org/toh/netgear/r8000#:~:text=Use%20https%3A%2F%2Ffirmware-selector.openwrt.org%20to%20download%20the%20most%20recent%20stable,a%20customized%20OpenWrt%20image%20with%20different%20installed%20packages)

## Prerequisites

### On the OpenWrt Router

Python 3 is required to run the Kafka producer. The reference page for the OpenWrt Python 3 package is available here:  
[OpenWrt Package: python3](https://openwrt.org/packages/pkgdata/python3)

Ensure the router is connected to the internet and that it can reach your Kafka server (e.g., on a subnet like `192.168.2.0/24`).

### On the Raspberry Pi

Install Ubuntu and download the Confluent Platform (version used: `confluent-7.9.0`) from:  
[https://www.confluent.io/get-started/]

Java is required. This project used:

```
openjdk version "17.0.11"
```

## Kafka Setup (on Raspberry Pi)

Start Zookeeper:
```bash
PATH/confluent-7.9.0/bin$ sudo ./zookeeper-server-start ../etc/kafka/zookeeper.properties
```

Start Kafka broker:
```bash
PATH/confluent-7.9.0/bin$ sudo ./kafka-server-start ../etc/kafka/server.properties
```

Create a topic:
```bash
PATH/confluent-7.9.0/bin$ sudo ./kafka-topics --create --topic network --partitions 1 --bootstrap-server 192.168.2.165:9092
```

## OpenWrt Producer Setup

### Step-by-step

```bash
cd ~
mkdir Moon
cd Moon
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install scapy
pip install kafka-python3
```

Upload the `kafka_producer.py` file into the `Moon` directory using `scp` or another method.

Run the producer (inside the virtualenv):
```bash
(venv) root@OpenWrt:~/Moon# python3.10 kafka_producer.py
```

> Note: The interface (`wan`), Kafka IP (`192.168.2.165`), and topic name (`network`) are just examples and should be changed to fit your environment.

## Kafka Consumer Setup (on Raspberry Pi)

### Step-by-step

```bash
mkdir Network
cd Network
python3 -m venv venv
source venv/bin/activate
pip install scapy
pip install confluent-kafka
```

Upload `consumer_kafka.py` into the `Network` directory.

Run the consumer:
```bash
(venv) user@raspberrypi:~/Network$ python3 consumer_kafka.py
```

The consumer will store incoming packets in `.pcap` files, rotating when files reach 10MB.

## Final Notes

This project is minimal and meant as a proof-of-concept. Feel free to modify, improve, or expand it for your needs.  
Feedback and suggestions are welcome!
