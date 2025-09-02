#!/usr/bin/env python3
"""
Arduino I2C Bridge Command Runner

Reads commands from a text file and sends them line by line to the Arduino I2C bridge.
Lines starting with # are treated as comments and ignored.
Text after # on any line is treated as an inline comment and stripped.
"""

import serial
import time
import sys
import argparse
import logging
from datetime import datetime


def run_command_file(port, baudrate, command_file):
    """
    Execute commands from file on Arduino I2C bridge.
    
    Args:
        port (str): Serial port path
        baudrate (int): Serial communication speed
        command_file (str): Path to command file
    """

    try:
        # Connect to Arduino
        ser = serial.Serial(port, baudrate, timeout=2)
        time.sleep(0.25)  # Wait for Arduino to reset
        logging.info(f"Connected to I2C bridge on {port}")
        
        # Read and execute commands
        with open(command_file, 'r') as f:
            line_number = 0
            executed_count = 0
            
            logging.info(f"Starting execution of commands from: {command_file}")
            
            for line in f:
                line_number += 1
                
                # Strip whitespace
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Handle comments - strip everything after #
                if '#' in line:
                    command = line.split('#')[0].strip()
                    comment = line.split('#', 1)[1].strip()
                else:
                    command = line
                    comment = ""

                if comment:
                    logging.debug(f"Line {line_number}: '{command}' # {comment}")
                else:
                    logging.debug(f"Line {line_number}: '{command}'")
                if not command:
                    continue
                
                # Send command to Arduino
                logging.debug(f"Sending command: {command}")
                print(f"---> {command}")
                ser.write(f"{command}\n".encode())
                executed_count += 1
                
                # Read any other response from Arduino
                time.sleep(0.1)
                while ser.in_waiting > 0:
                    response = ser.readline().decode().strip()
                    if response:
                        if response.startswith("[DBG]"):
                            logging.debug(response)
                        else:
                            print(f"<--- {response}")
                

        logging.debug(f"Execution completed: {executed_count} commands from {line_number} lines")
        
    except FileNotFoundError:
        logging.error(f"Command file '{command_file}' not found")
        sys.exit(1)
    except serial.SerialException as e:
        logging.error(f"Serial connection error on {port}: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        ser.close()
        logging.debug("Connection closed")


def main():
    parser = argparse.ArgumentParser(description='Run I2C bridge commands from file')
    parser.add_argument('command_file', help='Path to command file')
    parser.add_argument('-p', '--port', default='/dev/ttyACM0', 
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('-b', '--baudrate', type=int, default=9600,
                       help='Baudrate (default: 9600)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging (Arduino responses)')
    
    args = parser.parse_args()
    
    # Set up root logger level based on verbose flag
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    

    run_command_file(args.port, args.baudrate, args.command_file)


if __name__ == "__main__":
    main()
