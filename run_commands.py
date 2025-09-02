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
import re
from datetime import datetime


class I2CCommandRunner:
    def __init__(self, port, baudrate, command_file):
        self.port = port
        self.baudrate = baudrate
        self.command_file = command_file
        self.ser = None
        self.last_response = ""
        self.line_number = 0
        self.executed_count = 0
        self.variables = {}

    def connect(self):
        """Connect to Arduino via serial port."""
        self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
        time.sleep(0.25)  # Wait for Arduino to reset
        logging.info(f"Connected to I2C bridge on {self.port}")

    def disconnect(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.debug("Connection closed")

    def parse_line(self, line):
        """Parse command line and extract command and comment."""
        line = line.strip()
        
        if not line:
            return None, None
        
        if '#' in line:
            command = line.split('#')[0].strip()
            comment = line.split('#', 1)[1].strip()
        else:
            command = line
            comment = ""
        
        return command, comment

    def handle_variable_assignment(self, command):
        """Handle variable assignment (VAR=VALUE)."""
        if '=' not in command:
            return False
        
        var_name, var_value = command.split('=', 1)
        var_name = var_name.strip()
        var_value = var_value.strip()
        
        # Remove quotes if present
        if var_value.startswith('"') and var_value.endswith('"'):
            var_value = var_value[1:-1]
        
        self.variables[var_name] = var_value
        logging.debug(f"Variable set: {var_name} = {var_value}")
        return True

    def substitute_variables(self, command):
        """Replace variable names with their values in command."""
        for var_name, var_value in self.variables.items():
            command = command.replace(var_name, var_value)
        return command

    def handle_expect_command(self, command):
        """Handle EXPECT command for response validation."""
        expected = command[7:].strip()
        expected = expected.strip('"')
        
        # Substitute variables in expected pattern
        expected = self.substitute_variables(expected)

        try:
            if re.match(expected, self.last_response):
                print(f"---> EXPECT \"{expected}\" ✓")
            else:
                logging.error(f"EXPECT failed on line {self.line_number}")
                logging.error(f"Expected pattern: \"{expected}\"")
                logging.error(f"Received: \"{self.last_response}\"")
                sys.exit(1)
        except re.error as e:
            logging.error(f"EXPECT failed on line {self.line_number}: Invalid regex pattern")
            logging.error(f"Pattern: \"{expected}\"")
            logging.error(f"Regex error: {e}")
            sys.exit(1)

    def send_command(self, command):
        """Send command to Arduino and read response."""
        # Substitute variables in command
        original_command = command
        command = self.substitute_variables(command)
        
        if original_command != command:
            logging.debug(f"After variable substitution: {original_command} -> {command}")
        
        logging.debug(f"Sending command: {command}")
        print(f"---> {command}")
        self.ser.write(f"{command}\n".encode())
        self.executed_count += 1
        
        # Read response from Arduino
        self.last_response = ""
        time.sleep(0.1)
        while self.ser.in_waiting > 0:
            response = self.ser.readline().decode().strip()
            if response:
                if response.startswith("[DBG]"):
                    logging.debug(response)
                else:
                    print(f"<--- {response}")
                    self.last_response = response

    def execute_commands(self):
        """Execute all commands from the command file."""
        try:
            self.connect()
            logging.info(f"Starting execution of commands from: {self.command_file}")
            
            with open(self.command_file, 'r') as f:
                for line in f:
                    self.line_number += 1
                    
                    command, comment = self.parse_line(line)
                    
                    if command is None:
                        continue
                    
                    if comment:
                        logging.debug(f"Line {self.line_number}: '{command}' # {comment}")
                    else:
                        logging.debug(f"Line {self.line_number}: '{command}'")
                    
                    if not command:
                        continue
                    
                    # Handle variable assignment
                    if self.handle_variable_assignment(command):
                        continue
                    
                    # Handle EXPECT command
                    if command.upper().startswith("EXPECT "):
                        self.handle_expect_command(command)
                        continue
                    
                    # Send regular command
                    self.send_command(command)

            logging.debug(f"Execution completed: {self.executed_count} commands from {self.line_number} lines")
            
        except FileNotFoundError:
            logging.error(f"Command file '{self.command_file}' not found")
            sys.exit(1)
        except serial.SerialException as e:
            logging.error(f"Serial connection error on {self.port}: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            sys.exit(1)
        finally:
            self.disconnect()


def run_command_file(port, baudrate, command_file):
    """Execute commands from file on Arduino I2C bridge."""
    runner = I2CCommandRunner(port, baudrate, command_file)
    runner.execute_commands()


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
