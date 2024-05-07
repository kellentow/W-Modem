# WModem USB Data Transfer Protocol Documentation

## 1. Overview

The WModem USB Data Transfer Protocol defines a basic method for emulating a modem-like data transfer interface over USB. This protocol enables simple and reliable data exchange between a USB device (emulating a modem) and a host computer.

## 2. Protocol Description

### 2.1 Data Format

Data is transmitted in a binary format. Each message consists of a header followed by a payload.

### 2.2 Message Structure

Each message follows this structure:

- **Header**:
  - **Header Byte**: Indicates the start of the header (`0x8E`)
  - **Message Type**: Specifies the type of message (e.g., `0x80` for data message).
  - **Payload Length**: Length of the payload in bytes (1 byte).

- **Payload**: Actual data to be transmitted.
    - **Payload Byte**: Indicates the start of the payload (`0x8D`)
    - **Payload Data**: Actual data to be transmitted.
    - **Checksum Byte**: The checksum of the payload. (Note: this is calculating the sum of all bytes in the payload, including the checksum byte.)
    - **End Byte**: Indicates the end of the payload (`0x8F`)

### 2.3 Supported Commands

| **Command** | **Description** | **Byte Code** |
|---|---|---|
| **Data Message** | Used for transmitting data (from device to host) resembling "received" data from the modem. | `0x80` |
| **DtD Settings Agreement** | Agreeing on settings so that smooth data transfer can occur | `0x81` |
| **Saved for more data types**| Saved for future use | `0x82 - 0x85` |
| **Acknowledgement** | Acknowledges receipt of a message. | `0x86` |
| **NAK** | Not Acknowledged. Indicates that the message was not received. | `0x87` |
| **Abort** | Aborts the current transmission. | `0x88` |
| **Busy** | Busy. Indicates that the modem is busy. | `0x89` |
| **Error** | Indicates that an error has occurred. | `0x8A` |
| **Ignore** | Ignores the next Command code (Allows for extended alphabets to not interfere with the transfer protocol) | `0x8B` |
| **Search Ping** | Used to search for a device. | `0x8C` |
| **Start Of Payload** | Indicates the start of the payload. | `0x8D` |
| **Header**| Indicates the start of the header. | `0x8E` |
| **End Of Payload** | Indicates the end of the payload. | `0x8F` |
| **Saved for more commands**| Saved for future use | `0x90 - 0xBF` |

## 3. Searching for Devices

### 3.1 Sending search ping

The host sends a search command to all curently connected devices and the client should send a ACK message.

## 4. USB Configuration

### 4.1 USB Device Class

The USB device class used is Vendor-Specific (0xFF), emulating a modem-like interface.

### 4.2 Endpoints

- **Endpoint 1 (IN)**: Used for sending data (from device to host) resembling "received" data from the modem.
  - **Type**: Bulk endpoint.
  - **Max Packet Size**: 64 bytes.

- **Endpoint 2 (OUT)**: Used for receiving data (from host to device) resembling "transmitted" data to the modem.
  - **Type**: Bulk endpoint.
  - **Max Packet Size**: 64 bytes.

## 5. Protocol Implementation

### 5.1 Device Initialization

1. Configure USB peripheral.
2. Implement endpoint handlers for data transmission/reception.

### 5.2 Message Handling

1. Parse incoming messages based on the defined message structure.
2. Process received data based on message type.

### 5.3 Message Format

- **Data Message**:
  - **Header**: `0xAA 0x01 <Payload Length>`
  - **Payload**: Variable-length data bytes.

### 5.4 Error Handling

Error handling mechanisms are crucial for ensuring the reliability and robustness of the protocol. The following strategies and implementations are employed:

#### 5.4.1 Timeout Mechanism

A timeout mechanism is implemented to handle situations where expected data is not received within a specified timeframe.

**Implementation**:
- Maintain a timer to track elapsed time while waiting for data.
- If the timeout period is exceeded before receiving expected data, trigger a timeout error.

#### 5.4.2 Checksum Verification

To ensure data integrity, a checksum can be calculated and transmitted alongside each message. The receiver verifies the checksum to detect transmission errors.

**Implementation**:
- Include a checksum (e.g., CRC-16) in the message header or footer.
- Calculate the checksum over the message payload and compare it with the received checksum.
- If the checksums do not match, consider the message corrupted and request retransmission.

#### 5.4.3 NAK (Negative Acknowledgment) and Retransmission

When a receiver detects an error in a received message, it sends a NAK signal (negative acknowledgment) to the sender, indicating that the message was received incorrectly.

**Implementation**:
- Define a NAK response to indicate unsuccessful message reception.
- Upon receiving a NAK, the sender can retransmit the message or take appropriate corrective actions.

#### 5.4.4 Flow Control

Implement flow control mechanisms to manage data flow and prevent buffer overflow or underflow conditions.

**Implementation**:
- Use buffer management techniques to control the amount of data transmitted and received.
- Implement protocols such as XON/XOFF or hardware-based flow control (e.g., RTS/CTS) to regulate data flow between sender and receiver.

#### 5.4.5 Error Reporting and Recovery

Provide mechanisms for reporting errors and recovering from error states to maintain communication integrity.

**Implementation**:
- Define error codes and error handling procedures in the protocol specification.
- Implement error recovery strategies (e.g., retransmission, reset) based on specific error conditions encountered during communication.

#### 5.4.6 State Management

Maintain clear state management to handle transitions between communication states (e.g., idle, transmitting, receiving) and ensure proper error recovery based on the current state.

**Implementation**:
- Define a finite state machine (FSM) to manage communication states and transitions.
- Implement error recovery routines within each state to handle unexpected events and maintain protocol stability.

### 5.5 Example Error Scenarios

Provide examples of common error scenarios encountered during data transmission and demonstrate how error handling mechanisms are utilized to recover from these situations.

**Examples**:
1. Timeout error due to data not being received within a specified duration.
2. Checksum mismatch indicating data corruption.
3. NAK response triggering message retransmission.

## 6. Example Usage

### 6.1 Sending Data (Device to Host)

1. Construct a data message resembling "received" data from the modem.
2. Send the message via Endpoint 1.

### 6.2 Receiving Data (Host to Device)

1. Poll Endpoint 2 for incoming data resembling "transmitted" data to the modem.
2. Parse and process received messages.

## 7. Dependencies

- **Hardware**: USB-capable microcontroller or USB device.
- **Firmware**: USB stack/library supporting bulk data transfer.
- **Host Application**: Software on the host for sending/receiving data.

## 8. Conclusion

This documentation provides a guideline for implementing and using the WModem USB Data Transfer Protocol for emulating a modem-like data transfer interface over USB. Refer to this documentation for protocol details and integration instructions.
