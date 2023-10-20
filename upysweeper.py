#!/usr/bin/python3

# You need to install these packages:
# tk, pycryptodome, pyserial

# If you're on Linux, you need to run this script as a user with serial port access permission.

# Update : µpysweeper
# Author : krazynez
# Date   : September 29, 2023
# Version: 0.1
# headless version of pysweeper ( still requires PC for now ;-) )

from Crypto.Cipher import AES 
import serial
import serial.tools.list_ports
import threading
import time
import os
import sys
import argparse


keystore = {\
    0x00: "5C52D91CF382ACA489D88178EC16297B",\
    0x01: "9D4F50FCE1B68E1209307DDBA6A5B5AA",\
    0x02: "0975988864ACF7621BC0909DF0FCABFF",\
    0x03: "C9115CE2064A2686D8D6D9D08CDE3059",\
    0x04: "667539D2FB4273B2903FD7A39ED2C60C",\
    0x05: "F4FAEF20F4DBAB31D18674FD8F990566",\
    0x06: "EA0C811363D7E930F961135A4F352DDC",\
    0x08: "0A2E73305C382D4F310D0AED84A41800",\
    0x09: "D20474308FE269046ED7BB07CF1CFF43",\
    0x0A: "AC00C0E3E80AF0683FDD1745194543BD",\
    0x0B: "0177D750BDFD2BC1A0493A134A4C6ACF",\
    0x0C: "05349170939345EE951A14843334A0DE",\
    0x0D: "DFF3FCD608B05597CF09A23BD17D3FD2",\
    0x2F: "4AA7C7B01134466FAC82163E4BB51BF9",\
    0x97: "cac8b87acd9ec49690abe0813920b110",\
    0xB3: "03BEB65499140483BA187A64EF90261D",\
    0xD9: "C7AC1306DEFE39EC83A1483B0EE2EC89",\
    0xEB: "418499BE9D35A3B9FC6AD0D6F041BB26"}
                    
challenge1_secret = {\
    0x00: "D2072253A4F27468",\
    0x01: "B37A16EF557BD089",\
    0x02: "A04E32BBA7139E46",\
    0x03: "B0B809833989FAE2",\
    0x04: "FE7D7899BFEC47C5",\
    0x05: "306F3A03D86CBEE4",\
    0x06: "8422DFEAE21B63C2",\
    0x08: "AD4043B256EB458B",\
    0x0A: "C2377E8A74096C5F",\
    0x0D: "581C7F1944F96262",\
    0x2F: "F1BC562BD55BB077",\
    0x97: "af6010a846f741f3",\
    0xB3: "DBD3AEA4DB046410",\
    0xD9: "90E1F0C00178E3FF",\
    0xEB: "0BD9027E851FA123"}

challenge2_secret = {\
    0x00: "F5D7D4B575F08E4E",\
    0x01: "CC699581FD89126C",\
    0x02: "495E034794931D7B",\
    0x03: "F4E04313AD2EB4DB",\
    0x04: "865E3EEF9DFBB1FD",\
    0x05: "FF72BD2B83B89D2F",\
    0x06: "58B95AAEF399DBD0",\
    0x08: "67C07215D96B39A1",\
    0x0A: "093EC519AF0F502D",\
    0x0D: "318053875C203E24",\
    0x2F: "1BDF2433EB29155B",\
    0x97: "9deec01144b66f41",\
    0xB3: "E32B8F56B2641298",\
    0xD9: "C34A6A7B205FE8F9",\
    0xEB: "F791ED0B3F49A448"}

go_key1 = bytes.fromhex("C66E9ED6ECBCB121B7465D25037D6646")
go_key2 = bytes.fromhex("da24dab43a61cbdf61fd255d0aea7957")
go_secret = bytes.fromhex("880e2a94110926b20e53e22ae648ae9d")

ser = serial.Serial()
running = False;
storedsl = ''
       
def test_serial_port(portsel):
    ser = serial.Serial(port=portsel, baudrate=19200, bytesize=8, parity=serial.PARITY_EVEN, timeout=1, stopbits=serial.STOPBITS_TWO)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    teststr = "The quick brown fox jumps over the lazy dog. 1234567890\n".encode('utf-8')
    ser.write(teststr)
    cmpstr = ser.read_until()
    ser.close()
    if teststr != cmpstr:
        return False
    else:
        return True

def startsv():
    global running
    global storedsl
    parser = argparse.ArgumentParser(description='Options to supply µpysweeper')
    parser.add_argument('-p', '--port', help='Serial port', required=True, nargs=1)
    parser.add_argument('-bt', '--battery-type', help='Type of Battery to emulate', choices=['Service', 'Autoboot','Normal', 'Custom'], default='Serivce')
    args, ukn = parser.parse_known_args()
    if args.battery_type == 'Custom':
        if ukn:
            custom_battery_type = ukn[0]
            if custom_battery_type[0] == '0' and custom_battery_type[1].lower() == 'x':
                custom_battery_type = custom_battery_type[2:]
            if len(custom_battery_type) < 8 or len(custom_battery_type) > 8:
                print("\nLooks like you are not sure what to do so we will just be using service mode for the battery type\n")
                custom_battery_type = 'FFFFFFFF'
    hexstr = args.battery_type.lower()
    if hexstr == 'autoboot':
        hexstr = '00000000'
    elif hexstr == 'normal':
        hexstr = '34127856'
    elif hexstr == 'service':
        hexstr = 'FFFFFFFF'
    elif hexstr == 'custom':
        hexstr = custom_battery_type
    else:
        hexstr = 'FFFFFFFF'
    if args.port is not None:
        portsel = args.port[0] #"/dev/ttyUSB0"
        storedsl = portsel
    else:
        stopsv()
        return
    if running == True: return

        
    serialn = bytearray(4)
    serialn = bytearray.fromhex(hexstr)
    serialn[0::2], serialn[1::2] = serialn[1::2], serialn[0::2]
    running = True
    # spastic code
    # Spastic code 2: test if port is valid, close it, run emulation loop
    if not test_serial_port(portsel):
        print("No port echo detected. Double check your assembly.")
        stopsv()
        return
    t = threading.Thread(target=emuloop, args=(portsel, serialn))
    t.start()

def stopsv():
    global running
    running = False
    ser.close()

def updatecom():
    portlist = list()
    for port in serial.tools.list_ports.comports():
        portlist.append(port.device)
    if len(portlist) > 0:
        portsel = portlist[0]

def openport(pname):
    try:
        global ser
        ser = serial.Serial(port=pname, baudrate=19200, bytesize=8, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_TWO)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        return 0
    except serial.SerialException:
        print("Port " + pname + " is busy, not present or you don't have permissions to use it.")
        return 1
    except Exception as e:
        print("An exception occurred during port opening: " + repr(e))
        return 1

def readpacket(key):
    mesg = bytearray()
    hello = ser.read(1) # 1
    if hello.hex() == key:
        len = ser.read(1) # 2
        opcode = ser.read(1) # 3
        if len.hex() != "02":
            msglen = (int.from_bytes(len, byteorder='little', signed=False) - 2)
            while (ser.in_waiting < (msglen + 1)):
                time.sleep(0.001)
            mesg = bytearray(msglen)
            mesg = ser.read(msglen)
            csum = ser.read(1)
            print(hello.hex().upper() + ' ' + len.hex().upper() + ' ' + opcode.hex().upper() + ' ' + mesg.hex().upper() + ' ' + csum.hex().upper())
        else:
            csum = ser.read(1)
            print(hello.hex().upper() + ' ' + len.hex().upper() + ' ' + opcode.hex().upper() + ' ' + csum.hex().upper())
        return (hello, len, opcode, mesg, csum)


def writewithchecksum(header, mesg):
    ser.write(bytes.fromhex(header))
    ser.write(mesg)
    ser.write(checksum(header + mesg.hex()))

def emuloop(pname, sn):
    if openport(pname) == 1: return
    challenge1b = bytearray()
    print("Service Started.")
    print("Using serial " + sn.hex().upper())
    try:
        while ser.is_open and running:
            time.sleep(0.001)
            if ser.in_waiting >= 4: # a packet is no less than 4 bytes long
                packet = readpacket("5a")
                if packet:
                    if packet[0].hex() == "5a":
                        if packet[2].hex() == "01":
                            ser.write(bytes.fromhex("a5050610c30676"))  # battery capacity 
                        elif packet[2].hex() == "0c":
                            writewithchecksum("a50606", sn) # battery sn 
                        elif packet[2].hex() == "80":
                            screq = packet[3]
                            version = screq[0]
                            if version not in keystore:
                                response1 = bytes.fromhex("ffffffffffffffff")
                            else:
                                req = screq[1:]
                                data=MixChallenge1(version,req)
                                challenge1a=AES.new(bytes.fromhex(keystore[version]), AES.MODE_ECB).encrypt(bytes(MatrixSwap(data)))
                                second = bytearray(0x10)
                                second[:] = challenge1a[:]
                                challenge1b=MatrixSwap(AES.new(bytes.fromhex(keystore[version]), AES.MODE_ECB).encrypt(bytes((second))))
                                #challenge1b = bytearray.fromhex('AAAAAAAAAAAAAAAA')
                                response1 = bytes(challenge1a[0:8]) + bytes(challenge1b[0:8])
                            writewithchecksum("a51206", response1)
                        elif packet[2].hex() == "81":
                            data2=MixChallenge2(version,challenge1b[0:8])
                            challenge2=AES.new(bytes.fromhex(keystore[version]), AES.MODE_ECB).encrypt(bytes(MatrixSwap(data2)))
                            response2=(AES.new(bytes.fromhex(keystore[version]), AES.MODE_ECB).encrypt(challenge2))
                            writewithchecksum("a51206", response2)
                            if version in (0xEB, 0xB3):
                                ser.write(bytes.fromhex("5a0201a2"))
                        elif packet[2].hex() == "90":
                            screq=packet[3]
                            payload=AES.new(go_key1, AES.MODE_CBC, bytearray(0x10)).decrypt(screq[0x8:0x28])
                            print('Decrypted result: ' + payload.hex().upper())
                            payload91 = payload[8:0x10] + payload[0:8] + bytearray(0x10)
                            if payload[0x10:0x20] == go_secret:
                                print("Go Handshake Request is valid")
                            else:
                                print("Invalid request from Syscon")
                                return
                            resp2 = AES.new(go_key2, AES.MODE_CBC, bytearray(0x10)).decrypt(payload91)
                            writewithchecksum("a52A062001000082828282", resp2)
                        elif packet[2].hex() == "03":
                            ser.write(bytes.fromhex("a5040636100a"))
                        elif packet[2].hex() == "07":
                            ser.write(bytes.fromhex("a50406080741"))
                        elif packet[2].hex() == "0b":
                            ser.write(bytes.fromhex("a504060f0041"))
                        elif packet[2].hex() == "09":
                            ser.write(bytes.fromhex("a5040601044b"))
                        elif packet[2].hex() == "02":
                            ser.write(bytes.fromhex("a503061b36"))
                        elif packet[2].hex() == "04":
                            ser.write(bytes.fromhex("a504066810d8"))
                        elif packet[2].hex() == "16":
                            ser.write(bytes.fromhex("a51306536f6e79456e65726779446576696365736b"))
                        elif packet[2].hex() == "0d":
                            ser.write(bytes.fromhex("a507069d1010281454"))
                        elif packet[2].hex() == "08":
                            ser.write(bytes.fromhex("a50406e2046a"))
             
                    readpacket("a5")
        
    except serial.SerialException:
        if running:
            print("Port disconnected. Retrying in 1 second.")
            time.sleep(1)
            updatecom()
            emuloop(pname, sn)
        else:
            print("Service stopped, COM port closed.")
            return
    
    except OSError:
        if running:
            print("Port disconnected. Retrying in 2 seconds.")
            time.sleep(2)
            updatecom()
            try:
                newname = '/dev/' + os.path.basename(os.readlink(storedsl))
                emuloop(newname, sn)
            except:
                stopsv()
        else:
            print("Service stopped, COM port closed.")
            return

    except Exception as e:
        print("An exception occurred in IO loop: " + str(e))
        print("Service stopped, COM port closed.")
        ser.close()
        return

def checksum(packet):
    bp = bytearray.fromhex(packet)
    Sum = sum(bp)
    sh = hex(Sum)
    temp = bytes.fromhex(sh[len(sh)-2:len(sh)])
    return (255 - int.from_bytes(temp, byteorder='little', signed=False)).to_bytes(1, byteorder="little", signed=False)

#PSP v4 Syscon Handshake Calculator by Proxima (R)
def MixChallenge1(version, challenge):
    data = [ 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
    secret1=bytes.fromhex(challenge1_secret[version])
    data[0] =secret1[0]
    data[4] =secret1[1]
    data[8] =secret1[2]
    data[0xC] =secret1[3]
    data[1] =secret1[4]
    data[5] =secret1[5]
    data[9] =secret1[6]
    data[0xD] =secret1[7]
    data[2] = challenge[0]
    data[6] = challenge[1]
    data[0xA] = challenge[2]
    data[0xE] = challenge[3]
    data[3] = challenge[4]
    data[7] = challenge[5]
    data[0xB] = challenge[6]
    data[0xF] = challenge[7]
    return data


def MixChallenge2(version, challenge):
    data = [ 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
    secret2=bytes.fromhex(challenge2_secret[version])
    data[0] =challenge[0]
    data[4] =challenge[1]
    data[8] =challenge[2]
    data[0xC] =challenge[3]
    data[1] =challenge[4]
    data[5] =challenge[5]
    data[9] =challenge[6]
    data[0xD] =challenge[7]
    data[2] = secret2[0]
    data[6] = secret2[1]
    data[0xA] = secret2[2]
    data[0xE] = secret2[3]
    data[3] = secret2[4]
    data[7] = secret2[5]
    data[0xB] = secret2[6]
    data[0xF] = secret2[7]
    return data

newmap = [
    0x00, 0x04, 0x08, 0x0C, 0x01, 0x05, 0x09, 0x0D, 0x02, 0x06, 0x0A, 0x0E, 0x03, 0x07, 0x0B, 0x0F, 
]

def MatrixSwap(key):
    temp = [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
    for i in range(0,len(key)):
        temp[i] = key[newmap[i]]
    return temp[0:len(key)]

    
if __name__ == '__main__':
    startsv()

