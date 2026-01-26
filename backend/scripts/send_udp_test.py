#!/usr/bin/env python3
"""
UDP test sender: envia JSON messages to a UDP endpoint for testing realtime pipeline.
Usage: python send_udp_test.py --host 127.0.0.1 --port 8765 --gesture CLOSE --conf 0.9
"""
import json
import socket
import argparse
import time

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--gesture', default='CLOSE')
    p.add_argument('--conf', type=float, default=0.9)
    p.add_argument('--interval', type=float, default=1.0)
    args = p.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending to {args.host}:{args.port} gesture={args.gesture}")
    try:
        while True:
            msg = json.dumps({
                'ts': time.time(),
                'gesture': args.gesture,
                'conf': args.conf,
                'source': 'udp_test'
            })
            sock.sendto(msg.encode('utf-8'), (args.host, args.port))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('Stopped')

if __name__ == '__main__':
    main()
